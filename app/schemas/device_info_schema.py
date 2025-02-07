from pydantic import BaseModel


class SDeviceInfo(BaseModel):
    user_agent: str | None
    ip_address: str | None
