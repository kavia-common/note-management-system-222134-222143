from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

from .routes.health import blp as health_blp
from .routes.notes import blp as notes_blp


app = Flask(__name__)
app.url_map.strict_slashes = False

# Enable CORS for all origins; in production restrict as needed via environment configuration.
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAPI / Swagger configuration
app.config["API_TITLE"] = "My Flask API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Register API blueprints with flask-smorest
api = Api(app)

# Tag ordering and descriptions for OpenAPI docs
api.spec.components.security_scheme("NoAuth", {"type": "apiKey", "in": "header", "name": "X-API-KEY"})
api.spec.tag({"name": "Healt Check", "description": "Health check route"})  # preserving existing spelling in docs
api.spec.tag({"name": "Notes", "description": "CRUD operations for notes"})

api.register_blueprint(health_blp)
api.register_blueprint(notes_blp)
