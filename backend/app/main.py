"""RupeeRadar — FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.api.router import api_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup tasks."""
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

# Allowed frontend origins
origins = [
    "http://localhost:5173",
    "https://rupee-radar-sigma.vercel.app",
    "https://rupee-radar-c41yubqux-vikki5.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "RupeeRadar Backend is Running 🚀"
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "RupeeRadar Backend",
        "version": "0.1.0",
    }