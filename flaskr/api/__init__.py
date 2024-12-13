from flask.blueprints import Blueprint

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__)


# Import the API routes
from flaskr.api import (  # noqa: F401, E402
    v1,
)
