from http import HTTPStatus
from flask import request, Blueprint, current_app
from werkzeug.security import check_password_hash
from jwt.api_jwt import encode, decode
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from typing import Union
from datetime import datetime, timedelta

from api.consts.error_enum import ErrorEnum
from .auth_middlewares import get_secret_key, set_auth_headers
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


ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"
VERIFICATION_TOKEN = "verification_token"


@authentication.route("/register", methods=["POST"])
def signup_user():
    data: Union[Users, None] = request.get_json()
    # TODO: data needs verification
    if not data:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()
    inserted_user = us.insert_one(Users.from_dict(data))
    try:
        verification_token = encode(
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
    verification_url = generate_verification_url(
        verification_token.decode("UTF-8")
    )
    try:
        send_verification_email(data, verification_url)
        # TODO: Store all verification tokens in redis and check if the token is valid
        # current_app.redis_client.set(VERIFICATION_TOKEN, verification_token)
    except Exception as e:
        return e
    return SuccessResponse({"user": inserted_user}).created()


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
            access_token = encode(
                {
                    "uuid": user["uuid"],
                    "exp": datetime.utcnow()
                    + timedelta(seconds=AUTH_TOKEN_EXPIRATION),
                },
                get_secret_key(),
                algorithm="HS256",
            )

            refresh_token = encode(
                {
                    "uuid": user["uuid"],
                    "exp": datetime.utcnow()
                    + timedelta(seconds=AUTH_REFRESH_TOKEN_EXPIRATION),
                },
                get_secret_key(),
                algorithm="HS256",
            )
            current_app.redis_client.set(REFRESH_TOKEN, refresh_token)
            # TODO: current_app.redis_client.set(ACCESS_TOKEN, access_token)
            return SuccessResponse(
                {
                    "message": "Logged in successfully.",
                    ACCESS_TOKEN: access_token.decode("UTF-8"),
                }
            ).ok()

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
    user = us.update_one(user["uuid"])
    return SuccessResponse({"user": user}).ok()


@authentication.route("/refresh/verification", methods=["POST"])
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


@authentication.route("/refresh/token", methods=["GET"])
def refresh_token():
    refresh_token = current_app.redis_client.get(REFRESH_TOKEN)
    if not refresh_token:
        return ErrorResponse(ErrorEnum.AUTH_INVALID_REFRESH_TOKEN).unauthorized()
    try:
        data = decode(
            refresh_token,
            get_secret_key(),
            algorithms=["HS256"],
        )
    except PyJWTError as e:
        if isinstance(e, ExpiredSignatureError):
            current_app.redis_client.delete(REFRESH_TOKEN)
            current_app.redis_client.delete(ACCESS_TOKEN)
            return JWTErrorResponse(
                ErrorEnum.AUTH_TOKEN_EXPIRED, e
            ).unauthorized()
            # TODO: log out user here
        return JWTErrorResponse(ErrorEnum.JWT_INVALID, e).unauthorized()
    user = us.find_one(
        user_uuid=data["uuid"],
    )
    if not user:
        return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()
    try:
        access_token = encode(
            {
                "uuid": user["uuid"],
                "exp": datetime.utcnow()
                + timedelta(seconds=AUTH_TOKEN_EXPIRATION),
            },
            get_secret_key(),
            algorithm="HS256",
        )
        refresh_token = encode(
            {
                "uuid": user["uuid"],
                "exp": datetime.utcnow()
                + timedelta(seconds=AUTH_REFRESH_TOKEN_EXPIRATION),
            },
            get_secret_key(),
            algorithm="HS256",
        )
        # TODO: current_app.redis_client.set(ACCESS_TOKEN, access_token)
        current_app.redis_client.set(REFRESH_TOKEN, refresh_token)
        return SuccessResponse({ACCESS_TOKEN: access_token.decode("UTF-8")}).ok()
    except PyJWTError as e:
        return JWTErrorResponse(ErrorEnum.JWT_ERROR).internal_server_error()
