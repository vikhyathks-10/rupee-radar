"""RupeeRadar — FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create directories and database tables."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(os.path.dirname(settings.db_path), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="RupeeRadar",
    description="AI-powered personal finance assistant API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://rupee-radar-sigma.vercel.app",
        "https://rupee-radar-nk9bdlfqe-vikki5.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API endpoints
app.include_router(api_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "RupeeRadar Backend",
        "version": "0.1.0",
    }