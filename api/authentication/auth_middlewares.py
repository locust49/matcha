from functools import wraps
from flask import request, jsonify
import jwt
from jwt.api_jwt import decode
import os

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
            return jsonify({"message": "A valid token is missing"}), 401
        try:
            data = decode(token, get_secret_key(), algorithms=["HS256"])
            logged_user = us.find_one(data["uuid"])
            if not logged_user:
                return jsonify({"message": "User not found"}), 404
        except Exception as e:
            print("Exception: {}".format(e))
            return jsonify({"Error": str(e)})
        return fct(logged_user, *args, **kwargs)

    return decorator
