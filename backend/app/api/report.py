"""Report API endpoint — generates and returns a downloadable PDF report."""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.statement import Statement
from app.models.insight import Insight
from app.services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

report_generator = ReportGenerator()


@router.get("/report/pdf")
async def get_report_pdf(
    statement_id: str = Query(..., description="Statement ID"),
    db: Session = Depends(get_db),
):
    """Generate and download a PDF financial summary report."""
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    if statement.status != "completed":
        raise HTTPException(status_code=422, detail=f"Statement status: {statement.status}")

    # Load metrics from stored JSON
    metrics = {}
    if statement.metrics_json:
        try:
            metrics = json.loads(statement.metrics_json)
        except json.JSONDecodeError:
            logger.error("Failed to parse metrics JSON for report")

    # Load recurring items from stored JSON
    recurring_items = []
    if statement.recurring_json:
        try:
            recurring_items = json.loads(statement.recurring_json)
        except json.JSONDecodeError:
            logger.error("Failed to parse recurring JSON for report")

    # Load insights from database
    insights = db.query(Insight).filter(Insight.statement_id == statement_id).all()
    insights_data = [
        {
            "title": i.title,
            "description": i.description,
            "severity": i.severity,
            "category": i.category,
            "amount_referenced": i.amount_referenced,
        }
        for i in insights
    ]

    # Generate PDF
    pdf_bytes = report_generator.generate_pdf(
        statement_id=statement_id,
        filename=statement.filename,
        metrics=metrics,
        recurring_items=recurring_items,
        insights=insights_data,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=rupeeradar_report_{statement_id[:8]}.pdf"
        },
    )
