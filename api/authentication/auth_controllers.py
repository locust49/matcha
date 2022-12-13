from flask import request, jsonify, Blueprint, make_response
from werkzeug.security import check_password_hash
from jwt.api_jwt import encode
from typing import Union
from datetime import datetime, timedelta

from api.consts.error_enum import ErrorEnum
from .auth_middlewares import get_secret_key
import api.users.users_services as us
from api.users.users_models import Users
from ..consts.responses import SuccessResponse, ErrorResponse

authentication = Blueprint("authentication", __name__)


@authentication.route("/register", methods=["POST"])
def signup_user():
    data: Union[Users, None] = request.get_json()
    # needs verification
    if not data:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()
    inserted_user = us.insert_one(Users.from_dict(data))
    return SuccessResponse(inserted_user).created()


@authentication.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    if not auth or not auth["username"] or not auth["password"]:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()
    user = us.find_one(username=auth["username"])
    if not user:
        return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()
    if check_password_hash(user["password"], auth["password"]):
        token = encode(
            {"uuid": user["uuid"], "exp": datetime.utcnow() + timedelta(minutes=45)},
            get_secret_key(),
            algorithm="HS256",
        )
        return SuccessResponse({"token": token.decode("UTF-8")}).ok()

    return ErrorResponse(ErrorEnum.AUTH_INVALID_CREDENTIALS).unauthorized()
