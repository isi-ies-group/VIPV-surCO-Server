from flaskr.db_tables import SessionFiles
from flaskr.common_user import (
    CredentialsValidator,
    valid_login,
    register_user,
    get_user_by_email,
)
from flaskr.common_files import (
    get_sessions_dir_for_user,
)

from flask.blueprints import Blueprint
from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import json
import time


# Create a Blueprint for the API
v1_bp = Blueprint("api", __name__)


@v1_bp.route("/up", methods=["GET"])
def up():
    """
    Check if the API is up.

    Response data
    -------------
    {
        "message": "API v1 is up",
        "privacy_policy_last_updated": "string",
        "client_build_number_minimal": int,
        "client_build_number_deprecated": int


    Returns
    -------
    200: API is up
    """
    return jsonify(
        {
            "message": "API v1 is up",
            "privacy_policy_last_updated": current_app.config["PRIVACY_POLICY"][
                "last-updated"
            ],
            "client_build_number_minimal": current_app.config[
                "CLIENT_BUILD_NUMBER_MINIMAL"
            ],
            "client_build_number_deprecated": current_app.config[
                "CLIENT_BUILD_NUMBER_DEPRECATED"
            ],
        }
    ), 200


@v1_bp.route("/salt", methods=["GET"])
def salt():
    """
    Get the salt for a user by email.

    Request data
    ------------
    {
        "email": "string"
    }

    Response data
    -------------
    {
        "passSalt": "string"
    }

    Returns
    -------
    200: Salt found
    400: email field is required
    404: User not found
    """
    data = request.headers
    email = data.get("email")

    if not email:
        return jsonify({"message": "email is required"}), 400

    user = get_user_by_email(email)

    if not user:
        time.sleep(1.5)
        return jsonify({"message": "User not found"}), 404

    return jsonify({"passSalt": user.salt}), 200


@v1_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Request data
    ------------
    {
        "email": "string",
        "passHash": "string",
        "passSalt": "string",
        "username": "string",
    }

    Returns
    -------
    201: User registered successfully
    400: All fields are required
    409: Email already registered
    """
    data = request.get_json()
    username = data.get("username")
    passhash = data.get("passHash")
    salt = data.get("passSalt")
    email = data.get("email")

    if not username or not passhash or not salt or not email:
        return jsonify({"message": "All fields are required"}), 400

    # validate fields
    if not (
        CredentialsValidator.validate_username(username)
        and CredentialsValidator.validate_email(email)
    ):
        return jsonify({"message": "Invalid fields"}), 400

    # register the user
    try:
        register_user(
            usermail=email,
            username=username,
            passHash=passhash,
            salt=salt,
        )
    except ValueError:
        return jsonify({"message": "Email already registered"}), 409

    return jsonify({"message": "User registered successfully"}), 201


@v1_bp.route("/login", methods=["POST"])
def login():
    """
    Returns a token for the user if the credentials are correct.
    This token is valid for JWT_ACCESS_TOKEN_EXPIRES [seconds] and is used to
    authenticate the user.

    Request data
    ------------
    {
        "email": "string",
        "passHash": "string",
        "app_build_number": "string"
    }

    Returns
    -------
    200: Access token returned successfully:

        {
            "username": "string",
            "access_token": "string",
            "validity": int,
            "deprecated_client": bool  # True if the client is deprecated
        }

    400: All fields are required
    401: Incorrect password
    404: User not found
    426: Client version too old
    """
    data = request.get_json()
    email = data.get("email")
    passhash = data.get("passHash")
    app_build_number = int(data.get("app_build_number"))

    if not email or not passhash:
        return jsonify({"message": "All fields are required"}), 400

    if app_build_number < current_app.config["CLIENT_BUILD_NUMBER_MINIMAL"]:
        return jsonify(
            {
                "message": "Client version too old. "
                + f"Minimum required version is {current_app.config['CLIENT_BUILD_NUMBER_MINIMAL']}."  # noqa: E501
            }
        ), 426
    client_is_deprecated = (
        app_build_number <= current_app.config["CLIENT_BUILD_NUMBER_DEPRECATED"]
    )

    try:
        user = valid_login(email, passHash=passhash)
    except TypeError:
        return jsonify({"message": "User not found"}), 404
    except ValueError:
        return jsonify({"message": "Incorrect password"}), 401

    # create a random unique token for the user
    access_token = create_access_token(identity=user.email, fresh=True)

    return jsonify(
        {
            "username": user.username,
            "access_token": access_token,
            "validity": current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds(),
            "deprecated_client": client_is_deprecated,
        }
    ), 200


@v1_bp.route("/session/upload", methods=["POST"])
@jwt_required()
def upload_session_file():
    """
    Upload a file to the server.
    This endpoint should be used with Content-Type: multipart/form-data.
    """
    email_identity = get_jwt_identity()

    user = get_user_by_email(email_identity)

    if not user:
        return jsonify({"message": "User not found"}), 401

    files_in_form = request.files
    if (len_files := len(files_in_form)) != 1:
        if len_files == 0:
            return jsonify({"message": "File is required"}), 400
        else:  # len_files > 1
            return jsonify({"message": "Only one file is allowed at the moment"}), 400

    filename: str
    content: FileStorage
    for _, content in files_in_form.items():
        filename = content.filename
        content = content.read().decode("utf-8")
        # ensure secure filename
        filename = secure_filename(filename)

        # save the file to the server in the instance/sessions/<user-id> folder
        # and save the filename to the database
        user_sessions_dir = get_sessions_dir_for_user(user)
        user_sessions_dir.mkdir(parents=True, exist_ok=True)
        filepath = user_sessions_dir / filename

        if filepath.exists():
            return jsonify({"message": "File already exists"}), 409

        with open(filepath, "w") as f:
            f.write(content)

        # save the filename to the database
        new_file = SessionFiles(user.id, filename)
        with current_app.Session() as sql_db:
            sql_db.add(new_file)
            sql_db.commit()

        return jsonify({"message": "Session file uploaded successfully"}), 201


@v1_bp.route("/privacy-policy", methods=["GET"])
def privacy_policy():
    """
    Get the privacy policy text in the requested language.

    Query parameters
    ----------------
    lang: str (optional, default: "en")
        The language code for the privacy policy text. Supported languages are
        defined in the app configuration.

    Response data
    -------------
    {
        "content": "string",
        "last_updated": "string",
        "language": "string"
    }
    """
    language = request.args.get("lang", "en")

    if language not in current_app.config["PRIVACY_POLICY"]["texts"]:
        language = "en"  # Fallback to English

    content = current_app.config["PRIVACY_POLICY"]["texts"][language]
    last_updated = current_app.config["PRIVACY_POLICY"]["last-updated"]

    return jsonify(
        {"content": content, "last_updated": last_updated, "language": language}
    ), 200
