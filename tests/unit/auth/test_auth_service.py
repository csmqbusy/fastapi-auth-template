from contextlib import nullcontext
from datetime import datetime, UTC
from typing import ContextManager

import pytest

from app.core.config import settings
from app.services.auth import (
    TokenType,
    get_token_iat_and_exp,
    SECS_IN_HOUR,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)


@pytest.mark.parametrize(
    "token_type, expectation",
    [
        (
            TokenType.ACCESS,
            nullcontext(),
        ),
        (
            TokenType.REFRESH,
            nullcontext(),
        ),
        (
            "FakeTokenType",
            pytest.raises(ValueError),
        ),
    ]
)
def test_get_token_iat_and_exp(
    token_type: TokenType,
    expectation: ContextManager,
):
    with expectation:
        iat_and_exp = get_token_iat_and_exp(token_type)
        iat = iat_and_exp["iat"]
        exp = iat_and_exp["exp"]
        if token_type == TokenType.ACCESS:
            assert exp - iat == settings.auth.access_token_expires_sec
        elif token_type == TokenType.REFRESH:
            refresh_token_expires_sec = (
                settings.auth.refresh_token_expires_days * SECS_IN_HOUR
            )
            assert exp - iat == refresh_token_expires_sec


@pytest.mark.parametrize(
    "payload",
    [
        {"sub": "etoo"},
    ]
)
def test_create_access_token(
    payload: dict,
):
    iat = int(datetime.now(UTC).timestamp())
    exp = iat + 300
    token = create_access_token(payload, iat, exp)
    assert token is not None
    assert isinstance(token, str)

    decoded_payload = decode_access_token(token)
    assert decoded_payload is not None
    assert decoded_payload["sub"] == payload["sub"]
    assert decoded_payload["iat"] == iat
    assert decoded_payload["exp"] == exp


@pytest.mark.parametrize(
    "payload",
    [
        {"sub": "ronaldinho"},
    ]
)
def test_create_refresh_token(
    payload: dict,
):
    iat = int(datetime.now(UTC).timestamp())
    exp = iat + 30000
    token = create_refresh_token(payload, iat, exp)
    assert token is not None
    assert isinstance(token, str)

    decoded_payload = decode_refresh_token(token)
    assert decoded_payload is not None
    assert decoded_payload["sub"] == payload["sub"]
    assert decoded_payload["iat"] == iat
    assert decoded_payload["exp"] == exp


@pytest.mark.parametrize(
    "password",
    [
        "qwerty",
    ]
)
def test_hash_password(
    password: str,
):
    hashed_password = hash_password(password)
    assert hashed_password is not None
    assert verify_password(password, hashed_password)
