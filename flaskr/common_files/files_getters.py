from flaskr.db_tables import SessionFiles, UserCredentials

from flask import current_app

import sqlalchemy


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
