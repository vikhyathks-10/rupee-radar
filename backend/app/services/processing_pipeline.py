"""Processing pipeline — orchestrates parse → clean → categorize → detect_recurring → compute_metrics → generate_insights → save."""

import json
import logging
import uuid

from sqlalchemy.orm import Session

from app.models.statement import Statement
from app.models.transaction import Transaction
from app.models.insight import Insight
from app.services.parser import parse_statement
from app.services.cleaner import CleanerService
from app.services.categorizer import CategorizerService
from app.services.recurring_detector import RecurringDetector
from app.services.metrics_calculator import MetricsCalculator
from app.services.insight_generator import InsightGenerator
from app.services.report_generator import ReportGenerator
from app.ai.categorize_chain import CategorizeChain

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    """Orchestrates the full statement processing pipeline."""

    def __init__(self, use_ai: bool = True):
        self.parser = parse_statement
        self.cleaner = CleanerService()
        self.categorizer = CategorizerService(
            ai_chain=CategorizeChain() if use_ai else None,
        )
        self.recurring_detector = RecurringDetector()
        self.metrics_calculator = MetricsCalculator()
        self.insight_generator = InsightGenerator(use_ai=use_ai)
        self.report_generator = ReportGenerator()

    async def process(self, db: Session, file_path: str, filename: str, file_type: str) -> Statement:
        """Run the full pipeline on an uploaded statement file.

        1. Parse → extract raw transactions
        2. Clean → normalize dates, amounts, descriptions
        3. Categorize → rule-based + AI
        4. Detect Recurring → flag periodic payments
        5. Compute Metrics → income, spend, savings, breakdown
        6. Generate Insights → AI-powered financial insights
        7. Save → store all results in database

        Returns the Statement record with status updated.
        """
        # Create statement record
        statement = Statement(
            id=str(uuid.uuid4()),
            filename=filename,
            file_type=file_type,
            status="processing",
        )
        db.add(statement)
        db.commit()
        db.refresh(statement)

        try:
            # Step 1: Parse
            logger.info(f"[{statement.id}] Step 1/7: Parsing statement: {filename}")
            try:
                raw_txns = self.parser(file_path)
            except ValueError as parse_err:
                # Parser raised a descriptive error (corrupted file, bad format)
                statement.status = "failed"
                statement.processing_error = str(parse_err)
                db.commit()
                return statement

            if not raw_txns:
                statement.status = "failed"
                statement.processing_error = "No transactions found in the uploaded file. The file may be empty or have unrecognized column headers."
                db.commit()
                return statement

            # Step 2: Clean
            logger.info(f"[{statement.id}] Step 2/7: Cleaning {len(raw_txns)} raw transactions")
            cleaned_txns = self.cleaner.clean(raw_txns)
            if not cleaned_txns:
                statement.status = "failed"
                statement.processing_error = "All transactions were invalid, had missing fields, or were duplicates. No usable data remains."
                db.commit()
                return statement

            # Step 3: Categorize
            logger.info(f"[{statement.id}] Step 3/7: Categorizing {len(cleaned_txns)} transactions")
            categorized_txns = self.categorizer.categorize(cleaned_txns)

            # Step 4: Detect Recurring
            logger.info(f"[{statement.id}] Step 4/7: Detecting recurring payments")
            recurring_items = self.recurring_detector.detect(categorized_txns)

            # Step 5: Compute Metrics
            logger.info(f"[{statement.id}] Step 5/7: Computing financial metrics")
            metrics = self.metrics_calculator.compute(categorized_txns)

            # Step 6: Generate Insights
            logger.info(f"[{statement.id}] Step 6/7: Generating AI insights")
            insight_results = self.insight_generator.generate_and_save(
                db=db,
                statement_id=statement.id,
                transactions=categorized_txns,
                metrics=metrics,
                recurring_items=recurring_items,
            )

            # Step 7: Save transactions + recurring flags
            logger.info(f"[{statement.id}] Step 7/7: Saving {len(categorized_txns)} transactions to database")
            for txn_data in categorized_txns:
                transaction = Transaction(
                    id=str(uuid.uuid4()),
                    statement_id=statement.id,
                    date=txn_data["date"],
                    description=txn_data["description"],
                    original_description=txn_data["original_description"],
                    amount=txn_data["amount"],
                    category=txn_data["category"],
                    is_recurring=txn_data.get("is_recurring", False),
                    recurring_group_id=txn_data.get("recurring_group_id"),
                    confidence=txn_data.get("confidence"),
                )
                db.add(transaction)

            # Store metrics and recurring as JSON on the statement for quick retrieval
            # Convert any date objects to strings for JSON serialization
            def _json_serialize(obj):
                if hasattr(obj, 'strftime'):
                    return obj.strftime('%Y-%m-%d')
                raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

            statement.metrics_json = json.dumps(metrics, default=_json_serialize)
            statement.recurring_json = json.dumps(recurring_items, default=_json_serialize)

            # Update statement status
            statement.transaction_count = len(categorized_txns)
            statement.status = "completed"
            db.commit()

            logger.info(f"[{statement.id}] Processing complete: {len(categorized_txns)} transactions, {len(recurring_items)} recurring, {len(insight_results)} insights")

        except Exception as e:
            logger.error(f"[{statement.id}] Processing failed at step: {e}")
            # Rollback any partial DB writes before setting failure status
            db.rollback()
            statement.status = "failed"
            statement.processing_error = f"Processing error: {str(e)}"
            db.commit()

        return statement
