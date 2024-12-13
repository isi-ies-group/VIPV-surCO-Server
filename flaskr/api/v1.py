from flaskr.api import api_bp
from flaskr.db_tables import UserCredentials, SessionFiles

from flask import request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from pathlib import Path


@api_bp.route("/salt", methods=["GET"])
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
    # access db property of the app
    sql_db: SQLAlchemy = current_app.db

    data = request.headers
    email = data.get("email")

    if not email:
        return jsonify({"message": "email is required"}), 400

    # get the salt for the user
    user = sql_db.session.query(UserCredentials).filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({"passSalt": user.salt}), 200


@api_bp.route("/register", methods=["POST"])
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

    # find if the user already exists by username
    user = current_app.db.session.query(UserCredentials).filter_by(email=email).first()
    if user:
        return jsonify({"message": "Email already registered"}), 409

    # create a new user
    new_user = UserCredentials(
        username=username,
        email=email,
        passhash=generate_password_hash(passhash),
        salt=salt,
    )

    # add the new user to the database
    current_app.db.session.add(new_user)
    current_app.db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@api_bp.route("/login", methods=["POST"])
def login():
    """
    Returns a token for the user if the credentials are correct.
    This token is valid for JWT_ACCESS_TOKEN_EXPIRES and is used to
    authenticate the user. Validity is in seconds.

    Request data
    ------------
    {
        "email": "string",
        "passHash": "string"
    }

    Returns
    -------
    200: Access token returned successfully:

        {
            "username": "string",
            "access_token": "string",
            "validity": int
        }

    400: All fields are required
    401: Incorrect password
    404: User not found
    """
    data = request.get_json()
    email = data.get("email")
    passhash = data.get("passHash")

    if not email or not passhash:
        return jsonify({"message": "All fields are required"}), 400

    # find the user by email
    user: UserCredentials = (
        current_app.db.session.query(UserCredentials).filter_by(email=email).first()
    )

    if not user:
        return jsonify({"message": "User not found"}), 404

    # check if the passhash is correct
    if check_password_hash(user.passhash, passhash):
        return jsonify({"message": "Incorrect password"}), 401

    # create a random unique token for the user
    access_token = create_access_token(identity=email, fresh=True)

    return jsonify(
        {
            "username": user.username,
            "access_token": access_token,
            "validity": current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds(),
        }
    ), 200


@api_bp.route("/session/upload", methods=["POST"])
@jwt_required()
def upload_session_file():
    """
    Upload a file to the server.
    This endpoint should be used with Content-Type: multipart/form-data.
    """
    email_identity = get_jwt_identity()
    user: UserCredentials = (
        current_app.db.session.query(UserCredentials)
        .filter_by(email=email_identity)
        .first()
    )

    if not user:
        return jsonify({"message": "User not found"}), 400

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
        user_sessions_dir = Path(current_app.instance_path) / "sessions" / str(user.id)
        user_sessions_dir.mkdir(parents=True, exist_ok=True)
        filepath = user_sessions_dir / filename

        if filepath.exists():
            return jsonify({"message": "File already exists"}), 409

        with open(filepath, "w") as f:
            f.write(content)

        # save the filename to the database
        new_file = SessionFiles(user.id, filename)
        current_app.db.session.add(new_file)
        current_app.db.session.commit()

        return jsonify({"message": "Session file uploaded successfully"}), 201
