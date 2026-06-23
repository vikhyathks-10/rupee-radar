from datetime import date
from typing import Optional

from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    name: str
    total: float
    count: int
    percentage: float


class BiggestTransaction(BaseModel):
    description: str
    amount: float
    date: str


class MonthlyBreakdown(BaseModel):
    month: str
    income: float
    spend: float


class RecurringItem(BaseModel):
    merchant: str
    amount: float
    frequency: str
    occurrences: int
    next_expected_date: Optional[str] = None
    annual_cost: float
    category: str


class MetricsResponse(BaseModel):
    total_income: float
    total_spend: float
    savings: float
    savings_rate: Optional[float] = None
    top_categories: list[CategoryBreakdown]
    biggest_transactions: list[BiggestTransaction]
    monthly_breakdown: list[MonthlyBreakdown]
