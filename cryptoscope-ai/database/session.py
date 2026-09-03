"""
CryptoScope AI - Database Base & Session Management
"""
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from core.config import settings

Base = declarative_base()

# SQLite fallback for quick local testing/in-memory evaluation, or Postgres in production
DATABASE_URL = "sqlite+aiosqlite:///./cryptoscope.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
