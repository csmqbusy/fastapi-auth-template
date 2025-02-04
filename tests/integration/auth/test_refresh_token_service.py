import pytest
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories import user_repo, refresh_token_repo
from app.schemes.device_info import SDeviceInfo
from app.schemes.refresh_token import SRefreshToken
from app.schemes.user import SUserSignUp
from app.services.refresh_token import (
    _get_all_user_auth_sessions,
    _hash_token,
    check_token_in_db,
    delete_refresh_token_from_db,
    _delete_all_user_auth_sessions,
    _delete_same_device_auth_sessions,
    add_refresh_token_to_db,
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, token",
    [
        (
            "hummels",
            "password",
            "hummels@example.com",
            "hummels_token",
        ),
    ]
)
async def test_delete_refresh_token_from_db(
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

    refresh_token = SRefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        created_at=1234567890,
        expires_at=1234567890 + 3600,
        device_info=SDeviceInfo(user_agent="Mozilla", ip_address="1.1.1"),
    )
    await refresh_token_repo.add(db_session, refresh_token.model_dump())

    assert await check_token_in_db(db_session, token) is True

    await delete_refresh_token_from_db(db_session, token)
    assert await check_token_in_db(db_session, token) is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, token_prefix, add_n_times",
    [
        (
            "neuer",
            "password",
            "neuer@example.com",
            "neuer_token",
            7,
        ),
        (
            "robben",
            "password",
            "robben@example.com",
            "robben_token",
            0,
        ),
    ]
)
async def test__delete_all_user_auth_sessions(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
    token_prefix: str,
    add_n_times: int,
):
    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    user_id = (await user_repo.add(db_session, user.model_dump())).id

    for i in range(add_n_times):
        token_hash = _hash_token(f"{token_prefix}_{i}")
        refresh_token = SRefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            created_at=1234567890,
            expires_at=1234567890 + 3600,
            device_info=SDeviceInfo(user_agent="Mozilla", ip_address=f"1.{i}"),
        )
        await refresh_token_repo.add(db_session, refresh_token.model_dump())

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == add_n_times

    await _delete_all_user_auth_sessions(db_session, user_sessions)

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, token_prefix, device_info, same_tokens, "
    "diff_tokens",
    [
        (
            "ribery",
            "password",
            "ribery@example.com",
            "ribery_token",
            SDeviceInfo(user_agent="Opera", ip_address="2.2.2"),
            3,
            2,
        ),
        (
            "klose",
            "password",
            "klose@example.com",
            "klose_token",
            SDeviceInfo(user_agent="Opera", ip_address="2.2.2"),
            8,
            0,
        ),
        (
            "dante",
            "password",
            "dante@example.com",
            "dante_token",
            SDeviceInfo(user_agent="Opera", ip_address="2.2.2"),
            0,
            3,
        ),
    ]
)
async def test__delete_same_device_auth_sessions(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
    token_prefix: str,
    device_info: SDeviceInfo,
    same_tokens: int,
    diff_tokens: int,
):
    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    user_id = (await user_repo.add(db_session, user.model_dump())).id

    for _ in range(same_tokens):
        token_hash = _hash_token(token_prefix)
        refresh_token = SRefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            created_at=1234567890,
            expires_at=1234567890 + 3600,
            device_info=device_info
        )
        await refresh_token_repo.add(db_session, refresh_token.model_dump())

    for i in range(diff_tokens):
        token_hash = _hash_token(token_prefix)
        refresh_token = SRefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            created_at=1234567890,
            expires_at=1234567890 + 3600,
            device_info=SDeviceInfo(user_agent="Opera", ip_address=f"1.1.{i}"),
        )
        await refresh_token_repo.add(db_session, refresh_token.model_dump())

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == same_tokens + diff_tokens

    await _delete_same_device_auth_sessions(db_session, user_id, device_info)

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == diff_tokens


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, token",
    [
        (
            "mbappe",
            "password",
            "mbappe@example.com",
            "mbappe_token",
        ),
    ]
)
async def test_add_refresh_token_to_db__first_token(
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

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == 0

    await add_refresh_token_to_db(
        session=db_session,
        token=token,
        user_id=user_id,
        created_at=1234567890,
        expires_at=1234567890 + 3600,
        device_info=SDeviceInfo(user_agent="Opera", ip_address="2.2.2"),
    )

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, token",
    [
        (
            "arteta",
            "password",
            "arteta@example.com",
            "arteta_token",
        ),
    ]
)
async def test_add_refresh_token_to_db__too_much_active_auth_sessions(
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

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == 0

    for _ in range(settings.auth.max_active_auth_sessions):
        refresh_token = SRefreshToken(
            user_id=user_id,
            token_hash=token,
            created_at=1234567890,
            expires_at=1234567890 + 3600,
            device_info=SDeviceInfo(user_agent="Opera", ip_address="2.2.2")
        )
        await refresh_token_repo.add(db_session, refresh_token.model_dump())

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == settings.auth.max_active_auth_sessions

    last_token_device_info = SDeviceInfo(
        user_agent="Marked session",
        ip_address="77.2.2",
    )
    await add_refresh_token_to_db(
        session=db_session,
        token=token,
        user_id=user_id,
        created_at=1234567890,
        expires_at=1234567890 + 3600,
        device_info=last_token_device_info,
    )

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == 1

    assert user_sessions[0].device_info == last_token_device_info.model_dump()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, email, token, same_dev_info, diff_dev_info",
    [
        (
            "saliba",
            "password",
            "saliba@example.com",
            "saliba_token",
            2,
            1,
        ),
        (
            "nketiah",
            "password",
            "nketiah@example.com",
            "nketiah_token",
            1,
            3,
        ),
        (
            "iwobi",
            "password",
            "iwobi@example.com",
            "iwobi_token",
            0,
            4,
        ),
        (
            "xhaka",
            "password",
            "xhaka@example.com",
            "xhaka_token",
            4,
            0,
        ),
        (
            "holding",
            "password",
            "holding@example.com",
            "holding_token",
            0,
            0,
        ),
    ]
)
async def test_add_refresh_token_to_db__same_device_info(
    db_session: AsyncSession,
    username: str,
    password: str,
    email: EmailStr,
    token: str,
    same_dev_info: int,
    diff_dev_info: int,
):
    user = SUserSignUp(
        username=username,
        password=password.encode(),
        email=email,
    )
    user_id = (await user_repo.add(db_session, user.model_dump())).id

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == 0

    repeating_device_info = SDeviceInfo(
        user_agent="Same device info",
        ip_address="127.00.11",
    )
    for _ in range(same_dev_info):
        refresh_token = SRefreshToken(
            user_id=user_id,
            token_hash=token,
            created_at=1234567890,
            expires_at=1234567890 + 3600,
            device_info=repeating_device_info
        )
        await refresh_token_repo.add(db_session, refresh_token.model_dump())

    for i in range(diff_dev_info):
        refresh_token = SRefreshToken(
            user_id=user_id,
            token_hash=token,
            created_at=1234567890,
            expires_at=1234567890 + 3600,
            device_info=SDeviceInfo(user_agent="Opera", ip_address=f"1.1.{i}"),
        )
        await refresh_token_repo.add(db_session, refresh_token.model_dump())

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == same_dev_info + diff_dev_info

    await add_refresh_token_to_db(
        session=db_session,
        token=token,
        user_id=user_id,
        created_at=1234567890,
        expires_at=1234567890 + 3600,
        device_info=repeating_device_info,
    )

    user_sessions = await _get_all_user_auth_sessions(db_session, user_id)
    assert len(user_sessions) == diff_dev_info + 1
