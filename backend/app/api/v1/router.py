from fastapi import APIRouter

from app.api.v1.endpoints import context, health, missions, report, simulation, synthetic
from app.api.v1.endpoints import system
from app.api.v1.endpoints import persistence
from app.api.v1.endpoints import harmonics

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(context.router, tags=["context"])
# persistence router has /missions/today - must come before missions router with /{mission_id}
api_router.include_router(persistence.router, tags=["persistence"])
api_router.include_router(missions.router, tags=["missions"])
api_router.include_router(simulation.router, tags=["simulation"])
api_router.include_router(synthetic.router, tags=["synthetic"])
api_router.include_router(report.router, tags=["report"])

api_router.include_router(system.router, tags=['system'])
api_router.include_router(harmonics.router, tags=['harmonics'])
