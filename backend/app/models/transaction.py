import uuid
from datetime import date

from sqlalchemy import Column, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    statement_id = Column(String, ForeignKey("statements.id"), nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    original_description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, default="Other")
    is_recurring = Column(Boolean, default=False)
    recurring_group_id = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)

    statement = relationship("Statement", back_populates="transactions")
