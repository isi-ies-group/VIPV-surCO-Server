import tomllib
import os


SECRETS_PATH = os.path.abspath(os.path.join(__file__, "../../secrets/secrets.toml"))

if os.path.exists(SECRETS_PATH):
    with open(SECRETS_PATH, "rb") as f:
        secrets = tomllib.load(f)
    claveTokens = secrets["claveTokens"]
    admin_pass = secrets["admin_pass"]
    GOOGLE_ID = secrets["GOOGLE_ID"]
    GOOGLE_SECRET = secrets["GOOGLE_SECRET"]
else:
    claveTokens = os.environ.get("claveTokens")
    admin_pass =  os.environ.get("admin_pass")
    GOOGLE_ID = os.environ.get("GOOGLE_ID")
    GOOGLE_SECRET = os.environ.get("GOOGLE_SECRET")
