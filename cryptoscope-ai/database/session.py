"""
CryptoScope AI - Production Database Base & Async Engine (Step 7)
Supports PostgreSQL + TimescaleDB (production) and SQLite (tests/dev).
Uses settings.DATABASE_URL.
"""
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from core.config import settings
import logging

logger = logging.getLogger("cryptoscope.db")

Base = declarative_base()

# Retrieve database URL from centralized settings
db_url = settings.DATABASE_URL
if not db_url:
    db_url = "sqlite+aiosqlite:///./cryptoscope.db"

# Engine configuration with appropriate pooling
connect_args = {}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args
)

async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session

async def init_db():
    """Initializes schema tables if not present."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
