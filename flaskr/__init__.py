from flask import (
    Flask,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash,
    get_flashed_messages,
)

from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import JWTManager, unset_jwt_cookies
from pathlib import Path
import os
import json

from flaskr.db_tables import (
    Base,
    UserCredentials,
    SessionFiles,
    UserClientInfo,
)
from flaskr.env_config import (
    SECRET_KEY,
    JWT_SECRET_KEY,
    DATABASE_URI,
    CLIENT_BUILD_NUMBER_MINIMAL,
    CLIENT_BUILD_NUMBER_DEPRECATED,
)
from flaskr import api
from flaskr import web

from datetime import timedelta


def create_app(test_config=None):
    # # Initialization of the instance
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,  # secret key for sessions
        JWT_SECRET_KEY=JWT_SECRET_KEY,  # secret key to sign JWT tokens
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),  # token expiration time
        JWT_TOKEN_LOCATION=["headers", "cookies"],  # where to find the token
        SQLALCHEMY_DATABASE_URI=DATABASE_URI,  # database URI
        # least session version number accepted
        CLIENT_BUILD_NUMBER_MINIMAL=int(CLIENT_BUILD_NUMBER_MINIMAL),
        CLIENT_BUILD_NUMBER_DEPRECATED=int(CLIENT_BUILD_NUMBER_DEPRECATED),
    )

    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path, exist_ok=True)

    # configuration
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["JWT_COOKIE_SECURE"] = app.config["SECRET_KEY"] != "dev"

    # resources & config created on startup
    # privacy policy populated versions and last-updated date
    privacy_policy_path = (
        Path(app.root_path) / app.template_folder / "privacy-policy"
    )
    with (
        (privacy_policy_path / "privacy-policy-conf.json")
        .resolve()
        .open("r", encoding="utf-8") as privacy_policy_file
    ):
        privacy_policy_json = json.load(privacy_policy_file)
    with app.app_context():
        app.config["PRIVACY_POLICY"] = {
            "last-updated": privacy_policy_json["last-updated"],
            "texts": {
                lang_id: render_template(
                    f"privacy-policy/privacy-policy-{lang_id}.jinja2",
                    last_updated=privacy_policy_json["last-updated"],
                )
                for lang_id in privacy_policy_json["available-languages"]
            },
        }
    del privacy_policy_json
    del privacy_policy_path

    # required to use Google OAuth
    # app.config["GOOGLE_ID"] = GOOGLE_ID
    # app.config["GOOGLE_SECRET"] = GOOGLE_SECRET

    # # Initialization of extensions
    # database initialization
    with app.app_context():
        # ASSERT ALL MODELS ARE IMPORTED BEFORE CREATING ALL:
        # If you define models in submodules, you must import them so that SQLAlchemy
        # knows about them before calling create_all.
        assert Base
        assert UserCredentials
        assert SessionFiles
        assert UserClientInfo
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        Base.metadata.create_all(engine)
        app.Session = sessionmaker(bind=engine)

    # JWT manager
    app.jwt = JWTManager(app)

    # session for browsers
    Session(app)

    # # Blueprints with their routes
    # App client API
    app.register_blueprint(api.v1_bp, url_prefix="/api/v1")
    # Web interface
    app.register_blueprint(web.web_bp, url_prefix="/")

    @app.jwt.expired_token_loader
    def expired_jwt_token_callback(jwt_header, jwt_payload):
        response = redirect("/login")
        unset_jwt_cookies(response)
        return response

    # # Routes
    @app.route("/admin", methods=["GET", "POST"])  # Pagina de administrador
    def admin():
        if "authenticated" in session:
            # El usuario ya está autenticado, mostrar la página admin
            mensajes = get_flashed_messages(with_categories=True)
            return render_template("admin.html", mensajes=mensajes)
        else:
            # El usuario no está autenticado, verificar la contraseña
            if request.method == "POST":
                password = request.form["password"]
                if password == SECRET_KEY:  # TODO: change to a different password
                    session["authenticated"] = True
                    return redirect(url_for("admin"))
                else:
                    flash("Contraseña incorrecta", "error")
        return render_template("admin.html")

    return app  # Return the app instance (end of create_app factory function)
