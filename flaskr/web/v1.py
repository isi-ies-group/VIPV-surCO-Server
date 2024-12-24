from flaskr.web import web_bp
from flaskr.db_tables import UserCredentials, SessionFiles
from flaskr.common import CredentialsValidator, user_login_and_register

from flask import (
    render_template,
    request,
    redirect,
    session,
    current_app,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
# import folium

import traceback


@web_bp.route("/", methods=["GET"])
def index():
    """
    Index page
    """
    return render_template("index.html")


@web_bp.route("/isLoggedIn", methods=["GET"])
def is_logged_in():
    """
    Check if the user is logged in
    """
    return jsonify({"result": ("usermail" in session)}), 200


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    This function handles the login page
    """
    # Check if the user is already logged in
    if "usermail" in session:
        return redirect("/profile")

    if request.method == "GET":  # On GET request, return the login page
        return render_template("login.html")
    elif request.method == "POST":  # On POST request, check if the user is valid
        # Get credentials from the form
        email = request.form["email"]
        password = request.form["password"]

        # Validate login
        try:
            user = user_login_and_register.valid_login(email, password=password)
        except ValueError:
            print(traceback.format_exc())
            return render_template("login.html", error_message="Contraseña incorrecta")
        except TypeError:
            print(traceback.format_exc())
            return render_template("login.html", error_message="Usuario no registrado")

        # If the password is correct, log the user in
        session["usermail"] = user.email.lower()  # TODO: may consider JWT instead

        return redirect("/profile")


@web_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """
    Logout to landing page
    """
    # Log the user out
    session.pop("usermail", default=None)

    # Check if the user is logged in
    if "usermail" not in session:
        return redirect("/")

    return redirect("/")


@web_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Register a new user
    """
    # Check if the user is already logged in
    if "usermail" in session:
        return redirect("/profile")

    if request.method == "GET":  # On GET request, return the register page
        return render_template("signup.html")
    elif request.method == "POST":  # On POST request, register the user
        # Get credentials from the form
        email = request.form["email"].lower()
        password = request.form["password"]
        username = request.form["username"]

        # Validate credentials
        if not CredentialsValidator.validate_email(email):
            return render_template("signup.html", error_message="Email inválido")

        if not CredentialsValidator.validate_password(password):
            return render_template("signup.html", error_message="Contraseña inválida")

        if not CredentialsValidator.validate_username(username):
            return render_template(
                "signup.html", error_message="Nombre de usuario inválido"
            )

        # Create the user
        try:
            user_login_and_register.register_user(
                usermail=email, username=username, password=password
            )
        except ValueError:
            return render_template("signup.html", error_message="Email ya registrado")

        # Log the user in
        session["usermail"] = email

        # Redirect to the profile page
        return redirect("/profile")


@web_bp.route("/profile", methods=["GET"])
def profile():
    """
    Profile page of the user
    """
    # Check if the user is logged in
    if "usermail" not in session:
        return redirect("/login")

    # access db property of the app
    sql_db: SQLAlchemy = current_app.db

    # Get the user's files
    user = (
        sql_db.session.query(UserCredentials)
        .filter_by(email=session["usermail"].lower())
        .first()
    )
    n_files = sql_db.session.query(SessionFiles).filter_by(user_id=user.id).count()

    # TODO: add files to the template
    return render_template("profile.html", user=user, n_files=n_files)


'''  # TODO: use folium to show a map of the user's routes
@web_bp.route("/profile/map", methods=["GET"])
def map():
    """
    Map page of the user
    """
    # Check if the user is logged in
    if "usermail" not in session:
        return redirect("/login")

    return render_template("map.html")
'''


@web_bp.route("/about", methods=["GET"])
def about():
    """
    About page
    """
    return render_template("about.html")


@web_bp.route("/contact", methods=["GET"])
def contact():
    """
    Contact page
    """
    return render_template("contact.html")
