from ..config.database import db_connection as db
from werkzeug.security import generate_password_hash


users_private_fields = [
    "uuid",
    "username",
    "email",
    "first_name",
    "last_name",
    "created_at",
    "verified",
    "password",
]

users_public_fields = users_private_fields.copy()
users_public_fields.remove("password")


class UsersPublic:
    def __init__(self, username, email, first_name, last_name) -> None:
        assert (
            username is not None
            and len(username) > 0
            and len(username) < 20
            and username.isalnum()
        ), "Username must be alphanumeric and between 1 and 20 characters,\
            received {}".format(
            username
        )
        assert (
            email is not None
            and len(email) > 0
            and len(email) < 50  # TODO: Add validator of email
        ), "Email must be between 1 and 50 characters,\
            received {}".format(
            email
        )
        assert (
            first_name is not None
            and len(first_name) > 0
            and len(first_name) < 20
        ), "First name must be between 1 and 20 characters, received {}\
        ".format(
            first_name
        )
        assert (
            last_name is not None and len(last_name) > 0 and len(last_name) < 20
        ), "Last name must be between 1 and 20 characters, received {}".format(
            last_name
        )
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.verified = False

    # Return the object as a dictionary
    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    # Construct the object from a dictionary
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    # Insert to database
    def insert(self):
        db.get_cursor().execute(
            "INSERT INTO users (username, email, password, first_name, \
                last_name) VALUES ('{}', '{}', '{}', '{}', '{}') RETURNING\
                uuid".format(
                self.username,
                self.email,
                self.password,
                self.first_name,
                self.last_name,
            ),
        )
        user_uuid = db.get_cursor().fetchone()
        if user_uuid is not None:
            return user_uuid
        else:
            return {"msg": "User not inserted"}

    # Get all users
    @classmethod
    def get_all(cls):
        try:
            db.get_cursor().execute(
                "SELECT {} FROM users".format(",".join(users_public_fields))
            )
            users = db.get_cursor().fetchall()
            return users
        except Exception as e:
            print(e)
            return None

    # Get user by id
    @classmethod
    def get_by_uuid(cls, uuid, secure=True):
        if not secure:
            fields = users_private_fields
        else:
            fields = users_public_fields
        db.get_cursor().execute(
            "SELECT {} FROM users WHERE uuid = '{}'".format(
                ",".join(fields), uuid
            )
        )
        try:
            return db.get_cursor().fetchone()
        except Exception as e:
            print(e)
            return None

    # Get user by username
    @classmethod
    def get_by_username(cls, username, secure=True):
        if not secure:
            fields = users_private_fields
        else:
            fields = users_public_fields
        db.get_cursor().execute(
            "SELECT {} FROM users WHERE username = '{}'".format(
                ",".join(fields), username
            )
        )
        try:
            return db.get_cursor().fetchone()
        except Exception as e:
            print(e)
            return None

    # Delete user by id
    @classmethod
    def delete_by_uuid(cls, uuid):
        db.get_cursor().execute(
            "DELETE FROM users WHERE uuid = '{}'".format(uuid)
        )
        try:
            return db.get_cursor().fetchone()
        except Exception as e:
            print(e)
            return None

    @classmethod
    def verify_user(cls, uuid):
        db.get_cursor().execute(
            "UPDATE users SET verified = true WHERE uuid = '{}' \
                RETURNING verified".format(
                uuid
            )
        )
        try:
            return db.get_cursor().fetchone()
        except Exception as e:
            print(e)
            return None

    def __repr__(self) -> str:
        return f"User({self.username = }, {self.email = }, {self.password = },\
            {self.first_name = }, {self.last_name = })"

    def __str__(self) -> str:
        return f"User({self.username = }, {self.email = }, {self.password = },\
            {self.first_name = }, {self.last_name = })"

    def __getitem__(self, key):
        return getattr(self, key)

    def __del__(self):
        print("User object deleted")


class Users(UsersPublic):
    # Add more fields to the public class
    def __init__(
        self,
        username,
        email,
        password,
        first_name,
        last_name,
    ) -> None:
        super().__init__(username, email, first_name, last_name)
        # encrypted password
        self.password = generate_password_hash(password, method="sha256")

    # Return the object as a dictionary
    def to_dict(self):
        pass
