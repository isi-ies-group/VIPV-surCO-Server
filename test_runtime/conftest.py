import os
import sys
from pathlib import Path
import pytest


# Ensure the parent directory is in the Python path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(scope="module")
def url_base():  # Fixture to provide the base URL for the API.
    return os.environ.get("TEST_API_BASE", "http://localhost:5000").strip()


@pytest.fixture(scope="module")
def api_base(url_base):
    """
    Fixture to provide the base URL for the API.
    This can be overridden by setting the TEST_API_BASE environment variable.
    """
    return url_base + "/api/v1"


@pytest.fixture(scope="module")
def registered_user():
    """
    Fixture to provide a registered user for testing.
    This should be replaced with actual user registration logic.
    """
    usermail = os.environ.get("TEST_USER_EMAIL", "").strip()
    password = os.environ.get("TEST_USER_PASSWORD", "").strip()
    client_build_number = os.environ.get("TEST_CLIENT_BUILD_NUMBER", "").strip()
    if not usermail or not password:
        raise ValueError(
            "Test user credentials are not set in environment variables.\n"
            "Set with TEST_USER_EMAIL=… and TEST_USER_PASSWORD=…"
        )
    return {
        "email": usermail,
        "password": password,
        "username": usermail.split("@")[0],  # Use the part before '@' as username
        "client_build_number": client_build_number,
    }


@pytest.fixture(scope="session")
def data_dir():
    """
    Fixture to provide the path to the data directory.
    """
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def sessions_dir(data_dir):
    """
    Fixture to provide the path to the sessions directory.
    """
    return data_dir / "sessions"
