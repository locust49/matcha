from flask import g
from .database import Database


class Users:
    def __init__(self, username, email, password, first_name, last_name) -> None:
        assert (
            username is not None
            and len(username) > 0
            and len(username) < 20
            and username.isalnum()
        ), "Username must be alphanumeric and between 1 and 20 characters, received {}".format(
            username
        )
        assert (
            email is not None
            and len(email) > 0
            and len(email) < 50  # TODO: Add validator of email
        ), "Email must be between 1 and 50 characters, received {}".format(email)
        assert password is not None, "Missing password".format(password)
        assert (
            first_name is not None and len(first_name) > 0 and len(first_name) < 20
        ), "First name must be between 1 and 20 characters, received {}".format(
            first_name
        )
        assert (
            last_name is not None and len(last_name) > 0 and len(last_name) < 20
        ), "Last name must be between 1 and 20 characters, received {}".format(
            last_name
        )
        self.username = username
        self.email = email
        # encrypted password
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    # Return the object as a dictionary
    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    # Construct the object from a dictionary
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    # Insert to database
    def insert(self):
        db = Database().get_db()
        # db.cursor().execute(
        #     "INSERT INTO users (username, email, password, first_name, last_name) VALUES ('{}', '{}', '{}', '{}', '{}') RETURNING uuid".format(
        #         self.username,
        #         self.email,
        #         self.password,
        #         self.first_name,
        #         self.last_name,
        #     ),
        # )
        # db.commit()
        db.cursor().execute("SELECT * FROM users;")
        user = db.cursor().fetchone()
        print("returning user: ", user)
        if user is not None:
            return user
        else:
            return None

    # Get all users
    @classmethod
    def get_all(cls):
        # db = Database().get_db()
        # try:
        #     db.cursor().execute("SELECT * FROM users")
        #     users = db.cursor().fetchall()
        #     return users
        # except Exception as e:
        #     print(e)
        #     return None
        db_inst = Database()
        db_inst.get_db()
        db_inst.get_cursor().execute("SELECT * FROM users")
        users = db_inst.get_cursor().fetchall()
        print(">>>>>>>>>> ", db_inst.get_cursor().statusmessage)
        print(users)

    # Get user by id
    @classmethod
    def get_by_uuid(cls, uuid):
        db = Database().get_db()
        user = db.cursor().execute("SELECT * FROM users WHERE uuid = {}".format(uuid))
        try:
            user = db.cursor().fetchone()
            return user
        except Exception as e:
            print(e)
            return None

    # Get user by username
    @classmethod
    def get_by_username(cls, username):
        db = Database().get_db()
        user = db.cursor().execute(
            "SELECT * FROM users WHERE username = '{}'".format(username)
        )
        try:
            print(">>> User  = ", user)
            print(">>> username  = ", username)

            # user = db.cursor().fetchone()
            if user:
                print("User found", user)
                return dict(user)
            else:
                print("User not found", user)
                return None
        except Exception as e:
            print(e)
            return None

    def __repr__(self) -> str:
        return f"User({self.username = }, {self.email = }, {self.password = }, {self.first_name = }, {self.last_name = })"

    def __str__(self) -> str:
        return f"User({self.username = }, {self.email = }, {self.password = }, {self.first_name = }, {self.last_name = })"

    def __getitem__(self, key):
        return getattr(self, key)

    def __del__(self):
        print("User object deleted")
