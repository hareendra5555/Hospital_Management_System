from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

settings = get_settings()

# The engine is the core interface to the database
# It manages the connection pool automatically
# pool_size=10 means 10 persistent connections
# max_overflow=20 means 20 extra connections allowed under heavy load
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
)

# Session factory — creates DB sessions on demand
# expire_on_commit=False means objects stay usable after a commit
# Without this, accessing an attribute after commit triggers another DB call
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class for all SQLAlchemy models
# Every model will inherit from this
class Base(DeclarativeBase):
    pass


# Dependency — used in routes and services to get a DB session
# WHY a generator function?
# The try/finally guarantees the session is ALWAYS closed
# even if an exception occurs mid-request
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()