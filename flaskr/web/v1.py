from flaskr.web import web_bp
from flaskr.db_tables import UserCredentials, SessionFiles
from flaskr.common import CredentialsValidator

from flask import render_template, request, redirect, url_for, session
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
        return redirect(url_for("profile"))

    if request.method == "GET":  # On GET request, return the login page
        return render_template("login.html")
    elif request.method == "POST":  # On POST request, check if the user is valid
        # Get credentials from the form
        email = request.form["email"]
        password = request.form["password"]

        # Check if the user exists
        user = UserCredentials.query.filter_by(email=email).first()

        # If the user does not exist, return an error
        if user is None:
            return render_template("login.html", error="Usuario no registrado")

        # If the user exists, hash the password with user's salt
        ph = PasswordHasher(time_cost=6, memory_cost=65536, type=Type.I)
        passhash = ph.hash(password, salt=user.salt)

        # Check if the password is correct
        if not check_password_hash(passhash, user.password):
            return render_template("login.html", error="Contraseña incorrecta")

        # If the password is correct, log the user in
        session["usermail"] = user.email  # TODO: may consider JWT instead

        return redirect(url_for("profile"))


@web_bp.route("/logout", methods=["GET"])
def logout():
    """
    Logout to landing page
    """
    # Check if the user is logged in
    if "usermail" not in session:
        return redirect(url_for("/"))

    # Log the user out
    session.pop("usermail")

    return redirect(url_for("/"))


@web_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Register a new user
    """
    # Check if the user is already logged in
    if "usermail" in session:
        return redirect(url_for("profile"))

    if request.method == "GET":  # On GET request, return the register page
        return render_template("singup.html")
    elif request.method == "POST":  # On POST request, register the user
        # Get credentials from the form
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]

        # Validate credentials
        if not CredentialsValidator.validate_email(email):
            return render_template("singup.html", error="Email inválido")

        if not CredentialsValidator.validate_password(password):
            return render_template("singup.html", error="Contraseña inválida")

        if not CredentialsValidator.validate_username(username):
            return render_template("singup.html", error="Nombre de usuario inválido")

        # Check if the user already exists
        user = UserCredentials.query.filter_by(email=email).first()
        if user is not None:
            return render_template("singup.html", error="Email ya registrado")

        # create random salt
        salt = os.urandom(size=16)

        # Hash the password
        ph = PasswordHasher(time_cost=6, memory_cost=65536, type=Type.I)
        passhash = ph.hash(password, salt=salt)

        # Add the user to the database
        new_user = UserCredentials(
            email=email, password=passhash, username=username, salt=salt
        )
        new_user.save()

        # Log the user in
        session["usermail"] = email


@web_bp.route("/profile", methods=["GET"])
def profile():
    """
    Profile page of the user
    """
    # Check if the user is logged in
    if "usermail" not in session:
        return redirect(url_for("login"))

    # Get the user's files
    user = UserCredentials.query.filter_by(email=session["usermail"]).first()
    n_files = SessionFiles.query.filter_by(user_id=user.id).count()

    # TODO: add files to the template
    return render_template("profile.html", n_files=n_files)


'''  # TODO: use folium to show a map of the user's routes
@web_bp.route("/profile/map", methods=["GET"])
def map():
    """
    Map page of the user
    """
    # Check if the user is logged in
    if "usermail" not in session:
        return redirect(url_for("login"))

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
