from __future__ import annotations

import json
import logging
import time
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

    logger = logging.getLogger("jarvis")

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        start = time.perf_counter()

        incoming_request_id = request.headers.get("X-Request-Id")
        request_id = incoming_request_id.strip() if incoming_request_id else ""
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex}"

        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except RequestValidationError as exc:
            payload, status = err(
                request,
                code="INVALID_PARAMS",
                message="Invalid request parameters",
                status_code=400,
                details={"errors": exc.errors()},
            )
            response = JSONResponse(payload, status_code=status)
        except HTTPException as exc:
            payload, status = err(
                request,
                code="HTTP_ERROR",
                message=str(exc.detail),
                status_code=exc.status_code,
            )
            response = JSONResponse(payload, status_code=status)
        except Exception:
            payload, status = err(
                request,
                code="INTERNAL",
                message="Unexpected server error",
                status_code=500,
            )
            response = JSONResponse(payload, status_code=status)

        duration_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Request-Id"] = request_id

        logger.info(
            json.dumps(
                {
                    "event": "request",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": getattr(response, "status_code", None),
                    "duration_ms": duration_ms,
                }
            )
        )

        return response

    # NOTE: We intentionally handle exceptions in middleware so that:
    # - every response includes X-Request-Id
    # - error responses keep the standard envelope

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
