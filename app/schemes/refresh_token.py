from pydantic import BaseModel

from app.schemes.device_info import SDeviceInfo


class SRefreshToken(BaseModel):
    user_id: int
    token_hash: str
    created_at: int
    expires_at: int
    device_info: SDeviceInfo
