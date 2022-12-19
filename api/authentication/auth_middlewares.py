from functools import wraps
from flask import request
from jwt.exceptions import PyJWTError
from jwt.api_jwt import decode
import os
from api.consts.error_enum import ErrorEnum
from api.consts.responses import ErrorResponse, JWTErrorResponse

import api.users.users_services as us


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
            return ErrorResponse(ErrorEnum.AUTH_INVALID_TOKEN).unauthorized()
        try:
            data = decode(token, get_secret_key(), algorithms=["HS256"])
            logged_user = us.find_one(data["uuid"])
            if not logged_user:
                return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()
        except PyJWTError as e:
            return JWTErrorResponse(ErrorEnum.JWT_INVALID, e).unauthorized()
        return fct({"logged_user": logged_user}, *args, **kwargs)

    return decorator
