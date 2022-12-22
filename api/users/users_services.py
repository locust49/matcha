from .users_models import Users, UsersPublic


def insert_one(user: Users):
    try:
        inserted_user = user.insert()
    except Exception as e:
        print("Error inserting user: ", e)
        return None
    return inserted_user


def find_one(
    user_uuid=None, username=None, secure=True
):  # should return -> Users or Exception:
    if user_uuid:
        user = Users.get_by_uuid(user_uuid, secure)
    elif username:
        user = Users.get_by_username(username, secure)
    else:
        raise Exception("No user_uuid or username provided")
    if user:
        return dict(user)
    # should throw an error here
    return None


def find_all():
    users = UsersPublic.get_all()
    return users


def find_all_paginated(page, per_page):
    # users = Users.get_all_paginated(page, per_page)
    # return users
    pass


def remove_one(user_uuid):
    if not user_uuid:
        return None
    user = Users.get_by_uuid(user_uuid)
    if not user:
        return None
    try:
        Users.delete_by_uuid(user_uuid)
    except Exception as e:
        print(e)
        return None
    return user


def update_one(user_uuid):
    if not user_uuid:
        return None
    user = Users.get_by_uuid(user_uuid)
    if not user:
        return None
    try:
        updated_user = UsersPublic.verify_user(user_uuid)
    except Exception as e:
        print(e)
        return None
    return updated_user
