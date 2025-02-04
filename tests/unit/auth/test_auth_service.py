from contextlib import nullcontext
from typing import ContextManager

import pytest

from app.core.config import settings
from app.services.auth import (
    TokenType,
    get_token_iat_and_exp,
    SECS_IN_HOUR,
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
