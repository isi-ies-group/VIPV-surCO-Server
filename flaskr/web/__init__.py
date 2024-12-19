from flask.blueprints import Blueprint

# Create a Blueprint for the web interface
web_bp = Blueprint('web', __name__)


# Import the API routes
from flaskr.web import (  # noqa: F401, E402
    v1,
)
