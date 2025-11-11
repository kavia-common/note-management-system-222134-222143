from flask_smorest import Blueprint
from flask.views import MethodView

# Keep tag name as "Healt Check" to align with existing openapi.json; use consistent endpoint behavior.
blp = Blueprint("Healt Check", "health", url_prefix="/", description="Health check route")


@blp.route("/")
class HealthCheck(MethodView):
    def get(self):
        """Simple health check endpoint returning service status."""
        return {"message": "Healthy"}
