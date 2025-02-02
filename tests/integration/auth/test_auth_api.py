from enum import StrEnum

import pytest
from starlette import status
from starlette.testclient import TestClient

from app.core.config import settings


class RegistrationExpectedResponse(StrEnum):
    CREATED = "created"
    USERNAME_EXISTS = "username_exists"
    EMAIL_EXISTS = "email_exists"


@pytest.mark.parametrize(
    "username, password, email, status_code, expected_response",
    [
        (
            "mike",
            "password",
            "mike@example.com",
            status.HTTP_201_CREATED,
            RegistrationExpectedResponse.CREATED,
        ),
        (
            "mike",
            "password",
            "mike22@example.com",
            status.HTTP_409_CONFLICT,
            RegistrationExpectedResponse.USERNAME_EXISTS,
        ),
        (
            "john",
            "password",
            "mike@example.com",
            status.HTTP_409_CONFLICT,
            RegistrationExpectedResponse.EMAIL_EXISTS,
        ),
        (
            "john",
            "password",
            "john@example.com",
            status.HTTP_201_CREATED,
            RegistrationExpectedResponse.CREATED,
        ),
    ]
)
def test_sign_up_user(
    client: TestClient,
    username: str,
    password: str,
    email: str,
    status_code: int,
    expected_response: RegistrationExpectedResponse,
):
    expected_response_json = None
    if expected_response == RegistrationExpectedResponse.CREATED:
        expected_response_json = {"username": username, "email": email}
    elif expected_response == RegistrationExpectedResponse.USERNAME_EXISTS:
        expected_response_json = {"detail": "Username already exists."}
    elif expected_response == RegistrationExpectedResponse.EMAIL_EXISTS:
        expected_response_json = {"detail": "Email already exists."}

    response = client.post(
        url=f"{settings.api.prefix_v1}/registration/",
        json={
            "username": username,
            "password": password,
            "email": email,
        }
    )
    assert response.status_code == status_code
    assert response.json() == expected_response_json
