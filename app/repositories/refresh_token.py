from sqlalchemy import select, cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshTokenModel
from app.repositories.base import BaseRepository
from app.schemes.device_info import SDeviceInfo


class RefreshTokenRepository(BaseRepository[RefreshTokenModel]):
    def __init__(self):
        super().__init__(RefreshTokenModel)

    async def get_tokens_by_device_info(
        self,
        session: AsyncSession,
        user_id: int,
        device_info: SDeviceInfo,
    ) -> list[RefreshTokenModel]:
        device_info_dict = device_info.model_dump()
        query = select(self.model).filter(
            self.model.user_id == user_id,
            cast(self.model.device_info, JSONB).contains(device_info_dict),
        )
        result = await session.execute(query)
        same_device_tokens = result.scalars().all()
        return list(same_device_tokens)


refresh_token_repo = RefreshTokenRepository()
