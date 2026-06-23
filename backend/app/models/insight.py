import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Insight(Base):
    __tablename__ = "insights"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    statement_id = Column(String, ForeignKey("statements.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity = Column(String, default="info")  # info, warning, critical
    category = Column(String, nullable=True)
    amount_referenced = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    statement = relationship("Statement", back_populates="insights")
