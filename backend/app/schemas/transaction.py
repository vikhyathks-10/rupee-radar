from datetime import date
from typing import Optional

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: str
    date: date
    description: str
    original_description: str
    amount: float
    category: str
    is_recurring: bool
    confidence: Optional[float] = None


class TransactionsListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
