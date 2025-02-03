import pytest
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import user_repo
from app.schemes.user import SUserSignUp
from app.services.user import _check_unique_username, _check_unique_email


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
