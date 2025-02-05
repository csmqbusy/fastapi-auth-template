import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import refresh_token_repo, user_repo
from app.schemes.refresh_token import SRefreshToken
from app.schemes.device_info import SDeviceInfo
from app.schemes.user import SUserSignUp


async def _add_mock_users_to_db(db_session: AsyncSession, qty: int) -> None:
    for i in range(qty):
        user = SUserSignUp(
            username=f"mock_user_{200 + i}",
            password="qwerty".encode(),
            email=f"mock_email_{i}@example.com",  # noqa
        )
        await user_repo.add(db_session, user.model_dump())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, token_hash, created_at, expires_at, device_info, add_mock_users",
    [
        (
            1,
            "hash1",
            1234567890,
            1234567890 + 3600,
            SDeviceInfo(user_agent="Mozilla/5.0", ip_address="192.168.1.1"),
            True,
        ),
        (
            2,
            "hash2",
            1234567891,
            1234567891 + 3600,
            SDeviceInfo(user_agent="Mozilla/5.0", ip_address="192.168.1.2"),
            False,
        ),
    ]
)
async def test_add_refresh_token(
    db_session: AsyncSession,
    user_id: int,
    token_hash: str,
    created_at: int,
    expires_at: int,
    device_info: SDeviceInfo,
    add_mock_users: bool,
):
    if add_mock_users:
        await _add_mock_users_to_db(db_session, 10)

    refresh_token = SRefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        created_at=created_at,
        expires_at=expires_at,
        device_info=device_info,
    )
    await refresh_token_repo.add(db_session, refresh_token.model_dump())
    tokens = await refresh_token_repo.get_all(db_session, {})
    added_token = tokens[-1]

    assert added_token.user_id == user_id
    assert added_token.token_hash == token_hash
    assert added_token.created_at == created_at
    assert added_token.expires_at == expires_at
    device_info_from_db_scheme = SDeviceInfo.model_validate(
        added_token.device_info)
    assert device_info_from_db_scheme == device_info


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, token_hash, created_at, expires_at, device_info",
    [
        (
            1,
            "hash11",
            1234567890,
            1234567890 + 3600,
            SDeviceInfo(user_agent="Mozilla/5.0", ip_address="192.168.1.1"),
        ),
        (
            2,
            "hash21",
            1234567890,
            1234567890 + 3600,
            SDeviceInfo(user_agent="Mozilla/5.0", ip_address="192.168.1.2"),
        ),
    ]
)
async def test_get_refresh_token(
    db_session: AsyncSession,
    user_id: int,
    token_hash: str,
    created_at: int,
    expires_at: int,
    device_info: SDeviceInfo,
):
    all_users_in_db = await user_repo.get_all(db_session, {})
    if len(all_users_in_db) < 10:
        await _add_mock_users_to_db(db_session, 10)

    refresh_token = SRefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        created_at=created_at,
        expires_at=expires_at,
        device_info=device_info,
    )
    token_from_db = await refresh_token_repo.add(
        db_session, refresh_token.model_dump())
    token_after_get = await refresh_token_repo.get(db_session, token_from_db.id)
    assert token_after_get.id == token_from_db.id
    assert token_after_get.user_id == user_id
    assert token_after_get.token_hash == token_hash
    device_info_from_db_scheme = SDeviceInfo.model_validate(
        token_after_get.device_info
    )
    assert device_info_from_db_scheme == device_info


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, token_hash, add_n_times",
    [
        (
            1,
            "hash21",
            1,
        ),
        (
            2,
            "hash22",
            9,
        ),
        (
            3,
            "hash23",
            0,
        ),
    ]
)
async def test_get_all_refresh_tokens(
    db_session: AsyncSession,
    user_id: int,
    token_hash: str,
    add_n_times: int,
):
    all_users_in_db = await user_repo.get_all(db_session, {})
    if len(all_users_in_db) < 10:
        await _add_mock_users_to_db(db_session, 10)

    tokens = await refresh_token_repo.get_all(db_session, {})
    tokens_qty_before = len(tokens)
    for i in range(add_n_times):
        refresh_token = SRefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            created_at=1234567890,
            expires_at=1234567890 + 3600,
            device_info=SDeviceInfo(
                user_agent="Mozilla/5.0", ip_address="192.168.1.4"),
        )
        await refresh_token_repo.add(db_session, refresh_token.model_dump())

    tokens = await refresh_token_repo.get_all(db_session, {})
    tokens_qty_after = len(tokens)
    assert tokens_qty_before + add_n_times == tokens_qty_after


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, token_hash, iat, exp, device_info, typo_token_hash, typo_user_id",
    [
        (
            1,
            "hash31",
            1234567890,
            1234567890 + 3600,
            SDeviceInfo(user_agent="Mozilla/5.0", ip_address="192.168.1.1"),
            "hash_typo",
            11111,
        ),
    ]
)
async def test_get_refresh_token_by_filter(
    db_session: AsyncSession,
    user_id: int,
    token_hash: str,
    iat: int,
    exp: int,
    device_info: SDeviceInfo,
    typo_token_hash: str,
    typo_user_id: int,
):
    all_users_in_db = await user_repo.get_all(db_session, {})
    if len(all_users_in_db) < 10:
        await _add_mock_users_to_db(db_session, 10)

    refresh_token = SRefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        created_at=iat,
        expires_at=exp,
        device_info=device_info,
    )
    await refresh_token_repo.add(db_session, refresh_token.model_dump())
    token_from_db = await refresh_token_repo.get_by_filter(
        db_session,
        {"token_hash": token_hash},
    )
    assert token_from_db.token_hash == token_hash
    assert token_from_db.user_id == user_id

    none_from_db = await refresh_token_repo.get_by_filter(
        db_session,
        {"token_hash": typo_token_hash},
    )
    assert none_from_db is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, token_hash, created_at, expires_at, device_info",
    [
        (
            1,
            "hash41",
            1234567890,
            1234567890 + 3600,
            SDeviceInfo(user_agent="Mozilla/5.0", ip_address="192.168.1.1"),
        ),
    ]
)
async def test_delete_refresh_token(
    db_session: AsyncSession,
    user_id: int,
    token_hash: str,
    created_at: int,
    expires_at: int,
    device_info: SDeviceInfo,
):
    all_users_in_db = await user_repo.get_all(db_session, {})
    if len(all_users_in_db) < 10:
        await _add_mock_users_to_db(db_session, 10)

    refresh_token = SRefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        created_at=created_at,
        expires_at=expires_at,
        device_info=device_info,
    )
    token_from_db = await refresh_token_repo.add(
        db_session, refresh_token.model_dump())

    tokens_before = await refresh_token_repo.get_all(db_session, {})
    tokens_before = [token.token_hash for token in tokens_before]
    assert token_hash in tokens_before

    await refresh_token_repo.delete(db_session, token_from_db.id)

    tokens_after = await refresh_token_repo.get_all(db_session, {})
    tokens_after = [token.token_hash for token in tokens_after]
    assert token_hash not in tokens_after

    assert len(tokens_before) - 1 == len(tokens_after)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, token_hash_prefix, iat, exp, device_info, add_n_times",
    [
        (
            1,
            "hash5",
            1234567890,
            1234567890 + 3600,
            SDeviceInfo(
                user_agent="Unique User-Agent/777.0",
                ip_address="192.168.1.1",
            ),
            1,
        ),
        (
            2,
            "hash5",
            1234567890,
            1234567890 + 3600,
            SDeviceInfo(
                user_agent="Unique User-Agent/777.0",
                ip_address="192.168.1.1",
            ),
            5,
        ),
        (
            3,
            "hash5",
            1234567890,
            1234567890 + 3600,
            SDeviceInfo(
                user_agent="Unique User-Agent/777.0",
                ip_address="192.168.1.1",
            ),
            0,
        ),
    ]
)
async def test_get_tokens_by_device_info(
    db_session: AsyncSession,
    user_id: int,
    token_hash_prefix: str,
    iat: int,
    exp: int,
    device_info: SDeviceInfo,
    add_n_times: int,
):
    all_users_in_db = await user_repo.get_all(db_session, {})
    if len(all_users_in_db) < 10:
        await _add_mock_users_to_db(db_session, 10)

    for i in range(add_n_times):
        refresh_token = SRefreshToken(
            user_id=user_id,
            token_hash=f"{token_hash_prefix}{i}",
            created_at=iat,
            expires_at=exp,
            device_info=device_info,
        )
        await refresh_token_repo.add(db_session, refresh_token.model_dump())

    tokens_from_db = await refresh_token_repo.get_tokens_by_device_info(
        db_session,
        user_id,
        device_info,
    )

    assert len(tokens_from_db) == add_n_times
    for refresh_token in tokens_from_db:
        assert refresh_token.user_id == user_id
        assert refresh_token.device_info == device_info.model_dump()
