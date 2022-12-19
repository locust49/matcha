import os

from flask import Flask

from api.consts.responses import SuccessResponse


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/health")
    def health():
        return SuccessResponse({"status": "ok"}).ok()

    # register the database commands

    with app.app_context():
        from .config.database import db_connection
    # apply the blueprints to the app
    from .users.users_controllers import users
    from .authentication.auth_controllers import authentication

    app.register_blueprint(users, url_prefix="/users")
    app.register_blueprint(authentication, url_prefix="/auth")

    return app
