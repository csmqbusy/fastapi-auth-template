from contextlib import nullcontext
from typing import ContextManager

import pytest
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.user_exceptions import UsernameAlreadyExists, EmailAlreadyExists
from app.models import UserModel
from app.repositories import user_repo
from app.schemas.user_schemas import SUserSignUp
from app.services.user_service import (
    _check_unique_username,
    _check_unique_email,
    get_user_by_username,
    create_user,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email",
    [
        (
            "aubameyang",
            "password",
            "aubameyang@example.com",
        ),
    ]
)
async def test__check_unique_username(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
):
    assert await _check_unique_username(username, db_session) is True

    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    await user_repo.add(db_session, user.model_dump())

    assert await _check_unique_username(username, db_session) is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email",
    [
        (
            "ibrahimovic",
            "password",
            "ibrahimovic@example.com",
        ),
    ]
)
async def test__check_unique_email(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
):
    assert await _check_unique_email(email, db_session) is True

    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    await user_repo.add(db_session, user.model_dump())

    assert await _check_unique_email(email, db_session) is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email",
    [
        (
            "bukayo",
            "password",
            "bukayo@example.com",
        ),
    ]
)
async def test_get_user_by_username(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
):
    assert await get_user_by_username(username, db_session) is None

    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    await user_repo.add(db_session, user.model_dump())

    user_from_db = await get_user_by_username(username, db_session)
    assert isinstance(user_from_db, UserModel)
    assert user_from_db.username == username
    assert user_from_db.email == email


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, expectation",
    [
        (
            "salah",
            "password",
            "salah@example.com",
            nullcontext(),
        ),
        (
            "salah",
            "password",
            "mosalah@example.com",
            pytest.raises(UsernameAlreadyExists),
        ),
        (
            "mosalah",
            "password",
            "salah@example.com",
            pytest.raises(EmailAlreadyExists),
        ),
        (
            "bergkamp",
            "password",
            "bergkamp@example.com",
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
        await create_user(user, db_session)
        user_from_db = await get_user_by_username(user.username, db_session)
        assert isinstance(user_from_db, UserModel)
        assert user_from_db.username == username
        assert user_from_db.email == email
