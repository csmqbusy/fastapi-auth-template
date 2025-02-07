from pydantic import BaseModel

from app.schemas.device_info_schema import SDeviceInfo


class SRefreshToken(BaseModel):
    user_id: int
    token_hash: str
    created_at: int
    expires_at: int
    device_info: SDeviceInfo
