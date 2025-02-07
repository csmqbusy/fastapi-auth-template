from typing import Type, TypeVar, Generic, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def add(
        self,
        session: AsyncSession,
        obj_in: dict,
    ) -> T:
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get(
        self,
        session: AsyncSession,
        id_: Any,
    ) -> T | None:
        return await session.get(self.model, id_)

    async def get_all(
        self,
        session: AsyncSession,
        params: dict,
    ) -> list[T]:
        query = select(self.model).filter_by(**params)
        result = (await session.execute(query)).scalars().all()
        return list(result)

    async def get_by_filter(
        self,
        session: AsyncSession,
        params: dict,
    ) -> T | None:
        query = select(self.model).filter_by(**params)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def delete(
        self,
        session: AsyncSession,
        id_: Any,
    ) -> None:
        db_obj = await self.get(session, id_)
        if db_obj:
            await session.delete(db_obj)
            await session.commit()
