"""Categories API endpoint — returns spending breakdown by category."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.statement import Statement
from app.models.transaction import Transaction
from app.schemas.metrics import CategoryBreakdown

router = APIRouter()


@router.get("/categories", response_model=list[CategoryBreakdown])
async def get_categories(
    statement_id: str = Query(..., description="Statement ID"),
    db: Session = Depends(get_db),
):
    """Get spending breakdown by category for a processed statement."""
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    if statement.status != "completed":
        raise HTTPException(status_code=422, detail=f"Statement status: {statement.status}")

    # Calculate category totals (only for debits/spending)
    results = (
        db.query(
            Transaction.category,
            func.count(Transaction.id).label("count"),
            func.sum(Transaction.amount).label("total"),
        )
        .filter(Transaction.statement_id == statement_id)
        .group_by(Transaction.category)
        .all()
    )

    # Calculate total spend for percentages (only debits)
    total_spend = sum(abs(r.total) for r in results if r.total and r.total < 0)

    # Only include spending categories (negative amounts = debits)
    spending_categories = []
    for r in results:
        if r.total and r.total < 0:
            total = abs(r.total)
            percentage = (total / total_spend * 100) if total_spend > 0 else 0
            spending_categories.append(CategoryBreakdown(
                name=r.category,
                total=total,
                count=r.count,
                percentage=round(percentage, 1),
            ))

    # Sort by total (highest first)
    spending_categories.sort(key=lambda c: c.total, reverse=True)

    return spending_categories
