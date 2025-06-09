from flaskr.db_tables import UserClientInfo, UserCredentials

from flask import current_app
import sqlalchemy


def set_or_update_user_client_info(
    user: UserCredentials, client_version: int,
) -> UserClientInfo:
    """
    Set or update the user client info of an user.

    Parameters
    ----------
    user : UserCredentials
        User to set the client info for.
    client_version : int
        Client version to set.

    Returns
    -------
    UserClientInfo
        The user client info object.
    """
    try:
        with current_app.Session() as sql_db:
            # check if the user client info already exists
            user_client_info = (
                sql_db.query(UserClientInfo)
                .filter_by(user_id=user.id)
                .first()
            )

            if user_client_info:
                # update the existing user client info
                user_client_info.client_build_number = client_version
            else:
                # create a new user client info
                user_client_info = UserClientInfo(
                    user_id=user.id, client_build_number=client_version
                )
                sql_db.add(user_client_info)

            sql_db.commit()

    except sqlalchemy.exc.SQLAlchemyError as e:
        current_app.logger.error(f"Error setting or updating user client info: {e}")
        raise

    return user_client_info
