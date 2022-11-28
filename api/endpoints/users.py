from ..models.users import Users
from flask import request, Blueprint


users = Blueprint("users", __name__, url_prefix="/users")


@users.route("/create", methods=["POST"])
# should not be accessed by anyone even admin
def create_user():
    print("Creating user {}".format(request.get_json()))
    user = Users.from_dict(request.get_json())
    inserted_user = Users.insert(user)
    print("Inserted user {}".format(inserted_user))
    return user.to_dict(), 201


@users.route("/<user_uuid>", methods=["GET"])
def get_user_by_uuid(user_uuid):
    print("Getting user {}".format(user_uuid))
    user = Users.get_by_uuid(user_uuid)
    if user:
        return dict(user), 200
    else:
        return {"message": "User not found"}, 404


@users.route("/all", methods=["GET"])
def get_all_users():
    print("Getting all users")
    users = Users.get_all()
    return {"success": True}, 200
