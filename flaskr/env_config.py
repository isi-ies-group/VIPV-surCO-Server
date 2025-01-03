# usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loads the configuration from the environment variables.
"""

import os
from warnings import warn

# Secret key for the Flask app, used to sign cookies and sessions
SECRET_KEY = os.environ.get("SECRET_KEY", default=None)
if SECRET_KEY is None:
    warn(
        "Configuration pending: No secret key found.\n"
        + "    Set with SECRET_KEY=<key>"
    )
    SECRET_KEY = "dev"

# Secret key for the JWT tokens
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", default=None)
if JWT_SECRET_KEY is None:
    # create a random secret key, for all the workers to share
    # lock for the creation of the secret key
    warn(
        "Configuration pending: No JWT secret key found.\n"
        + "    Set with JWT_SECRET_KEY=<key>"
    )
    JWT_SECRET_KEY = "dev"

if (
    (POSTGRES_DB := os.environ.get("POSTGRES_DB"))
    and (POSTGRES_USER := os.environ.get("POSTGRES_USER"))
    and (POSTGRES_PASSWORD := os.environ.get("POSTGRES_PASSWORD"))
    and (POSTGRES_HOST := os.environ.get("POSTGRES_HOST"))
):
    DATABASE_URI = (
        "postgresql://"
        + f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
    )
elif DATABASE_URI := os.environ.get("DATABASE_URI", default=None):
    pass
else:
    warn(
        "Configuration pending: No database URI found.\n"
        + "    Set with DATABASE_URI=<uri> or in secrets.toml"
    )
    DATABASE_URI = "postgresql:///flaskr.db"
