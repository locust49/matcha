from ..config.database import db_connection as db
import datetime as dt


class ResetPasswordRequest:
    def __init__(self, email):
        self.email = email

    def to_dict(self):
        return {
            "email": self.email,
        }

    @classmethod
    def insert(cls, user_id, token):
        db.get_cursor().execute(
            f"INSERT INTO password_reset_tokens (\"user_id\", \"token\") \
            VALUES ('{user_id}', '{token}') RETURNING *"
        )

        record = db.get_cursor().fetchone()
        if record is not None:
            return record
        else:
            return {"msg": "no uuid returned"}

    @classmethod
    def get_by_token(cls, token):
        db.get_cursor().execute(
            f"SELECT * FROM password_reset_tokens WHERE \"token\" = '{token}'"
        )
        print("token", token)
        try:
            good = db.get_cursor().fetchone()
            return good
        except Exception as e:
            print(e)
            return None

    @classmethod
    def get_by_user(cls, user_id):
        db.get_cursor().execute(
            f"SELECT * FROM password_reset_tokens WHERE \"user_id\" = '{user_id}'"
        )
        try:
            good = db.get_cursor().fetchone()
            return good
        except Exception as e:
            print(e)
            return None

    @classmethod
    def delete(cls, token):
        db.get_cursor().execute(
            f"DELETE FROM password_reset_tokens WHERE \"token\" = '{token}'"
        )
        try:
            return True
        except Exception as e:
            print(e)
            return None
