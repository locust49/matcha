from http import HTTPStatus
from flask import request, Blueprint, current_app
from werkzeug.security import check_password_hash
from jwt.api_jwt import encode, decode
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from typing import Union
from datetime import datetime, timedelta

from api.consts.error_enum import ErrorEnum
from .auth_middlewares import get_secret_key
from .auth_models import ResetPasswordRequest
import api.users.users_services as us
from api.users.users_models import Users
from api.mail.mail_app import send_verification_email, send_reset_password_email
from ..consts.responses import SuccessResponse, ErrorResponse, JWTErrorResponse
from ..authentication.auth_helpers import (
    generate_verification_url,
    generate_password_reset_url,
)
import os
import secrets

authentication = Blueprint("authentication", __name__)

AUTH_TOKEN_EXPIRATION = int(os.getenv("AUTH_TOKEN_EXPIRATION"))
AUTH_REFRESH_TOKEN_EXPIRATION = int(os.getenv("AUTH_REFRESH_TOKEN_EXPIRATION"))
VERIFICATION_TOKEN_EXPIRATION = int(os.getenv("VERIFICATION_TOKEN_EXPIRATION"))
AUTH_RESET_TOKEN_EXPIRATION = int(os.getenv("AUTH_RESET_TOKEN_EXPIRATION"))


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
        return ErrorResponse(ErrorEnum.AUTH_INVALID_CREDENTIALS).unauthorized()
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
            current_app.redis_client.set(ACCESS_TOKEN, access_token)
            return SuccessResponse({"message": "Logged in successfully."}).ok()

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
    return SuccessResponse({"user": user}).partial_content()


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


@authentication.route("/logout", methods=["GET"])
def logout():
    current_app.redis_client.delete(REFRESH_TOKEN)
    current_app.redis_client.delete(ACCESS_TOKEN)
    return SuccessResponse({"message": "Logged out successfully."}).ok()


@authentication.route("/forgot-password", methods=["POST"])
def reset_password():
    email = request.get_json()
    if not email:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()

    user = us.find_one(email=email["email"], secure=False)
    if not user:
        return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()

    token = None
    try:
        # check if user has already requested a password reset
        record = ResetPasswordRequest.get_by_user(user["uuid"])
        if record is not None:
            # check if token is still valid
            if (
                record["created_at"]
                + timedelta(seconds=AUTH_RESET_TOKEN_EXPIRATION)
                > datetime.utcnow()
            ):
                token = record["token"]
            else:
                # delete old record
                ResetPasswordRequest.delete(record["token"])
        if token is None:
            token = secrets.token_urlsafe(64)
            ResetPasswordRequest.insert(user["uuid"], token)

        # TODO: move to service !
        reset_url = generate_password_reset_url(token)
        result = send_reset_password_email(user, reset_url)
        if result[1] != HTTPStatus.OK:
            return result
    except Exception as e:
        return ErrorResponse(ErrorEnum.DB_QUERY_FAILED).internal_server_error()
    return SuccessResponse({"message": "Password reset email sent!"}).ok()


@authentication.route("/reset/<token>", methods=["POST"])
def reset_password_with_token(token):
    password = request.get_json()
    if not password:
        return ErrorResponse(ErrorEnum.REQ_INVALID_INPUT).bad_request()
    try:
        reset_request = ResetPasswordRequest.get_by_token(token=token)
        if reset_request is None:
            return ErrorResponse(
                ErrorEnum.AUTH_INVALID_RESET_TOKEN
            ).unauthorized()
        expires_at = reset_request["created_at"] + timedelta(
            seconds=AUTH_RESET_TOKEN_EXPIRATION
        )
        if datetime.utcnow() > expires_at:
            return ErrorResponse(ErrorEnum.AUTH_TOKEN_EXPIRED).unauthorized()
        user = us.find_one(user_uuid=reset_request["user_id"])
        if not user:
            return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()
        us.update_password(user["uuid"], password["password"])
        ResetPasswordRequest.delete(token)
        return SuccessResponse(
            {"message": "Password reset successful!"}
        ).partial_content()
    except Exception as e:
        return ErrorResponse(ErrorEnum.DB_QUERY_FAILED).internal_server_error()
