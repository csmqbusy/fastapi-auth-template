from enum import Enum

import pytest
from starlette import status
from starlette.testclient import TestClient

from app.core.config import settings


class RegistrationExpectedResponse(Enum):
    CREATED = 0
    USERNAME_EXISTS = 1
    EMAIL_EXISTS = 2


class LoginFailType(Enum):
    NO_FAIL = 0
    USERNAME_ERROR = 1
    PASSWORD_ERROR = 2


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


@pytest.mark.parametrize(
    "username, password, email, status_code, fail_type",
    [
        (
            "daniel",
            "password",
            "daniel@example.com",
            status.HTTP_200_OK,
            LoginFailType.NO_FAIL,
        ),
        (
            "michael",
            "password",
            "michael@example.com",
            status.HTTP_401_UNAUTHORIZED,
            LoginFailType.USERNAME_ERROR,
        ),
        (
            "alice",
            "password",
            "alice@example.com",
            status.HTTP_401_UNAUTHORIZED,
            LoginFailType.PASSWORD_ERROR,
        ),
    ]
)
def test_login(
    client: TestClient,
    username: str,
    password: str,
    email: str,
    status_code: int,
    fail_type: LoginFailType,
):
    signup_response = client.post(
        url=f"{settings.api.prefix_v1}/registration/",
        json={
            "username": username,
            "password": password,
            "email": email,
        }
    )
    assert signup_response.status_code == status.HTTP_201_CREATED

    if fail_type == LoginFailType.NO_FAIL:
        assert client.cookies.get("access_token") is None
        assert client.cookies.get("refresh_token") is None
        login_response = client.post(
            url=f"{settings.api.prefix_v1}/login/",
            data={
                "username": username,
                "password": password,
            }
        )
        assert login_response.status_code == status_code
        assert login_response.json() == {"sign_in": "Success!"}
        assert client.cookies.get("access_token") is not None
        assert client.cookies.get("refresh_token") is not None

    else:
        if fail_type == LoginFailType.USERNAME_ERROR:
            username = username + "_fail"
        elif fail_type == LoginFailType.PASSWORD_ERROR:
            password = password + "_fail"

        assert client.cookies.get("access_token") is None
        assert client.cookies.get("refresh_token") is None
        login_response = client.post(
            url=f"{settings.api.prefix_v1}/login/",
            data={
                "username": username,
                "password": password,
            }
        )
        assert login_response.status_code == status_code
        assert login_response.json() == {"detail": "Could not validate credentials."}
        assert client.cookies.get("access_token") is None
        assert client.cookies.get("refresh_token") is None
