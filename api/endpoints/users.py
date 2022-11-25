from ..models.users import Users
from flask import request, Blueprint


users = Blueprint("users", __name__, url_prefix="/users")


@users.route("/create", methods=["POST"])
def create_user():
    print("Creating user {}".format(request.get_json()))
    user = Users.from_dict(request.get_json())
    Users.insert(user)
    return user.to_dict(), 201
