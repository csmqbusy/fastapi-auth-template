from pydantic import BaseModel, EmailStr


class SUserSignIn(BaseModel):
    username: str
    password: bytes


class SUserSignUp(SUserSignIn):
    email: EmailStr
    active: bool = True
