"""
CryptoScope AI - Middleware (Phase 25 CORS & Request Tracing)
- Request ID assignment (X-Request-ID)
- Request processing latency tracking
- Safe CORS headers based on canonical settings.CORS_ORIGINS
"""
import time
import uuid
import logging
from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

logger = logging.getLogger("cryptoscope.middleware")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration * 1000:.2f}"
        return response


def setup_middleware(app: FastAPI):
    # 1. Request tracing & context
    app.add_middleware(RequestContextMiddleware)

    # 2. Canonical CORS configuration (Phase 25)
    allowed_origins = list(settings.CORS_ORIGINS)
    if settings.ENVIRONMENT.lower() in ["development", "dev", "local"]:
        dev_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://10.0.2.2:8000"
        ]
        for origin in dev_origins:
            if origin not in allowed_origins:
                allowed_origins.append(origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
