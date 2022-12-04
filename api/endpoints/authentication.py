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


def token_required(fct):
    @wraps(fct)
    def decorator(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"][7:]
        if not token:
            return jsonify({"message": "A valid token is missing"})
        try:
            data = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
            current_user = Users.get_by_uuid(data["uuid"])
        except Exception as e:
            print("Exception: {}".format(e))
            return jsonify({"Error": str(e)})
        return fct(current_user, *args, **kwargs)

    return decorator


@authentication.route("/register", methods=["POST"])
def signup_user():
    data: Union[Users, None] = request.get_json()
    # needs verification
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
def login():
    auth = request.get_json()
    if not auth or not auth["username"] or not auth["password"]:
        return make_response("missing body", 401,
                             {"Authentication": 'login required"'})

    user = Users.get_by_username(auth["username"])
    if not user:
        return make_response(
            "inexistant user", 401, {"Authentication": 'login required"'}
        )
    print(
        "Verifying password : {}".format(
            check_password_hash(user["password"], auth["password"]))
    )
    if check_password_hash(user["password"], auth["password"]):
        token = jwt.encode(
            {"uuid": user["uuid"], "exp": datetime.utcnow() +
             timedelta(minutes=45)},
            get_secret_key(),
            algorithm="HS256",
        )
        return {"token": token.decode("UTF-8")}

    return make_response(
        "could not verify", 401, {"Authentication": '"Authentication Failed"'}
    )
