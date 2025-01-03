try:
    import tomllib
except ImportError:
    import toml as tomllib  # type: ignore
import os

from warnings import warn


SECRETS_PATH = os.path.abspath(os.path.join(__file__, "../../secrets/secrets.toml"))

if os.path.exists(SECRETS_PATH):
    try:
        with open(SECRETS_PATH, "rb") as f:
            secrets = tomllib.load(f)
    except TypeError:
        secrets = tomllib.load(SECRETS_PATH)
    claveTokens = secrets["claveTokens"]
    admin_pass = secrets["admin_pass"]
    GOOGLE_ID = secrets["GOOGLE_ID"]
    GOOGLE_SECRET = secrets["GOOGLE_SECRET"]
else:
    claveTokens = os.environ.get("claveTokens")
    admin_pass = os.environ.get("admin_pass")
    GOOGLE_ID = os.environ.get("GOOGLE_ID")
    GOOGLE_SECRET = os.environ.get("GOOGLE_SECRET")

SECRET_KEY = os.environ.get("SECRET_KEY", default="dev")
if SECRET_KEY is None:
    # create a random secret key, for all the workers to share
    # lock for the creation of the secret key
    warn("Configuration pending: No secret key found.\n" +
         "    Set with SECRET_KEY=<key> or in secrets.toml")

DATABASE_URI = os.environ.get("DATABASE_URI", default="sqlite:///flaskr.db")
