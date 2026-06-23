import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Statement(Base):
    __tablename__ = "statements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # "csv" or "pdf"
    upload_date = Column(DateTime, default=datetime.utcnow)
    transaction_count = Column(Integer, default=0)
    status = Column(String, default="processing")  # processing, completed, failed
    processing_error = Column(String, nullable=True)
    metrics_json = Column(Text, nullable=True)  # Stored metrics payload
    recurring_json = Column(Text, nullable=True)  # Stored recurring items payload

    transactions = relationship("Transaction", back_populates="statement", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="statement", cascade="all, delete-orphan")
