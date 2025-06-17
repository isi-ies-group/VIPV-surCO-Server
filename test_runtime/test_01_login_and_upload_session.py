import base64

import requests
import pytest

from flaskr.common_user.user_login_signin import hash_password


@pytest.fixture(scope="module")
def registered_user_salt(api_base, registered_user):
    """
    Fixture to provide the salt for a registered user.
    This should be replaced with actual logic to retrieve the user's salt.
    """

    # Simulate getting salt from the API
    salt_url = f"{api_base}/salt"
    response = requests.get(salt_url, headers={"email": registered_user["email"]})
    if response.status_code != 200:
        raise RuntimeError("Failed to get salt for registered user.")

    return response.json().get("passSalt")


@pytest.mark.parametrize(
    "session_file",
    [
        pytest.param(
            "VIPV_2025-06-06T06_42_37.544229Z-2025-06-06T15_06_31.891352Z_light.txt",
            id="light_file",
        ),
        pytest.param(
            "VIPV_2025-06-06T06_42_37.544229Z-2025-06-06T15_06_31.891352Z.txt",
            id="4mb_file",
        ),
    ],
)
def test_login_and_upload_session(
    api_base, registered_user, registered_user_salt, sessions_dir, session_file
):
    """
    Test the login and file upload functionality.
    This function will simulate a user login and file upload process.
    """
    session_file = sessions_dir / session_file
    if not session_file.exists():
        raise FileNotFoundError(f"Session file {session_file} does not exist.")

    # user credentials
    usermail = registered_user["email"]
    password = registered_user["password"]

    # Step 1: Get salt for the user
    salt = registered_user_salt
    decoded_salt = base64.b64decode(salt)

    # Step 2: Login
    login_url = f"{api_base}/login"
    login_data = {
        "email": usermail,
        "passHash": hash_password(password, salt=decoded_salt),
        "app_build_number": registered_user["client_build_number"],
    }
    login_response = requests.post(login_url, json=login_data)
    if login_response.status_code != 200:
        raise Exception(
            f"Login failed: {login_response.json().get('message', 'Unknown error')}"
        )
    login_json = login_response.json()
    access_token = login_json.get("access_token")
    if not access_token:
        raise Exception("Access token not received from login response.")

    # Step 3: Upload session file
    upload_url = f"{api_base}/session/upload"
    headers = {"Authorization": f"Bearer {access_token}"}
    with session_file.open("rb") as file:
        files = {"file": (session_file.name, file)}
        upload_response = requests.post(upload_url, headers=headers, files=files)
        assert upload_response.status_code == 201, (
            f"Failed to upload {session_file.name}"
            f"[Size: {session_file.stat().st_size} bytes]"
        )
