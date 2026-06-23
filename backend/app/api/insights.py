"""Insights API endpoint — returns AI-generated financial insights."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.statement import Statement
from app.models.insight import Insight
from app.schemas.insight import InsightResponse, InsightsListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/insights", response_model=InsightsListResponse)
async def get_insights(
    statement_id: str = Query(..., description="Statement ID"),
    db: Session = Depends(get_db),
):
    """Get AI-generated insights for a processed statement."""
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    if statement.status != "completed":
        raise HTTPException(status_code=422, detail=f"Statement status: {statement.status}")

    # Load insights from database
    insights = db.query(Insight).filter(Insight.statement_id == statement_id).all()

    return InsightsListResponse(
        insights=[
            InsightResponse(
                id=i.id,
                title=i.title,
                description=i.description,
                severity=i.severity,
                category=i.category,
                amount_referenced=i.amount_referenced,
                created_at=i.created_at,
            )
            for i in insights
        ]
    )
