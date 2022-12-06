from flask import request, jsonify, Blueprint, make_response
from werkzeug.security import check_password_hash
from jwt.api_jwt import encode
from typing import Union
from datetime import datetime, timedelta
from .auth_middlewares import get_secret_key
import api.users.users_services as us
from api.users.users_models import Users

authentication = Blueprint("authentication", __name__)


@authentication.route("/register", methods=["POST"])
def signup_user():
    data: Union[Users, None] = request.get_json()
    # needs verification
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    inserted_user = us.insert_one(Users.from_dict(data))
    return jsonify({"message": "registered successfully", "user": inserted_user}), 201


@authentication.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    if not auth or not auth["username"] or not auth["password"]:
        return make_response("missing body", 401, {"Authentication": 'login required"'})

    user = us.find_one(username=auth["username"])
    if not user:
        return make_response(
            {"error": "inexistant user"}, 404, {"Authentication": 'login required"'}
        )
    print(
        "Verifying password : {}".format(
            check_password_hash(user["password"], auth["password"])
        )
    )
    if check_password_hash(user["password"], auth["password"]):
        token = encode(
            {"uuid": user["uuid"], "exp": datetime.utcnow() + timedelta(minutes=45)},
            get_secret_key(),
            algorithm="HS256",
        )
        return {"token": token.decode("UTF-8")}  # type: ignore

    return make_response(
        "could not verify", 401, {"Authentication": '"Authentication Failed"'}
    )
