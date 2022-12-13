from . import users_services as us
from .users_models import Users
from flask import request, Blueprint
from api.authentication.auth_middlewares import token_required
from api.consts.responses import SuccessResponse, ErrorResponse
from api.consts.error_enum import ErrorEnum

users = Blueprint("users", __name__)


@users.route("/<user_uuid>", methods=["GET"])
def get_user_by_uuid(user_uuid):
    result = {"user": us.find_one(user_uuid)}
    # user = us.find_one(user_uuid)
    if not result["user"]:  # TODO: change condition to check if user
        # contains an error
        return ErrorResponse(ErrorEnum.USR_NOT_FOUND).not_found()
    return SuccessResponse(result).ok()


@users.route("/all", methods=["GET"], defaults={"page": 1, "per_page": 10})
@token_required
def get_all_users(current_user, page, per_page):
    # users = us.find_all_paginated(page, per_page)
    users = us.find_all()
    return SuccessResponse({"users": users}).ok()


@users.route("/remove/<user_uuid>", methods=["DELETE"])
def remove_user(user_uuid):
    result = us.remove_one(user_uuid)
    if not result:
        return ErrorResponse(ErrorEnum.USR_NOT_FOUND).not_found()
    return SuccessResponse(result).no_content()
