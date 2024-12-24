from flaskr.db_tables import UserCredentials

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from argon2 import PasswordHasher, Type

import os
import base64


passwordHasher = PasswordHasher(time_cost=6, memory_cost=65536, type=Type.ID)


def valid_login(usermail: str, *, password=None, passHash=None) -> UserCredentials:
    """
    Check if the provided login information make for a successful login.

    Parameters
    ----------
    usermail : str
        Email of the user.
    password : str, optional
        Password of the user.
    passHash : str, optional
        Hash of the password. From Argon2 ID using user's salt.

    Returns
    -------
    UserCredentials : logged-in user

    Raises
    ------
    TypeError
        If the user is not registered.
    ValueError
        If the password is invalid.
    """
    sql_db: SQLAlchemy = current_app.db
    usermail = usermail.lower()

    # Get the user's salt from the database
    user = sql_db.session.query(UserCredentials).filter_by(email=usermail).first()
    print(f"{user=}")
    if user is None:  # User not found
        raise TypeError("User is not registered")

    print(f"{password=}, {passHash=}")
    if passHash is None:
        # Calculate the hash of the password
        # with Argon2
        decoded_salt = base64.b64decode(user.salt)
        passHash = passwordHasher.hash(
            password, salt=decoded_salt
        )
        print(f"{passHash}, {decoded_salt=}")

    print(f"{user.passhash=}, {passHash=}")
    # Check if the passHashes coincide
    print(f"{check_password_hash(user.passhash, passHash)=}")
    if not check_password_hash(user.passhash, passHash):
        raise ValueError("Invalid password")
    else:
        return user


def register_user(
    usermail: str, username: str, *, password: str = None, passHash=None, salt=None
) -> None:
    """
    Register a user in the database.

    Either provide a password or a passHash and its salt.

    Parameters
    ----------
    usermail : str
        Email of the user.
    password : str, optional
        Password of the user.
    passHash : str, optional
        Hash of the password.
    salt : str, optional
        Salt used to hash the password.

    Raises
    ------
    ValueError
        If the user already exists.
    AssertionError
        If both password and (passHash or salt) is provided.
    """
    sql_db: SQLAlchemy = current_app.db
    usermail = usermail.lower()

    # Check if the user already exists
    if (
        sql_db.session.query(UserCredentials).filter_by(email=usermail).first()
        is not None
    ):
        raise ValueError("User already exists")

    # If the password is provided, create a salt and hash it
    if password:
        assert (
            passHash is None
        ), "Either password or passHash must be provided, not both."
        assert (
            salt is None
        ), "Do not provide 'salt'. It is created by the server if password is provided."
        # Create random salt
        salt = os.urandom(16)  # 16 bytes
        # Calculate the hash of the password
        # with Argon2
        passHash = passwordHasher.hash(password, salt=salt)
        # Encode the salt in base64
        print(f"Provided password, {salt=}")
        salt = base64.b64encode(salt).decode("utf-8")
    elif passHash and salt:
        pass
    else:
        assert False, "Either password or (passHash and salt) must be provided"

    # Create the user
    new_user = UserCredentials(
        username=username,
        email=usermail,
        passhash=generate_password_hash(passHash),
        salt=salt,
    )
    print(f"{passHash=}, {salt=}")
    sql_db.session.add(new_user)
    sql_db.session.commit()
