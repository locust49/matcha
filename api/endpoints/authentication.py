from functools import wraps
from flask import request, jsonify, Blueprint, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from typing import Union
from datetime import datetime, timedelta
import os

from api.models.users import Users
from api.models.database import Database

authentication = Blueprint("authentication", __name__, url_prefix="/auth")


def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("No SECRET_KEY")
    return secret_key


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if "x-access-tokens" in request.headers:
            token = request.headers["x-access-tokens"]
        if not token:
            return jsonify({"message": "A valid token is missing"})
        try:
            data = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
            current_user = Users.get_by_uuid(data["uuid"])
        except:
            return jsonify({"message": "token is invalid"})
        return f(current_user, *args, **kwargs)

    return decorator


@authentication.route("/register", methods=["POST"])
def signup_user():
    data: Union[Users, None] = request.get_json()
    # if not data:
    #     return jsonify({"message": "No input data provided"}), 400
    # if not data["username"]:
    #     return jsonify({"message": "No username provided"}), 400
    # if not data["email"]:
    #     return jsonify({"message": "No email provided"}), 400
    # if not data["password"]:
    #     return jsonify({"message": "No password provided"}), 400
    # if not data["first_name"]:
    #     return jsonify({"message": "No first name provided"}), 400
    # if not data["last_name"]:
    #     return jsonify({"message": "No last name provided"}), 400
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    hashed_password = generate_password_hash(data["password"], method="sha256")

    new_user = Users(
        data["username"],
        data["email"],
        hashed_password,
        data["first_name"],
        data["last_name"],
    )
    new_user.insert()
    return jsonify({"message": "registered successfully"})


@authentication.route("/login", methods=["POST"])
def login_user():
    auth = request.get_json()
    print("Auth", auth)
    if not auth or not auth["username"] or not auth["password"]:
        return make_response("missing body", 401, {"Authentication": 'login required"'})

    user = Users.get_by_username(auth["username"])
    print("User", user)
    if not user:
        return make_response(
            "inexistant user", 401, {"Authentication": 'login required"'}
        )
    if check_password_hash(user["password"], auth["password"]):
        token = jwt.encode(
            {"uuid": user["uuid"], "exp": datetime.utcnow() + timedelta(minutes=45)},
            get_secret_key(),
            "HS256",
        )
        return jsonify({"token": token})

    return make_response(
        "could not verify", 401, {"Authentication": '"login required"'}
    )
