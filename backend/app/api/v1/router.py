from fastapi import APIRouter

from app.api.v1.endpoints import health, missions, context, report, synthetic, system


api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(system.router, tags=["system"])
api_router.include_router(context.router, tags=["context"])
api_router.include_router(missions.router, tags=["missions"])
api_router.include_router(synthetic.router, tags=["synthetic"])
api_router.include_router(report.router, tags=["report"])
