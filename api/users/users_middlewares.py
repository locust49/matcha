from functools import wraps
from api.consts.error_enum import ErrorEnum
from api.consts.responses import ErrorResponse


def verification_required(fct):
    @wraps(fct)
    # define the decorator function  that checks if the user is verified or not
    def decorator(*args, **kwargs):
        logged_user = args[0]["logged_user"]
        if not logged_user or not logged_user["verified"]:
            return ErrorResponse(ErrorEnum.USR_NOT_VERIFIED).unauthorized()
        return fct(*args, **kwargs)

    return decorator
