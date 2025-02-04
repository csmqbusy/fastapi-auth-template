import pytest
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import user_repo, refresh_token_repo
from app.schemes.device_info import SDeviceInfo
from app.schemes.refresh_token import SRefreshToken
from app.schemes.user import SUserSignUp
from app.services.refresh_token import (
    _get_all_user_auth_sessions,
    _hash_token,
    check_token_in_db,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, add_n_times",
    [
        (
            "lukaku",
            "password",
            "lukaku@example.com",
            2,
        ),
        (
            "januzaj",
            "password",
            "januzaj@example.com",
            0,
        ),
        (
            "vermaelen",
            "password",
            "vermaelen@example.com",
            9,
        ),
    ]
)
async def test__get_all_user_auth_sessions(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
    add_n_times: int,
):
    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    user_from_db = await user_repo.add(db_session, user.model_dump())
    user_id = user_from_db.id

    for i in range(add_n_times):
        refresh_token = SRefreshToken(
            user_id=user_id,
            token_hash=f"lukaku_token_hash_{i}",
            created_at=1234567890,
            expires_at=1234567890 + 3600,
            device_info=SDeviceInfo(
                user_agent=f"Mozilla/{i}",
                ip_address=f"12{i}.{i}.{i}",
            ),
        )
        await refresh_token_repo.add(db_session, refresh_token.model_dump())

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    user_id_for_sessions = [i.user_id == user_id for i in user_sessions]
    assert len(user_sessions) == add_n_times
    assert all(user_id_for_sessions)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, token",
    [
        (
            "pogba",
            "password",
            "pogba@example.com",
            "pogba_token",
        ),
    ]
)
async def test_check_token_in_db(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
    token: str,
):
    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    user_id = (await user_repo.add(db_session, user.model_dump())).id
    token_hash = _hash_token(token)

    assert await check_token_in_db(db_session, token) is False

    refresh_token = SRefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        created_at=1234567890,
        expires_at=1234567890 + 3600,
        device_info=SDeviceInfo(user_agent="Mozilla", ip_address="1.1.1"),
    )
    await refresh_token_repo.add(db_session, refresh_token.model_dump())

    assert await check_token_in_db(db_session, token) is True
