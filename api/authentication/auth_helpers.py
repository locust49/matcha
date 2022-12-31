import os
from flask import current_app
from api.consts.error_enum import ErrorEnum
from api.consts.responses import *
from jwt.api_jwt import decode, encode
from datetime import datetime, timedelta
from jwt.exceptions import PyJWTError, ExpiredSignatureError
import api.users.users_services as us


HOST = os.getenv("HOST")
PORT = os.getenv("PORT")


ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"
VERIFICATION_TOKEN = "verification_token"

AUTH_TOKEN_EXPIRATION = int(os.getenv("AUTH_TOKEN_EXPIRATION"))
AUTH_REFRESH_TOKEN_EXPIRATION = int(os.getenv("AUTH_REFRESH_TOKEN_EXPIRATION"))
VERIFICATION_TOKEN_EXPIRATION = int(os.getenv("VERIFICATION_TOKEN_EXPIRATION"))
AUTH_RESET_TOKEN_EXPIRATION = int(os.getenv("AUTH_RESET_TOKEN_EXPIRATION"))


def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("No SECRET_KEY")
    return secret_key


def generate_verification_url(token):
    verification_url = f"http://{HOST}:{PORT}/auth/verify/{token}"
    print(f"Verification URL: {verification_url}")
    return verification_url


def generate_password_reset_url(token):
    password_reset_url = f"http://{HOST}:{PORT}/auth/reset/{token}"
    print(f"Password reset URL: {password_reset_url}")
    return password_reset_url


def refresh_token():
    refresh_token = current_app.redis_client.get(REFRESH_TOKEN)
    print("*) REFRESH TOKEN: ", refresh_token)
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
            response = JWTErrorResponse(
                ErrorEnum.AUTH_TOKEN_EXPIRED, e
            ).unauthorized()
            response.set_cookie(ACCESS_TOKEN, "", expires=0)
            return response
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
        return SuccessResponse({ACCESS_TOKEN: access_token.decode("UTF-8")}).ok()
    except PyJWTError as e:
        return JWTErrorResponse(ErrorEnum.JWT_ERROR).internal_server_error()
