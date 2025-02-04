import hashlib

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import RefreshTokenModel
from app.repositories.refresh_token import refresh_token_repo
from app.schemes.device_info import SDeviceInfo
from app.schemes.refresh_token import SRefreshToken


async def add_refresh_token_to_db(
    session: AsyncSession,
    token: str,
    user_id: int,
    created_at: int,
    expires_at: int,
    device_info: SDeviceInfo,
) -> None:

    all_user_sessions = await _get_all_user_auth_sessions(session, user_id)
    if len(all_user_sessions) >= settings.auth.max_active_auth_sessions:
        await _delete_all_user_auth_sessions(session, all_user_sessions)

    await _delete_same_device_auth_sessions(session, user_id, device_info)

    token_scheme = SRefreshToken(
        user_id=user_id,
        token_hash=_hash_token(token),
        created_at=created_at,
        expires_at=expires_at,
        device_info=device_info,
    )

    await refresh_token_repo.add(session, token_scheme.model_dump())


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def _delete_same_device_auth_sessions(
    session: AsyncSession,
    user_id: int,
    device_info: SDeviceInfo,
):
    same_device_auth_sessions = await _get_same_device_auth_sessions(
        session,
        user_id,
        device_info,
    )
    if same_device_auth_sessions:
        for auth_session in same_device_auth_sessions:
            await refresh_token_repo.delete(session, auth_session.id)


async def _delete_all_user_auth_sessions(
    session: AsyncSession,
    user_sessions: list[RefreshTokenModel],
):
    for auth_session in user_sessions:
        await refresh_token_repo.delete(session, auth_session.id)


async def _get_same_device_auth_sessions(
    session: AsyncSession,
    user_id: int,
    device_info: SDeviceInfo,
) -> list[RefreshTokenModel]:
    sessions = await refresh_token_repo.get_tokens_by_device_info(
        session,
        user_id=user_id,
        device_info=device_info,
    )
    return sessions


async def _get_all_user_auth_sessions(
    session: AsyncSession,
    user_id: int,
) -> list[RefreshTokenModel]:
    return await refresh_token_repo.get_all(session, dict(user_id=user_id))


async def check_token_in_db(
    session: AsyncSession,
    token: str,
) -> bool:
    token_hash = _hash_token(token)
    token_in_db = await refresh_token_repo.get_by_filter(
        session,
        {"token_hash": token_hash}
    )
    return bool(token_in_db)


async def delete_refresh_token_from_db(
    session: AsyncSession,
    token: str,
) -> None:
    token_in_db = await refresh_token_repo.get_by_filter(
        session,
        {"token_hash": _hash_token(token)},
    )
    if token_in_db:
        await refresh_token_repo.delete(session, token_in_db.id)
