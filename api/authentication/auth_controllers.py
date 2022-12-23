from http import HTTPStatus
from flask import request, jsonify, Blueprint, make_response
from werkzeug.security import check_password_hash
from jwt.api_jwt import encode, decode
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from typing import Union
from datetime import datetime, timedelta

from api.consts.error_enum import ErrorEnum
from .auth_middlewares import get_secret_key
import api.users.users_services as us
from api.users.users_models import Users
from api.mail.mail_app import send_verification_email
from ..consts.responses import SuccessResponse, ErrorResponse, JWTErrorResponse
from ..authentication.auth_helpers import generate_verification_url
import os

authentication = Blueprint("authentication", __name__)

AUTH_TOKEN_EXPIRATION = int(os.getenv("AUTH_TOKEN_EXPIRATION"))
AUTH_REFRESH_TOKEN_EXPIRATION = int(os.getenv("AUTH_REFRESH_TOKEN_EXPIRATION"))
VERIFICATION_TOKEN_EXPIRATION = int(os.getenv("VERIFICATION_TOKEN_EXPIRATION"))


@authentication.route("/register", methods=["POST"])
def signup_user():
    data: Union[Users, None] = request.get_json()
    # data needs verification
    if not data:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()
    inserted_user = us.insert_one(Users.from_dict(data))
    # send verification email with jwt token
    try:
        token = encode(
            {
                "uuid": inserted_user["uuid"],
                "exp": datetime.utcnow()
                + timedelta(seconds=VERIFICATION_TOKEN_EXPIRATION),
            },
            get_secret_key(),
            algorithm="HS256",
        )
    except PyJWTError as e:
        return JWTErrorResponse(ErrorEnum.JWT_ERROR).internal_server_error()
    verification_url = generate_verification_url(token.decode("UTF-8"))
    try:
        send_verification_email(data, verification_url)
    except Exception as e:
        return e
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
                    "exp": datetime.utcnow()
                    + timedelta(seconds=AUTH_TOKEN_EXPIRATION),
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
        if isinstance(e, ExpiredSignatureError):
            return JWTErrorResponse(
                ErrorEnum.AUTH_TOKEN_EXPIRED, e
            ).unauthorized()
        return JWTErrorResponse(ErrorEnum.JWT_INVALID, e).unauthorized()
    user = us.find_one(
        user_uuid=data["uuid"],
    )
    if not user:
        return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()
    if user["verified"]:
        return ErrorResponse(ErrorEnum.USR_ALREADY_VERIFIED).bad_request()
    # TODO: expire token after verification
    user = us.update_one(user["uuid"])
    return SuccessResponse({"user": user}).ok()


@authentication.route("/send/verification", methods=["POST"])
def refresh_verification_token():
    identifier = request.get_json()
    if not identifier:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()
    if "email" in identifier and "username" not in identifier:
        user = us.find_one(email=identifier["email"], secure=False)
    elif "username" in identifier and "email" not in identifier:
        user = us.find_one(username=identifier["username"], secure=False)
    else:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()
    if not user:
        return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()
    if user["verified"]:
        return ErrorResponse(ErrorEnum.USR_ALREADY_VERIFIED).bad_request()
    try:
        token = encode(
            {
                "uuid": user["uuid"],
                "exp": datetime.utcnow()
                + timedelta(seconds=VERIFICATION_TOKEN_EXPIRATION),
            },
            get_secret_key(),
            algorithm="HS256",
        )
    except PyJWTError as e:
        return JWTErrorResponse(ErrorEnum.JWT_ERROR).internal_server_error()
    verification_url = generate_verification_url(token.decode("UTF-8"))
    result = send_verification_email(user, verification_url)
    if result[1] != HTTPStatus.OK:
        return result
    return SuccessResponse({"message": "Verification email sent!"}).ok()
