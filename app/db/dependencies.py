from typing import AsyncGenerator

from app.core.config import settings
from app.db.manager import DatabaseSessionManager
from sqlalchemy.ext.asyncio import AsyncSession

database_manager = DatabaseSessionManager(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in database_manager.get_session():
        yield session


async def close_db():
    await database_manager.dispose()
