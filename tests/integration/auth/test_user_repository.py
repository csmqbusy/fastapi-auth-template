from contextlib import nullcontext

import pytest
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import ContextManager

from app.repositories import user_repo
from app.schemas.user import SUserSignUp


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email",
    [
        (
            "ronaldo",
            "password",
            "ronaldo@example.com",
        ),
        (
            "henry",
            "password",
            "henry@example.com",
        ),
    ]
)
async def test_get_user(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
):
    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    user_from_db = await user_repo.add(db_session, user.model_dump())
    user_after_get = await user_repo.get(db_session, user_from_db.id)
    assert user_after_get.id == user_from_db.id
    assert user_after_get.username == username
    assert user_after_get.email == email


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email_prefix, add_n_times",
    [
        (
            "benzema",
            "password",
            "benzema",
            1,
        ),
        (
            "ozil",
            "password",
            "ozil",
            7,
        ),
        (
            "ramos",
            "pasword",
            "ramos",
            0,
        ),
    ]
)
async def test_get_all_users(
    db_session: AsyncSession,
    username: str,
    password: str,
    email_prefix: str,
    add_n_times: int,
):
    users = await user_repo.get_all(db_session, {})
    users_qty_before = len(users)
    for i in range(add_n_times):
        user = SUserSignUp(
            username=f"{username}_{i}",
            password=password.encode(),
            email=f"{email_prefix}_{i}@example.com",  # noqa
        )
        await user_repo.add(db_session, user.model_dump())

    users = await user_repo.get_all(db_session, {})
    users_qty_after = len(users)
    assert users_qty_before + add_n_times == users_qty_after


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, typo_username, typo_email",
    [
        (
            "zidan",
            "password",
            "zidan@example.com",
            "zidantypo",
            "zidanetypo@example.com",
        ),
    ]
)
async def test_get_user_by_filter(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
    typo_username: str,
    typo_email: EmailStr,
):
    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    await user_repo.add(db_session, user.model_dump())
    user_from_db = await user_repo.get_by_filter(
        db_session,
        {"email": email},
    )
    assert user_from_db.username == username
    assert user_from_db.email == email

    user_from_db = await user_repo.get_by_filter(
        db_session,
        {"username": username},
    )
    assert user_from_db.username == username
    assert user_from_db.email == email

    none_from_db = await user_repo.get_by_filter(
        db_session,
        {"username": typo_username},
    )
    assert none_from_db is None

    none_from_db = await user_repo.get_by_filter(
        db_session,
        {"email": typo_email},
    )
    assert none_from_db is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email",
    [
        (
            "iniesta",
            "password",
            "iniesta@example.com",
        ),
    ]
)
async def test_delete_user(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
):
    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    user_from_db = await user_repo.add(db_session, user.model_dump())

    users_before = await user_repo.get_all(db_session, {})
    users_before = [user.username for user in users_before]
    assert username in users_before

    await user_repo.delete(db_session, user_from_db.id)

    users_after = await user_repo.get_all(db_session, {})
    users_after = [user.username for user in users_after]
    assert username not in users_after

    assert len(users_before) - 1 == len(users_after)
