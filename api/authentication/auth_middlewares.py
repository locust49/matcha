from functools import wraps
from flask import request, current_app
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from jwt import decode
from api.consts.error_enum import ErrorEnum
from api.consts.responses import ErrorResponse, JWTErrorResponse
from api.authentication.auth_helpers import refresh_token, get_secret_key

import api.users.users_services as us

ACCESS_TOKEN = "access_token"


def token_required(fct):
    @wraps(fct)
    def decorator(*args, **kwargs):
        token_cookie = request.cookies.get(ACCESS_TOKEN)
        if not token_cookie:
            return ErrorResponse(ErrorEnum.AUTH_INVALID_TOKEN).unauthorized()
        token = token_cookie.replace("Bearer b'", "").replace("'", "")
        if not token:
            return ErrorResponse(ErrorEnum.AUTH_INVALID_TOKEN).unauthorized()
        try:
            data = decode(token, get_secret_key(), algorithms=["HS256"])
            logged_user = us.find_one(user_uuid=data["uuid"])
            if not logged_user:
                return ErrorResponse(ErrorEnum.AUTH_INVALID_USER).unauthorized()
        except PyJWTError as e:
            if isinstance(e, ExpiredSignatureError):
                refresh_access_token = refresh_token()
                if "error" in refresh_access_token[0]:
                    error_refresh = refresh_access_token
                    return error_refresh
                # if refresh token is expired
                if refresh_access_token[1] != 200:
                    return ErrorResponse(
                        ErrorEnum.AUTH_INVALID_TOKEN
                    ).unauthorized()
                # get new access token
                new_access_token = refresh_access_token[0]["data"][
                    "access_token"
                ]
                # set new access token in redis
                current_app.redis_client.set(ACCESS_TOKEN, new_access_token)
                print("Refreshed access token")
                # decode new access token
                data = decode(
                    new_access_token,
                    get_secret_key(),
                    algorithms=["HS256"],
                )
                logged_user = us.find_one(user_uuid=data["uuid"])
                if not logged_user:
                    return JWTErrorResponse(
                        ErrorEnum.JWT_INVALID, e
                    ).unauthorized()
            else:
                return JWTErrorResponse(ErrorEnum.JWT_INVALID, e).unauthorized()
        return fct({"logged_user": logged_user}, *args, **kwargs)

    return decorator
