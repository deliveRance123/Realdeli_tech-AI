from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# Render/most free Postgres hosts give a URL starting with postgres:// or
# postgresql://. SQLAlchemy's async driver needs postgresql+asyncpg://.
_url = DATABASE_URL
if _url.startswith("postgres://"):
    _url = _url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _url.startswith("postgresql://"):
    _url = _url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(_url, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def init_db():
    """Create tables if they don't exist yet. Called once on bot startup."""
    from database import models  # noqa: F401 (ensures models are registered)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
