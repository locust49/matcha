import os
from flask_mail import Mail
from flask import Flask
import redis

# Create a Redis client object
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    db=os.getenv("REDIS_DB"),
)

from api.consts.responses import SuccessResponse


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    app.redis_client = redis_client

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/health")
    def health():
        return SuccessResponse({"status": "ok"}).ok()

    with app.app_context():
        from .config.database import db_connection

        # apply the blueprints to the app
        from .users.users_controllers import users
        from .authentication.auth_controllers import authentication
        from .mail.mail_app import email_blueprint

        app.register_blueprint(users, url_prefix="/users")
        app.register_blueprint(email_blueprint, url_prefix="/mail")
        app.register_blueprint(authentication, url_prefix="/auth")

        return app
