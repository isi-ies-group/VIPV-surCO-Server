import pytest
from flaskr import create_app
from flaskr.db_tables import UserCredentials
from flaskr.common_user.user_login_signin import register_user

import os
import sys

# Modify the path to include the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def registered_user() -> dict[str, str]:
    """
    Fixture to provide a registered user for testing.
    To be used in tests that require existing user credentials,
    username, email and password.
    """
    return {
        "username": "reg_uname",
        "email": "reg_uname@email.com",
        "password": "reg_uname_password",
    }


@pytest.fixture(scope="session")
def unregistered_user() -> dict[str, str]:
    """
    Fixture to provide an unregistered user for testing.
    To be used in tests that require non-existing user credentials,
    username, email and password.
    """
    return {
        "username": "unreg_uname",
        "email": "unreg_uname@email.com",
        "password": "unreg_uname_password",
    }


@pytest.fixture()
def app(registered_user, unregistered_user):
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here
    with app.app_context():
        # Initialize the database or any other resources needed for testing
        try:
            register_user(
                usermail=registered_user["email"],
                username=registered_user["username"],
                password=registered_user["password"],
            )
        except ValueError as e:
            # If the user already exists, we can ignore this error
            if e.args[0] != "User already exists":
                raise e

    yield app

    # clean up / reset resources here
    # remove the registered user after tests
    with app.app_context():
        with app.Session() as sql_db:
            for user_data in (registered_user, unregistered_user):
                # Remove the user from the database
                user = (
                    sql_db.query(UserCredentials)
                    .filter_by(email=user_data["email"])
                    .first()
                )
                if user:
                    sql_db.delete(user)
                    sql_db.commit()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
