"""
CryptoScope AI - Canonical Master Gateway (Phase 3)
Sole production entry point for CryptoScope AI.

Structure:
- Minimalist orchestrator
- Registers lifespan (DB pool, Redis cache, instrument discovery)
- Registers middleware (X-Request-ID, latency, strict CORS)
- Registers centralized exception handlers (Phase 24 standardized error envelope)
- Registers all modular routers under /api/v1 (and /health)
"""
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.api.lifespan import lifespan
from apps.api.middleware import setup_middleware
from apps.api.errors import (
    CryptoScopeApiException,
    api_exception_handler,
    http_exception_handler,
    validation_exception_handler
)
from core.config import settings

# Modular routers
from apps.api.routers import (
    health,
    auth,
    users,
    markets,
    derivatives,
    orderbook,
    orderflow,
    liquidations,
    predictions,
    alerts,
    paper,
    providers
)

logger = logging.getLogger("cryptoscope.api")

# FastAPI App Creation with Lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CryptoScope AI Canonical Quantitative Intelligence & Execution Gateway",
    version="2.4.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 1. Setup Middleware
setup_middleware(app)

# 2. Register Centralized Exception Handlers (Phase 24)
app.add_exception_handler(CryptoScopeApiException, api_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# 3. Register Modular Routers (Phase 3)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(markets.router)
app.include_router(derivatives.router)
app.include_router(orderbook.router)
app.include_router(orderflow.router)
app.include_router(liquidations.router)
app.include_router(predictions.router)
app.include_router(alerts.router)
app.include_router(paper.router)
app.include_router(providers.router)


# 4. Canonical WebSocket Market Stream (Phase 2)
@app.websocket("/api/v1/ws/market")
@app.websocket("/ws")  # Deprecated alias
async def websocket_market_endpoint(websocket: WebSocket):
    """
    Multiplexed real-time WebSocket market feed for tickers, depth, and predictions.
    """
    await websocket.accept()
    from services.websocket_manager import ws_manager
    client_id = await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.handle_client_message(client_id, data)
    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)
    except Exception as exc:
        logger.warning("WebSocket client %s exception: %s", client_id, exc)
        await ws_manager.disconnect(client_id)
