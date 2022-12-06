from . import users_services as us
from .users_models import Users
from flask import request, Blueprint
from api.authentication.auth_middlewares import token_required

users = Blueprint("users", __name__)


@users.route("/<user_uuid>", methods=["GET"])
def get_user_by_uuid(user_uuid):
    user = us.find_one(user_uuid)
    if not user:
        return {"message": "User not found"}, 404
    return user, 200


@users.route("/all", methods=["GET"], defaults={"page": 1, "per_page": 10})
@token_required
def get_all_users(current_user, page, per_page):
    print("current_user: {}".format(current_user, page, per_page))
    # users = us.find_all_paginated(page, per_page)
    users = us.find_all()
    if not users:
        return {"message": "No users found"}, 404
    return {"users": users}, 200
