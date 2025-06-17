from flaskr.common_user.user_login_signin import salt_and_hash_password
import requests


def test_register_user(api_base, registered_user):
    """
    Test the user registration endpoint.
    This function will simulate a user registration process.
    """
    # User credentials
    usermail = registered_user["email"]
    password = registered_user["password"]

    salt, hash = salt_and_hash_password(password)

    # Step 1: Register user
    register_url = f"{api_base}/register"
    register_data = {
        "email": usermail,
        "username": usermail.split("@")[0],  # Use the part before '@' as username
        "passHash": hash,
        "passSalt": salt,
    }

    response = requests.post(register_url, json=register_data)

    assert response.status_code == 201, f"Registration failed: {response.text}"
