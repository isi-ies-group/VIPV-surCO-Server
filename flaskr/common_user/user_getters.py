from flaskr.db_tables import UserCredentials

from flask import current_app
import sqlalchemy


def get_user_by_email(usermail: str) -> UserCredentials | None:
    """
    Get a user by email.

    Parameters
    ----------
    usermail : str
        Email of the user.

    Returns
    -------
    UserCredentials | None
        User with the email provided. ``None`` if not found.
    """
    usermail = usermail.lower()

    try:
        with current_app.Session() as sql_db:
            # get the user
            user = sql_db.query(UserCredentials).filter_by(email=usermail).first()
    except sqlalchemy.exc.SQLAlchemyError:
        return None

    return user


def get_user_by_id(user_id: int) -> UserCredentials | None:
    """
    Get a user by id.

    Parameters
    ----------
    user_id : int
        Id of the user.

    Returns
    -------
    UserCredentials | None
        User with the id provided. ``None`` if not found.
    """
    try:
        with current_app.Session() as sql_db:
            # get the user
            user = sql_db.query(UserCredentials).filter_by(id=user_id).first()
    except sqlalchemy.exc.SQLAlchemyError:
        return None

    return user
