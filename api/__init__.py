import os

from flask import Flask


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
        return {"status": "ok"}

    # register the database commands

    with app.app_context():
        from .models.database import db_connection
    # apply the blueprints to the app
    from .endpoints.users import users
    from .endpoints.authentication import authentication

    app.register_blueprint(users)
    app.register_blueprint(authentication)

    return app
