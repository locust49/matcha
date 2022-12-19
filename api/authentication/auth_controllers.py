from flask import request, jsonify, Blueprint, make_response
from werkzeug.security import check_password_hash
from jwt.api_jwt import encode, decode
from jwt.exceptions import PyJWTError
from typing import Union
from datetime import datetime, timedelta

from api.consts.error_enum import ErrorEnum
from .auth_middlewares import get_secret_key
import api.users.users_services as us
from api.users.users_models import Users
from ..consts.responses import SuccessResponse, ErrorResponse, JWTErrorResponse

authentication = Blueprint("authentication", __name__)


@authentication.route("/register", methods=["POST"])
def signup_user():
    data: Union[Users, None] = request.get_json()
    # needs verification
    if not data:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()
    inserted_user = us.insert_one(Users.from_dict(data))
    # send verification email with jwt token
    try:
        token = encode(
            {
                "uuid": inserted_user["uuid"],
                "exp": datetime.utcnow() + timedelta(minutes=5),
            },
            get_secret_key(),
            algorithm="HS256",
        )
    except PyJWTError as e:
        return JWTErrorResponse(ErrorEnum.JWT_ERROR).internal_server_error()
    # send mail here
    print(f'* Sending verification email with token: {token.decode("UTF-8")} *')
    return SuccessResponse(inserted_user).created()


@authentication.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    if not auth or not auth["username"] or not auth["password"]:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()
    user = us.find_one(username=auth["username"], secure=False)
    if not user:
        return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()
    if check_password_hash(user["password"], auth["password"]):
        try:
            token = encode(
                {
                    "uuid": user["uuid"],
                    "exp": datetime.utcnow() + timedelta(minutes=45),
                },
                get_secret_key(),
                algorithm="HS256",
            )
            return SuccessResponse({"token": token.decode("UTF-8")}).ok()
        except PyJWTError as e:
            return JWTErrorResponse(
                ErrorEnum.JWT_INVALID, e
            ).internal_server_error()
    return ErrorResponse(ErrorEnum.AUTH_INVALID_CREDENTIALS).unauthorized()


@authentication.route("/verify/<token>", methods=["GET"])
def verify(token):
    try:
        data = decode(token, get_secret_key(), algorithms=["HS256"])
    except PyJWTError as e:
        return JWTErrorResponse(ErrorEnum.JWT_INVALID, e).unauthorized()
    user = us.find_one(
        data["uuid"],
    )
    if not user:
        return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()
    if user["verified"]:
        return ErrorResponse(ErrorEnum.USR_ALREADY_VERIFIED).bad_request()
    # TODO: expire token after verification
    user = us.update_one(user["uuid"])
    return SuccessResponse({"user": user}).ok()
