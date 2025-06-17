import base64

import pytest

from flaskr.common_user import salt_and_hash_password, hash_password


@pytest.fixture(scope="module")
def api_base():
    """
    Fixture to provide the base URL for the API.
    """
    return "/api/v1"


@pytest.fixture(scope="module")
def email_non_existent():
    """
    Fixture to provide a non-existent email for testing.
    """
    return "non_existent_email@provider.ez"


def test_up(client, api_base):
    """
    Test the /up endpoint to check if the server is running.
    """
    response = client.get(api_base + "/up")
    assert response.status_code == 200
    json = response.json
    assert "message" in json
    assert "client_build_number_deprecated" in json
    assert "client_build_number_minimal" in json
    assert "privacy_policy_last_updated" in json
    assert json["message"] == "API v1 is up"


def test_salt_bad_request(client, api_base):
    """
    Test the /salt endpoint with a bad request (missing email).
    """
    response = client.get(api_base + "/salt")
    assert response.status_code == 400
    json = response.json
    assert "message" in json


def test_salt_non_existent_email(client, api_base, email_non_existent):
    """
    Test the /salt endpoint with a non-existent email.
    """
    response = client.get(api_base + "/salt", headers={"email": email_non_existent})
    assert response.status_code == 404
    json = response.json
    assert "message" in json
    assert json["message"] == "User not found"


def test_salt_existing_email(client, api_base, registered_user):
    """
    Test the /salt endpoint with an existing email.
    """
    response = client.get(
        api_base + "/salt", headers={"email": registered_user["email"]}
    )
    assert response.status_code == 200


def test_register_user(client, api_base, unregistered_user):
    """
    Test the /register endpoint to register a new user.
    """
    # lets create a random salt and hash the password
    salt, pass_hash = salt_and_hash_password(unregistered_user["password"])
    response = client.post(
        api_base + "/register",
        json={
            "username": unregistered_user["username"],
            "email": unregistered_user["email"],
            "passHash": pass_hash,
            "passSalt": salt,
        },
    )
    assert response.status_code == 201
    json = response.json
    assert "message" in json
    assert json["message"] == "User registered successfully"


def test_register_existing_user(client, api_base, registered_user):
    """
    Test the /register endpoint with an already registered user.
    """
    salt, pass_hash = salt_and_hash_password(registered_user["password"])
    response = client.post(
        api_base + "/register",
        json={
            "username": registered_user["username"],
            "email": registered_user["email"],
            "passHash": pass_hash,
            "passSalt": salt,
        },
    )
    assert response.status_code == 409
    json = response.json
    assert "message" in json
    assert json["message"] == "Email already registered"


def test_register_missing_fields(client, api_base, unregistered_user):
    """
    Test the /register endpoint with missing fields.
    """
    # lets create a random salt and hash the password
    salt, pass_hash = salt_and_hash_password(unregistered_user["password"])

    response = client.post(
        api_base + "/register",
        json={
            "username": "test_user",
            "email": "test_user@email.com",
            # "passHash" and "passSalt" fields missing
        },
    )
    assert response.status_code == 400

    response = client.post(
        api_base + "/register",
        json={
            "username": "test_user",
            "email": "test_user@email.com",
            "passSalt": salt,
            # "passHash" field missing
        },
    )
    assert response.status_code == 400

    response = client.post(
        api_base + "/register",
        json={
            "username": "test_user",
            "email": "test_user@email.com",
            "passHash": pass_hash,
            # "passSalt" field missing
        },
    )
    assert response.status_code == 400


def test_login_existing_user(client, api_base, registered_user):
    """
    Test the /login endpoint with an existing user.
    """
    # get the salt and hash the password
    response = client.get(
        api_base + "/salt", headers={"email": registered_user["email"]}
    )
    salt = response.json["passSalt"]
    decoded_salt = base64.b64decode(salt)
    pass_hash = hash_password(registered_user["password"], salt=decoded_salt)
    app_build_number = 1000000
    response = client.post(
        api_base + "/login",
        json={
            "email": registered_user["email"],
            "passHash": pass_hash,
            "app_build_number": app_build_number,
        },
    )
    assert response.status_code == 200
    json = response.json
    assert "access_token" in json


def test_login_non_existent_user(client, api_base, email_non_existent):
    """
    Test the /login endpoint with a non-existent user.
    """
    response = client.post(
        api_base + "/login",
        json={
            "email": email_non_existent,
            "passHash": "some_hash",
            "app_build_number": 1000000,
        },
    )
    assert response.status_code == 404
    json = response.json
    assert "message" in json
    assert json["message"] == "User not found"


def test_login_invalid_password(client, api_base, registered_user):
    """
    Test the /login endpoint with an existing user but invalid password.
    """
    # get the salt and hash the password
    response = client.get(
        api_base + "/salt", headers={"email": registered_user["email"]}
    )
    salt = response.json["passSalt"]
    decoded_salt = base64.b64decode(salt)

    # change the password to an invalid one
    invalid_pass_hash = hash_password("invalid_password", salt=decoded_salt)

    response = client.post(
        api_base + "/login",
        json={
            "email": registered_user["email"],
            "passHash": invalid_pass_hash,
            "app_build_number": 1000000,
        },
    )
    assert response.status_code == 401
    json = response.json
    assert "message" in json
    assert json["message"] == "Incorrect password"


def test_login_missing_fields(client, api_base, registered_user):
    """
    Test the /login endpoint with missing fields.
    """
    # get the salt and hash the password
    response = client.get(
        api_base + "/salt", headers={"email": registered_user["email"]}
    )
    salt = response.json["passSalt"]
    decoded_salt = base64.b64decode(salt)
    pass_hash = hash_password(registered_user["password"], salt=decoded_salt)

    # missing email
    response = client.post(
        api_base + "/login",
        json={
            "passHash": pass_hash,
            "app_build_number": 1000000,
        },
    )
    assert response.status_code == 400

    # missing passHash
    response = client.post(
        api_base + "/login",
        json={
            "email": registered_user["email"],
            "app_build_number": 1000000,
        },
    )
    assert response.status_code == 400

    # missing app_build_number
    response = client.post(
        api_base + "/login",
        json={
            "email": registered_user["email"],
            "passHash": pass_hash,
        },
    )
    assert response.status_code == 400


def test_login_obsolete_client_build(client, api_base, registered_user):
    """
    Test the /login endpoint with an obsolete client build number.
    """
    # get the salt and hash the password
    response = client.get(
        api_base + "/salt", headers={"email": registered_user["email"]}
    )
    salt = response.json["passSalt"]
    decoded_salt = base64.b64decode(salt)
    pass_hash = hash_password(registered_user["password"], salt=decoded_salt)

    # use an obsolete client build number
    obsolete_build_number = -1  # Example obsolete build number (default minimal is 0)
    response = client.post(
        api_base + "/login",
        json={
            "email": registered_user["email"],
            "passHash": pass_hash,
            "app_build_number": obsolete_build_number,
        },
    )
    assert response.status_code == 426
    json = response.json
    assert "message" in json
    assert "Client version too old" in json["message"]
