from http import HTTPStatus
from .error_enum import ErrorEnum


class SuccessResponse:
    def __init__(self, data):
        self.data = data

    def to_json(self):
        if self.data is None:
            return {}

        return {"data": self.data}

    def ok(self):
        return self.to_json(), HTTPStatus.OK

    def created(self):
        return self.to_json(), HTTPStatus.CREATED

    def accepted(self):
        return self.to_json(), HTTPStatus.ACCEPTED

    def no_content(self):
        return self.to_json(), HTTPStatus.NO_CONTENT

    def partial_content(self):
        return self.to_json(), HTTPStatus.PARTIAL_CONTENT

    def already_reported(self):
        return self.to_json(), HTTPStatus.ALREADY_REPORTED


class ErrorResponse:
    def __init__(self, code: ErrorEnum):
        self.code = code

    def to_json(self):
        return {"error": {"code": self.code.name, "message": self.code.value[1]}}

    def bad_request(self):
        return self.to_json(), HTTPStatus.BAD_REQUEST

    def unauthorized(self):
        return self.to_json(), HTTPStatus.UNAUTHORIZED

    def forbidden(self):
        return self.to_json(), HTTPStatus.FORBIDDEN

    def not_found(self):
        return self.to_json(), HTTPStatus.NOT_FOUND

    def method_not_allowed(self):
        return self.to_json(), HTTPStatus.METHOD_NOT_ALLOWED

    def not_acceptable(self):
        return self.to_json(), HTTPStatus.NOT_ACCEPTABLE

    def conflict(self):
        return self.to_json(), HTTPStatus.CONFLICT

    def internal_server_error(self):
        return self.to_json(), HTTPStatus.INTERNAL_SERVER_ERROR


class JWTErrorResponse(ErrorResponse):
    def __init__(self, code: ErrorEnum, error):
        super().__init__(code)
        self.error = error

    def to_json(self):
        return {
            "error": {
                "code": self.code.name,
                "message": str(self.error),
                "error": self.error.__class__.__name__,
            }
        }
