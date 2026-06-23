"""API router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.upload import router as upload_router
from app.api.transactions import router as transactions_router
from app.api.categories import router as categories_router
from app.api.recurring import router as recurring_router
from app.api.metrics import router as metrics_router
from app.api.insights import router as insights_router
from app.api.report import router as report_router

api_router = APIRouter()

api_router.include_router(upload_router, tags=["Upload"])
api_router.include_router(transactions_router, tags=["Transactions"])
api_router.include_router(categories_router, tags=["Categories"])
api_router.include_router(recurring_router, tags=["Recurring"])
api_router.include_router(metrics_router, tags=["Metrics"])
api_router.include_router(insights_router, tags=["Insights"])
api_router.include_router(report_router, tags=["Report"])
