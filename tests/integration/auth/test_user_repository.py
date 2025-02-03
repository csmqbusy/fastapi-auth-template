from contextlib import nullcontext

import pytest
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import ContextManager

from app.repositories import user_repo
from app.schemes.user import SUserSignUp


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, expectation",
    [
        (
            "vicky",
            "password",
            "vicky@example.com",
            nullcontext(),
        ),
        (
            "vicky",
            "password",
            "vicky@example.com",
            pytest.raises(IntegrityError),
        ),
        (
            "messi",
            "password",
            "messi@example.com",
            nullcontext(),
        ),
    ]
)
async def test_add_user(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
    expectation: ContextManager,
):
    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    with expectation:
        await user_repo.add(db_session, user.model_dump())
        users = await user_repo.get_all(db_session, {})
        added_user = users[-1]
        assert added_user.username == username
        assert added_user.email == email
