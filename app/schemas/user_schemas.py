from pydantic import BaseModel, EmailStr, ConfigDict


class SUserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str


class SUserSignIn(SUserBase):
    password: bytes


class SUserSignUp(SUserSignIn):
    email: EmailStr
    active: bool = True


class SUserShortInfo(SUserBase):
    email: EmailStr
