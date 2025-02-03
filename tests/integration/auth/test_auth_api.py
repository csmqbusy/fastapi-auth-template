import time
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


class RefreshFailType(Enum):
    NO_FAIL = 0
    NO_TOKEN = 1
    INVALID_TOKEN = 2


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
    expected_json_answer = None
    if expected_response == RegistrationExpectedResponse.CREATED:
        expected_json_answer = {"username": username, "email": email}
    elif expected_response == RegistrationExpectedResponse.USERNAME_EXISTS:
        expected_json_answer = {"detail": "Username already exists."}
    elif expected_response == RegistrationExpectedResponse.EMAIL_EXISTS:
        expected_json_answer = {"detail": "Email already exists."}

    response = client.post(
        url=f"{settings.api.prefix_v1}/registration/",
        json={
            "username": username,
            "password": password,
            "email": email,
        }
    )
    assert response.status_code == status_code
    assert response.json() == expected_json_answer


@pytest.mark.parametrize(
    "username, password, email, status_code, fail_type, json_answer",
    [
        (
            "daniel",
            "password",
            "daniel@example.com",
            status.HTTP_200_OK,
            LoginFailType.NO_FAIL,
            {"sign_in": "Success!"}
        ),
        (
            "michael",
            "password",
            "michael@example.com",
            status.HTTP_401_UNAUTHORIZED,
            LoginFailType.USERNAME_ERROR,
            {"detail": "Could not validate credentials."},
        ),
        (
            "alice",
            "password",
            "alice@example.com",
            status.HTTP_401_UNAUTHORIZED,
            LoginFailType.PASSWORD_ERROR,
            {"detail": "Could not validate credentials."},
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
    json_answer: dict,
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
        assert login_response.json() == json_answer
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
        assert login_response.json() == json_answer
        assert client.cookies.get("access_token") is None
        assert client.cookies.get("refresh_token") is None


@pytest.mark.parametrize(
    "username, password, email, status_code, fail_type, json_answer",
    [
        (
            "emily",
            "password",
            "emily@example.com",
            status.HTTP_200_OK,
            RefreshFailType.NO_FAIL,
            {"release_new_access_token": "Success!"},
        ),
        (
            "jack",
            "password",
            "jack@example.com",
            status.HTTP_401_UNAUTHORIZED,
            RefreshFailType.NO_TOKEN,
            {"detail": "Token not found."},
        ),
        (
            "diana",
            "password",
            "diana@example.com",
            status.HTTP_401_UNAUTHORIZED,
            RefreshFailType.INVALID_TOKEN,
            {"detail": "Invalid token."},
        ),
    ]
)
def test_refresh_access_token(
    client: TestClient,
    username: str,
    password: str,
    email: str,
    status_code: int,
    fail_type: RefreshFailType,
    json_answer: dict,
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

    login_response = client.post(
        url=f"{settings.api.prefix_v1}/login/",
        data={
            "username": username,
            "password": password,
        }
    )
    assert login_response.status_code == status.HTTP_200_OK

    old_token = client.cookies.get("access_token")
    assert old_token is not None

    if fail_type == RefreshFailType.NO_FAIL:
        time.sleep(1)
        refresh_response = client.post(
            url=f"{settings.api.prefix_v1}/refresh/",
        )
        assert refresh_response.status_code == status_code
        assert refresh_response.json() == json_answer

        new_token = client.cookies.get("access_token")
        assert new_token is not None
        assert new_token != old_token

    else:
        if fail_type == RefreshFailType.NO_TOKEN:
            client.cookies.pop("refresh_token")
        elif fail_type == RefreshFailType.INVALID_TOKEN:
            client.cookies.update({"refresh_token": "abcde"})

        refresh_response = client.post(
            url=f"{settings.api.prefix_v1}/refresh/",
        )
        assert refresh_response.status_code == status_code
        assert refresh_response.json() == json_answer
