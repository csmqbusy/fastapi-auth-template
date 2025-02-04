from datetime import datetime, UTC
from enum import StrEnum

import bcrypt
import jwt

from app.core.config import settings

SECS_IN_HOUR = 60 * 60 * 24


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


def _create_jwt(
    payload: dict,
    token_type: TokenType,
    private_key: str,
    iat: int,
    expire: int,
    algorithm: str = settings.auth.algorithm,
) -> str:
    to_encode = payload.copy()
    to_encode.update(
        iat=iat,
        exp=expire,
        token_type=token_type,
    )
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )
    return encoded_jwt


def create_access_token(
    payload: dict,
    iat: int,
    expire: int,
    token_type: TokenType = TokenType.ACCESS,
    private_key: str = settings.auth.access_private_key_path.read_text(),
) -> str:
    return _create_jwt(
        payload=payload,
        token_type=token_type,
        private_key=private_key,
        iat=iat,
        expire=expire,
    )


def create_refresh_token(
    payload: dict,
    iat: int,
    expire: int,
    token_type: TokenType = TokenType.REFRESH,
    private_key: str = settings.auth.refresh_private_key_path.read_text(),
) -> str:
    return _create_jwt(
        payload=payload,
        token_type=token_type,
        private_key=private_key,
        iat=iat,
        expire=expire,
    )


def _decode_jwt(
    token: str | bytes,
    public_key: str,
    algorithm: str = settings.auth.algorithm,
):
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm]
    )
    return decoded


def decode_access_token(
    token: str | bytes,
    public_key: str = settings.auth.access_public_key_path.read_text(),
):
    return _decode_jwt(token, public_key)


def decode_refresh_token(
    token: str | bytes,
    public_key: str = settings.auth.refresh_public_key_path.read_text(),
):
    return _decode_jwt(token, public_key)


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password)


def get_token_iat_and_exp(token_type: TokenType) -> dict[str, int]:
    now = int(datetime.now(UTC).timestamp())
    if token_type == TokenType.ACCESS:
        time_to_live = settings.auth.access_token_expires_sec
    elif token_type == TokenType.REFRESH:
        time_to_live = settings.auth.refresh_token_expires_days * SECS_IN_HOUR
    else:
        raise ValueError("Invalid token type")
    expire = now + time_to_live
    return {"iat": now, "exp": expire}
