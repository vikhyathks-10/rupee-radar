"""Metrics API endpoint — returns computed financial metrics."""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.statement import Statement
from app.schemas.metrics import MetricsResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    statement_id: str = Query(..., description="Statement ID"),
    db: Session = Depends(get_db),
):
    """Get computed financial metrics for a processed statement."""
    statement = db.query(Statement).filter(Statement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    if statement.status != "completed":
        raise HTTPException(status_code=422, detail=f"Statement status: {statement.status}")

    # Load metrics from stored JSON
    if not statement.metrics_json:
        raise HTTPException(status_code=404, detail="Metrics not computed for this statement")

    try:
        metrics = json.loads(statement.metrics_json)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse metrics JSON for statement {statement_id}")
        raise HTTPException(status_code=500, detail="Failed to load metrics data")

    return MetricsResponse(**metrics)
