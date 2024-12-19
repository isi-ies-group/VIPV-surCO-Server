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
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os

from flaskr.db_tables import (
    Base,
    UserCredentials,
    SessionFiles,
)
from flaskr.claves import claveTokens, GOOGLE_ID, GOOGLE_SECRET, admin_pass
from flaskr import api
from flaskr import web

from datetime import timedelta


def create_app(test_config=None):
    # # Initialization of the instance
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
        JWT_SECRET_KEY=claveTokens,  # secret key to sign JWT -- secrets.token_hex(32)
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),  # token expiration time
        SQLALCHEMY_DATABASE_URI=(
            "sqlite:///VIPV_Data_Crowdsourcing_Program.sqlite"
        ),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # configuration
    UPLOAD_FOLDER = "static/datosFoto/"  # Para guardar las imagenes enviadas

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["PFP_UPLOAD_FOLDER"] = (
        "static/userpfp/"  # Para almacenar las imagenes de perfil
    )

    # required to use Google OAuth
    app.config["GOOGLE_ID"] = GOOGLE_ID
    app.config["GOOGLE_SECRET"] = GOOGLE_SECRET

    # # Initialization of extensions
    # database initialization
    app.db = SQLAlchemy(app, model_class=Base)
    with app.app_context():
        # ASSERT ALL MODELS ARE IMPORTED BEFORE CREATING ALL:
        # If you define models in submodules, you must import them so that SQLAlchemy
        # knows about them before calling create_all.
        assert UserCredentials
        assert SessionFiles
        app.db.create_all()

    # JWT manager
    app.jwt = JWTManager(app)

    # session for browsers
    Session(app)

    # # Blueprints with their routes
    # App client API
    app.register_blueprint(api.v1_bp, url_prefix="/api/v1")
    # Web interface
    app.register_blueprint(web.web_bp, url_prefix="/")

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
                if password == admin_pass:
                    session["authenticated"] = True
                    return redirect(url_for("admin"))
                else:
                    flash("Contraseña incorrecta", "error")
        return render_template("admin.html")

    return app  # Return the app instance (end of create_app factory function)
