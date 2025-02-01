from pydantic import BaseModel


class SDeviceInfo(BaseModel):
    user_agent: str
    ip_address: str
