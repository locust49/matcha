from .users_models import Users


def insert_one(user: Users):
    inserted_user = user.insert()
    return inserted_user


def find_one(user_uuid=None, username=None):  # should return -> Users or Exception:
    if user_uuid:
        user = Users.get_by_uuid(user_uuid)
    elif username:
        user = Users.get_by_username(username)
    else:
        raise Exception("No user_uuid or username provided")
    if user:
        return dict(user)
    # should throw an error here
    return None


def find_all():
    users = Users.get_all()
    return users


def find_all_paginated(page, per_page):
    # users = Users.get_all_paginated(page, per_page)
    # return users
    pass
