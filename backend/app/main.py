from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.asyncio import Redis

from app.api.v1.router import api_router
from app.http_envelope import err
from app.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="jarvis-mission-control", version=settings.app_version)

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request.state.request_id = f"req_{uuid.uuid4().hex}"
        response = await call_next(request)
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        payload, status = err(
            request,
            code="INVALID_PARAMS",
            message="Invalid request parameters",
            status_code=400,
            details={"errors": exc.errors()},
        )
        return JSONResponse(payload, status_code=status)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        payload, status = err(
            request,
            code="HTTP_ERROR",
            message=str(exc.detail),
            status_code=exc.status_code,
        )
        return JSONResponse(payload, status_code=status)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        payload, status = err(
            request,
            code="INTERNAL",
            message="Unexpected server error",
            status_code=500,
        )
        return JSONResponse(payload, status_code=status)

    @app.on_event("startup")
    async def _startup():
        app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    @app.on_event("shutdown")
    async def _shutdown():
        redis: Redis = app.state.redis
        await redis.aclose()

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
