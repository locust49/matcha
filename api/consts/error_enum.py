from enum import Enum


class ErrorEnum(Enum):
    # User
    USR_NOT_FOUND = 1, "User not found"
    USR_ALREADY_EXISTS = 2, "User already exists"
    USR_INVALID_CREDENTIALS = 3, "Invalid credentials"
    USR_INVALID_EMAIL = 4, "Invalid email"
    USR_INVALID_PASSWORD = 5, "Invalid password"
    USR_INVALID_USERNAME = 6, "Invalid username"
    USR_INVALID_FIRST_NAME = 7, "Invalid first name"
    USR_INVALID_LAST_NAME = 8, "Invalid last name"
    USR_INVALID_PHONE_NUMBER = 9, "Invalid phone number"
    USR_INVALID = 10, "Invalid user"
    USR_INVALID_ID = 11, "Invalid user id"
    USR_NOT_VERIFIED = 12, "User not verified"
    USR_ALREADY_VERIFIED = 13, "User already verified"

    # Auth
    AUTH_INVALID_TOKEN = 14, "Invalid token"
    AUTH_INVALID_REFRESH_TOKEN = 15, "Invalid refresh token"
    AUTH_INVALID_CREDENTIALS = 16, "Authentication failed: Invalid credentials"
    AUTH_TOKEN_EXPIRED = 17, "Token expired"

    AUTH_REFRESH_TOKEN_EXPIRED = 18, "Refresh token expired"
    AUTH_INVALID_USER = 19, "Invalid user"
    AUTH_INVALID_RESET_TOKEN = 20, "Invalid reset token"

    # Database
    DB_CONNECTION_FAILED = 21, "Database connection failed"
    DB_QUERY_FAILED = 22, "Database query failed"

    # Requests
    REQ_INVALID_INPUT = 23, "Invalid data provided"

    # JWT
    JWT_INVALID = 24, "Invalid JWT token"

    # Mail
    MAIL_SEND_ERROR = 25, "Error sending mail"
