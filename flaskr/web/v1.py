from flaskr.web import web_bp
from flaskr.db_tables import UserCredentials, SessionFiles
from flaskr.common import CredentialsValidator

from flask import render_template, request, redirect, url_for, session, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
from argon2 import PasswordHasher, Type
# import folium

import os


@web_bp.route("/", methods=["GET"])
def index():
    """
    Index page
    """
    return render_template("index.html")


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    This function handles the login page
    """
    # Check if the user is already logged in
    if "user_id" in session:
        return redirect(url_for("web.profile"))

    if request.method == "GET":  # On GET request, return the login page
        return render_template("login.html")
    elif request.method == "POST":  # On POST request, check if the user is valid
        # Get credentials from the form
        email = request.form["email"]
        password = request.form["password"]

        # access db property of the app
        sql_db: SQLAlchemy = current_app.db

        # Check if the user exists
        user = sql_db.session.query(UserCredentials).filter_by(email=email).first()

        # If the user does not exist, return an error
        if user is None:
            return render_template("login.html", error="Usuario no registrado")

        # If the user exists, hash the password with user's salt
        ph = PasswordHasher(time_cost=6, memory_cost=65536, type=Type.I)
        passhash = ph.hash(password, salt=user.salt)

        # Check if the password is correct
        if passhash != user.passhash:
            return render_template("login.html", error="Contraseña incorrecta")

        # If the password is correct, log the user in
        session["usermail"] = user.email  # TODO: may consider JWT instead

        return redirect(url_for("web.profile"))


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
        return redirect(url_for("web.profile"))

    if request.method == "GET":  # On GET request, return the register page
        return render_template("signup.html")
    elif request.method == "POST":  # On POST request, register the user
        # Get credentials from the form
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]

        # Validate credentials
        if not CredentialsValidator.validate_email(email):
            return render_template("signup.html", error="Email inválido")

        if not CredentialsValidator.validate_password(password):
            return render_template("signup.html", error="Contraseña inválida")

        if not CredentialsValidator.validate_username(username):
            return render_template("signup.html", error="Nombre de usuario inválido")

        # access db property of the app
        sql_db: SQLAlchemy = current_app.db

        # Check if the user already exists
        user = sql_db.session.query(UserCredentials).filter_by(email=email).first()
        if user is not None:
            return render_template("signup.html", error="Email ya registrado")

        # create random salt
        salt = os.urandom(16)  # 16 bytes

        # Hash the password
        ph = PasswordHasher(time_cost=6, memory_cost=65536, type=Type.I)
        passhash = ph.hash(password, salt=salt)

        # Add the user to the database
        new_user = UserCredentials(
            email=email, passhash=passhash, username=username, salt=salt
        )

        # add the new user to the database
        sql_db.session.add(new_user)
        sql_db.session.commit()

        # Log the user in
        session["usermail"] = email

        # Redirect to the profile page
        return redirect(url_for("web.profile"))


@web_bp.route("/profile", methods=["GET"])
def profile():
    """
    Profile page of the user
    """
    # Check if the user is logged in
    if "usermail" not in session:
        return redirect(url_for("web.login"))

    # access db property of the app
    sql_db: SQLAlchemy = current_app.db

    # Get the user's files
    user = (
        sql_db.session.query(UserCredentials)
        .filter_by(email=session["usermail"])
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
        return redirect(url_for("web.login"))

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
