from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class StatementUploadResponse(BaseModel):
    statement_id: str
    status: str
    transaction_count: int
    processing_error: Optional[str] = None


class StatementDetail(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_date: datetime
    transaction_count: int
    status: str
    processing_error: Optional[str] = None
