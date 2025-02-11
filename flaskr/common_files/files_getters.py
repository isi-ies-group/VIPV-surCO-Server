from flaskr.db_tables import SessionFiles, UserCredentials

from flask import current_app

import sqlalchemy


def get_file_for_user_by_name(
    user: UserCredentials, filename: str
) -> SessionFiles | None:
    """
    Get the file for a user by file id.

    Parameters
    ----------
    user : UserCredentials
        User to get the file.
    filename : str
        Name of the file.

    Returns
    -------
    SessionFiles
        File for the user.
    """
    try:
        with current_app.Session() as sql_db:
            # get the file
            file = (
                sql_db.query(SessionFiles)
                .filter_by(user_id=user.id, filename=filename)
                .first()
            )
    except sqlalchemy.exc.SQLAlchemyError:
        return None

    return file


def get_files_for_user(user: UserCredentials) -> list[SessionFiles]:
    """
    Get the files for a user.

    Parameters
    ----------
    user : UserCredentials
        User to get the files.

    Returns
    -------
    list[SessionFiles]
        List of files for the user.
    """
    try:
        with current_app.Session() as sql_db:
            # get the files
            files = sql_db.query(SessionFiles).filter_by(user_id=user.id).all()
    except sqlalchemy.exc.SQLAlchemyError:
        return []

    return files


def get_number_of_files_for_user(user: UserCredentials) -> int:
    """
    Get the number of files for a user.

    Parameters
    ----------
    user : UserCredentials
        User to get the number of files.

    Returns
    -------
    int
        Number of files for the user.
    """
    try:
        with current_app.Session() as sql_db:
            # get the number of files
            number_of_files = (
                sql_db.query(SessionFiles).filter_by(user_id=user.id).count()
            )
    except sqlalchemy.exc.SQLAlchemyError:
        return 0

    return number_of_files
