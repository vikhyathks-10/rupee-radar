"""Insight generator service — orchestrates AI insight generation and saves to database."""

import logging
import uuid
from typing import Optional

from app.ai.insight_chain import InsightChain
from app.models.insight import Insight

logger = logging.getLogger(__name__)


class InsightGenerator:
    """Generate and store financial insights from categorized transactions and metrics."""

    def __init__(self, use_ai: bool = True):
        self.insight_chain = InsightChain() if use_ai else None

    def generate_and_save(
        self,
        db,
        statement_id: str,
        transactions: list[dict],
        metrics: dict,
        recurring_items: list[dict] = None,
    ) -> list[Insight]:
        """Generate insights and save them to the database.
        
        Falls back to rule-based insights if AI generation fails.
        Returns a list of Insight ORM objects.
        """
        raw_insights = []

        # Try AI insight generation first
        if self.insight_chain:
            try:
                raw_insights = self.insight_chain.generate_insights(metrics, recurring_items)
            except Exception as e:
                logger.error(f"AI insight generation failed for statement {statement_id}: {e}. Using fallback.")
                raw_insights = self._fallback_insights(metrics)
        else:
            raw_insights = self._fallback_insights(metrics)

        # Save to database
        db_insights = []
        for insight_data in raw_insights:
            insight = Insight(
                id=str(uuid.uuid4()),
                statement_id=statement_id,
                title=insight_data.get("title", "Financial Observation"),
                description=insight_data.get("description", ""),
                severity=insight_data.get("severity", "info"),
                category=insight_data.get("category"),
                amount_referenced=insight_data.get("amount_referenced"),
            )
            db.add(insight)
            db_insights.append(insight)

        logger.info(f"Generated {len(db_insights)} insights for statement {statement_id}")
        return db_insights

    def _fallback_insights(self, metrics: dict) -> list[dict]:
        """Rule-based fallback insight generation when AI is unavailable or fails."""
        insights = []

        income = metrics.get("total_income", 0)
        spend = metrics.get("total_spend", 0)
        savings = metrics.get("savings", 0)
        savings_rate = metrics.get("savings_rate", 0) or 0

        # Savings rate insight
        if savings_rate >= 20:
            insights.append({
                "title": "Good Savings Rate",
                "description": f"Your savings rate is {savings_rate:.1f}% — above the recommended 20%. You saved Rs.{abs(savings):,.0f} out of Rs.{abs(income):,.0f}.",
                "severity": "info",
                "category": None,
                "amount_referenced": savings,
            })
        elif savings_rate > 0:
            insights.append({
                "title": "Low Savings Rate",
                "description": f"Your savings rate is only {savings_rate:.1f}% — below the recommended 20%. Consider reducing discretionary spending.",
                "severity": "warning",
                "category": None,
                "amount_referenced": savings,
            })

        # Top spending category insight
        top_cats = metrics.get("top_categories", [])
        if top_cats:
            top = top_cats[0]
            cat_pct = top.get("percentage", 0) or 0
            if cat_pct > 30:
                insights.append({
                    "title": f"High {top['name']} Spending",
                    "description": f"{top['name']} accounts for {cat_pct:.1f}% of your total spending (Rs.{abs(top['total']):,.0f}), which exceeds the recommended 30% threshold.",
                    "severity": "warning",
                    "category": top['name'],
                    "amount_referenced": top['total'],
                })

        # Recurring payments insight
        recurring = metrics.get("recurring", [])
        if recurring and income > 0:
            total_recurring = sum(abs(r.get("amount", 0)) for r in recurring)
            recurring_pct = (total_recurring / income) * 100
            if recurring_pct > 40:
                insights.append({
                    "title": "High Recurring Commitments",
                    "description": f"Your recurring payments total Rs.{total_recurring:,.0f}, which is {recurring_pct:.1f}% of your income. This limits your financial flexibility.",
                    "severity": "warning",
                    "category": None,
                    "amount_referenced": total_recurring,
                })
            else:
                insights.append({
                    "title": "Recurring Payments Under Control",
                    "description": f"Your recurring payments total Rs.{total_recurring:,.0f} ({recurring_pct:.1f}% of income), which is manageable.",
                    "severity": "info",
                    "category": None,
                    "amount_referenced": total_recurring,
                })

        # Ensure at least 1 insight
        if not insights:
            insights.append({
                "title": "Financial Summary",
                "description": f"You earned Rs.{abs(income):,.0f} and spent Rs.{abs(spend):,.0f}, saving Rs.{abs(savings):,.0f} ({savings_rate:.1f}%).",
                "severity": "info",
                "category": None,
                "amount_referenced": savings,
            })

        return insights
