"""Recurring payments API endpoint — returns detected recurring payments."""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.statement import Statement
from app.schemas.metrics import RecurringItem

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/recurring", response_model=list[RecurringItem])
async def get_recurring(
    statement_id: str = Query(..., description="Statement ID"),
    db: Session = Depends(get_db),
):
    """Get detected recurring payments for a processed statement."""
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    if statement.status != "completed":
        raise HTTPException(status_code=422, detail=f"Statement status: {statement.status}")

    # Load recurring items from stored JSON
    if not statement.recurring_json:
        return []

    try:
        recurring_data = json.loads(statement.recurring_json)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse recurring JSON for statement {statement_id}")
        return []

    # Convert next_expected_date to string if it's a date object
    items = []
    for item in recurring_data:
        next_date = item.get("next_expected_date")
        if next_date and hasattr(next_date, "strftime"):
            next_date = next_date.strftime("%Y-%m-%d")
        elif next_date:
            next_date = str(next_date)

        items.append(RecurringItem(
            merchant=item["merchant"],
            amount=item["amount"],
            frequency=item["frequency"],
            occurrences=item["occurrences"],
            next_expected_date=next_date,
            annual_cost=item["annual_cost"],
            category=item["category"],
        ))

    return items
