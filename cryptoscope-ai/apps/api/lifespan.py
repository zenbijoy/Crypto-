"""
CryptoScope AI - FastAPI Master Gateway Lifespan
Manages startup discovery, database connection pools, Redis cache initialization,
and graceful shutdown.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from core.redis import redis_client
from database.session import init_db
from services.registry import registry
from services.redis_service import redis_service

logger = logging.getLogger("cryptoscope.api.lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup & Shutdown lifecycle hook for CryptoScope AI Canonical Gateway.
    """
    logger.info("Initializing CryptoScope AI Canonical Backend...")
    
    # 1. Connect Redis layer
    try:
        await redis_client.connect()
        await redis_service.connect()
    except Exception as exc:
        logger.warning("Redis initialization non-blocking notice: %s", exc)

    # 2. Initialize database schema
    try:
        await init_db()
        logger.info("Database schemas verified.")
    except Exception as exc:
        logger.warning("Database init non-blocking notice: %s", exc)

    # 3. Discover instruments and seed provider registry
    try:
        await registry.initialize_and_discover()
        logger.info("Exchange registry and instrument auto-discovery complete.")
    except Exception as exc:
        logger.warning("Provider discovery non-blocking notice: %s", exc)

    yield

    # Shutdown sequence
    logger.info("Shutting down CryptoScope AI Canonical Backend...")
    try:
        await redis_client.close()
        await redis_service.close()
    except Exception as exc:
        logger.error("Error closing Redis connections: %s", exc)
    logger.info("Shutdown complete.")
