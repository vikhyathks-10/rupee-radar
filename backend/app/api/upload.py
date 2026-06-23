"""Upload API endpoint — accepts CSV/PDF files and processes them."""

import os
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.statement import Statement
from app.schemas.statement import StatementUploadResponse
from app.services.processing_pipeline import ProcessingPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

pipeline = ProcessingPipeline(use_ai=True)

ALLOWED_EXTENSIONS = {".csv", ".pdf"}
MAX_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024


@router.post("/upload", response_model=StatementUploadResponse)
async def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process a bank statement (CSV or PDF)."""
    # Validate file extension
    filename = file.filename or "unknown"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Supported formats: CSV, PDF",
        )

    # Read and validate file size
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
        )

    # Save file to disk
    file_type = ext.lstrip(".")  # "csv" or "pdf"
    save_path = os.path.join(settings.upload_dir, filename)

    # Avoid overwriting: add unique suffix if file exists
    if os.path.exists(save_path):
        base, ext = os.path.splitext(save_path)
        save_path = f"{base}_{os.urandom(4).hex()}{ext}"

    with open(save_path, "wb") as f:
        f.write(content)

    # Process the statement
    statement = await pipeline.process(db, save_path, filename, file_type)

    # Delete the uploaded file after parsing (privacy)
    try:
        os.remove(save_path)
    except OSError:
        logger.warning(f"Could not delete uploaded file: {save_path}")

    if statement.status == "failed":
        # Empty statements get 422 with clear error message
        # Corrupted/unreadable files get 422 with parsing error details
        error_msg = statement.processing_error or "Processing failed"
        raise HTTPException(
            status_code=422,
            detail=error_msg,
        )

    return StatementUploadResponse(
        statement_id=statement.id,
        status=statement.status,
        transaction_count=statement.transaction_count,
        processing_error=statement.processing_error,
    )
