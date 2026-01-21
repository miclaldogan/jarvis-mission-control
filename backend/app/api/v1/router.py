from fastapi import APIRouter

from app.api.v1.endpoints import context, health, report, synthetic

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(context.router, tags=["context"])
api_router.include_router(synthetic.router, tags=["synthetic"])
api_router.include_router(report.router, tags=["report"])
