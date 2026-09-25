from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Engine asíncrono con pool de conexiones optimizado
async_engine = create_async_engine(
    str(settings.async_database_uri),
    echo=(settings.ENVIRONMENT == "development"),
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verifica conexiones muertas antes de usarlas
)

# Session Factory asincrono
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia FastAPI para inyectar sesiones con cierre garantizado."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
