from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InsightResponse(BaseModel):
    id: str
    title: str
    description: str
    severity: str  # info, warning, critical
    category: Optional[str] = None
    amount_referenced: Optional[float] = None
    created_at: datetime


class InsightsListResponse(BaseModel):
    insights: list[InsightResponse]
