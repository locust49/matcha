import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv, find_dotenv
from flask import current_app


loading = load_dotenv()

if not loading:
    raise ValueError("No .env file found")

db_config = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "cursor_factory": RealDictCursor,
}


class Database:
    __connection = None
    __cursor = None

    def __init__(self):
        """
        Initialize the database
        """
        print(
            "__Initializing__ database with connection {}".format(Database.__connection)
        )

        if Database.__connection is None:
            try:
                Database.__connection = psycopg2.connect(**db_config)
                if Database.__connection is None:
                    raise Exception("Database connection failed")
                Database.__connection.set_session(
                    autocommit=True, isolation_level=ISOLATION_LEVEL_READ_COMMITTED
                )
                Database.__cursor = Database.__connection.cursor()
            except Exception as e:
                print("Database connection failed with error: ", e)
        else:
            print("Connection established")

    @classmethod
    def get_cursor(cls) -> RealDictCursor:
        """
        Get the database cursor
        """
        if cls.__cursor is None:
            raise Exception("Database connection failed")
        return cls.__cursor

    @classmethod
    def get_connection(cls):
        """
        Get the database connection
        """
        return cls.__connection

    def init_db(self):
        """
        Initialize the database
        """

        if self.get_connection() is not None:
            with current_app.open_resource("models/schema.sql") as f:
                self.executeSchema()
                return self
        else:
            Database.__connection = None
            Database.__cursor = None

    def executeSchema(self):
        """
        Execute the schema
        """
        with current_app.open_resource("models/schema.sql") as f:
            self.get_cursor().execute(f.read().decode("utf8"))

    @classmethod
    def close_db(cls):
        """
        Close the database connection
        """
        cls.__cursor.close() if cls.__cursor is not None else None
        cls.__connection.close() if cls.__connection is not None else None
        cls.__connection = None
        cls.__cursor = None

        print("Database connection closed")


db_connection = Database().init_db()
