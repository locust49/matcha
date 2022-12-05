from .users_models import Users


def insert_one(user):
    inserted_user = Users.insert(user)
    return inserted_user


def find_one(user_uuid=None, username=None):
    if user_uuid:
        user = Users.get_by_uuid(user_uuid)
    elif username:
        user = Users.get_by_username(username)
    else:
        raise Exception("No user_uuid or username provided")
    if user:
        return dict(user)
    return None


def find_all():
    users = Users.get_all()
    return users


def find_all_paginated(page, per_page):
    # users = Users.get_all_paginated(page, per_page)
    # return users
    pass
