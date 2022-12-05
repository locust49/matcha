from . import users_services as us
from flask import request, Blueprint
from api.authentication.auth_middlewares import token_required

users = Blueprint("users", __name__)

# should not be accessed by anyone even admin
@users.route("/create", methods=["POST"], endpoint="create_user")
def create_user():
    inserted_user = us.insert_one(request.get_json())
    return inserted_user, 201


@users.route("/<user_uuid>", methods=["GET"])
def get_user_by_uuid(user_uuid):
    user = us.find_one(user_uuid)
    if not user:
        return {"message": "User not found"}, 404
    return user, 200


@users.route("/all", methods=["GET"], defaults={"page": 1, "per_page": 10})
@token_required
def get_all_users(current_user):
    # users = us.find_all_paginated(page, per_page)
    users = us.find_all()
    return {"users": users}, 200
