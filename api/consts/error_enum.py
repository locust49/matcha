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
    USR_INVALID_ROLE = 12, "Invalid role"

    # Auth
    AUTH_INVALID_TOKEN = 13, "Invalid token"
    AUTH_INVALID_REFRESH_TOKEN = 14, "Invalid refresh token"
    AUTH_INVALID_CREDENTIALS = 15, "Invalid credentials"
    AUTH_TOKEN_EXPIRED = 16, "Token expired"
    AUTH_REFRESH_TOKEN_EXPIRED = 17, "Refresh token expired"
    AUTH_INVALID_USER = 18, "Invalid user"

    # Database
    DB_CONNECTION_FAILED = 19, "Database connection failed"
    DB_QUERY_FAILED = 20, "Database query failed"
    
