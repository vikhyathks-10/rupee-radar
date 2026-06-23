"""Transactions API endpoint — returns cleaned and categorized transactions."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.statement import Statement
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionResponse, TransactionsListResponse

router = APIRouter()


@router.get("/transactions", response_model=TransactionsListResponse)
async def get_transactions(
    statement_id: str = Query(..., description="Statement ID to fetch transactions for"),
    category: str = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get cleaned, categorized transactions for a processed statement."""
    # Verify statement exists
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")

    if statement.status == "processing":
        raise HTTPException(status_code=202, detail="Statement is still being processed")
    if statement.status == "failed":
        raise HTTPException(status_code=422, detail=f"Statement processing failed: {statement.processing_error}")

    # Build query
    query = db.query(Transaction).filter(Transaction.statement_id == statement_id)

    # Filter by category if specified
    if category:
        valid_categories = ["Food", "Travel", "Shopping", "Bills", "EMI", "Subscriptions", "Salary", "Rent", "Investments", "Other"]
        if category not in valid_categories:
            raise HTTPException(status_code=400, detail=f"Invalid category '{category}'. Valid: {valid_categories}")
        query = query.filter(Transaction.category == category)

    # Pagination
    total = query.count()
    offset = (page - 1) * limit
    transactions = query.offset(offset).limit(limit).all()

    return TransactionsListResponse(
        transactions=[
            TransactionResponse(
                id=t.id,
                date=t.date,
                description=t.description,
                original_description=t.original_description,
                amount=t.amount,
                category=t.category,
                is_recurring=t.is_recurring,
                confidence=t.confidence,
            )
            for t in transactions
        ],
        total=total,
    )
