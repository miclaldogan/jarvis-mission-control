from __future__ import annotations

import json
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from redis.asyncio import Redis

from app.api.v1.router import api_router
from app.http_envelope import err
from app.logging_config import setup_structured_logging, get_logger, LogContext
from app.metrics import observe_request
from app.settings import get_settings

# Setup structured logging on module import
setup_structured_logging()

logger = get_logger("jarvis")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    settings = get_settings()

    # Startup
    redis = None
    try:
        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        await redis.ping()
        app.state.redis = redis
        logger.info(f"✅ Redis connected: {settings.redis_url}")
        logger.info(f"📦 Cache TTL: {settings.cache_ttl_seconds} seconds")
    except Exception as exc:
        # Redis is optional: fallback to no-cache mode
        app.state.redis = None
        logger.warning(f"⚠️  Redis unavailable, cache BYPASS mode enabled: {exc}")

    yield

    # Shutdown
    redis = getattr(app.state, "redis", None)
    if redis is not None:
        try:
            await redis.aclose()
        except Exception:
            pass

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="jarvis-mission-control",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-Id", "X-Cache", "X-Cache-Key", "X-Compute-Time-ms"],
    )

    logger = logging.getLogger("jarvis")

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        start = time.perf_counter()

        incoming_request_id = request.headers.get("X-Request-Id")
        request_id = incoming_request_id.strip() if incoming_request_id else ""
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex}"

        request.state.request_id = request_id

        # Log incoming request
        with LogContext(request_id=request_id, endpoint=request.url.path, method=request.method):
            logger.info(f"Request started: {request.method} {request.url.path}")

        try:
            response = await call_next(request)
        except RequestValidationError as exc:
            with LogContext(request_id=request_id, endpoint=request.url.path, method=request.method, error="validation_error"):
                logger.warning(f"Request validation failed: {exc.errors()}")
            payload, status = err(
                request,
                code="INVALID_PARAMS",
                message="Invalid request parameters",
                status_code=400,
                details={"errors": exc.errors()},
            )
            response = JSONResponse(payload, status_code=status)
        except HTTPException as exc:
            with LogContext(request_id=request_id, endpoint=request.url.path, method=request.method, error="http_error", status_code=exc.status_code):
                logger.warning(f"HTTP exception: {exc.detail}")
            payload, status = err(
                request,
                code="HTTP_ERROR",
                message=str(exc.detail),
                status_code=exc.status_code,
            )
            response = JSONResponse(payload, status_code=status)
        except Exception as e:
            with LogContext(request_id=request_id, endpoint=request.url.path, method=request.method, error=str(e)):
                logger.exception(f"Unhandled exception: {e}")
            payload, status = err(
                request,
                code="INTERNAL",
                message="Unexpected server error",
                status_code=500, 
            )
            response = JSONResponse(payload, status_code=status)

        duration_s = time.perf_counter() - start
        duration_ms = int(duration_s * 1000)
        response.headers["X-Request-Id"] = request_id

        # Basic security headers (baseline)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )

        # Log response with context
        with LogContext(
            request_id=request_id,
            endpoint=request.url.path,
            method=request.method,
            status_code=getattr(response, "status_code", None),
            duration_ms=duration_ms
        ):
            logger.info(f"Request completed: {request.method} {request.url.path} [{getattr(response, 'status_code', None)}] in {duration_ms}ms")

        observe_request(
            method=request.method,
            path=request.url.path,
            status=int(getattr(response, "status_code", 0) or 0),
            duration_seconds=duration_s,
        )

        return response

    @app.get("/metrics")
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # NOTE: We intentionally handle exceptions in middleware so that:
    # - every response includes X-Request-Id
    # - error responses keep the standard envelope

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
