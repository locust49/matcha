import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from flask import current_app

load_dotenv()


class Database:
    __connection = None
    __cursor = None

    def __init__(self, db_name=None):
        """
        Initialize the database
        """
        print("__Initializing__ database with {} : {}".format(
            Database.__connection, db_name))
        if Database.__connection is None:
            try:
                Database.__connection = psycopg2.connect(
                    host=os.getenv("DB_HOST"),
                    user=os.getenv("DB_USERNAME"),
                    password=os.getenv("DB_PASSWORD"),
                    dbname=db_name,
                )
                Database.__connection.set_session(
                    autocommit=True, isolation_level=ISOLATION_LEVEL_READ_COMMITTED
                )
                Database.__cursor = self.__connection.cursor(
                    cursor_factory=RealDictCursor)
            except Exception as e:
                print("Database connection failed with error: ", e)
        else:
            print("Connection established")

    @ classmethod
    def get_cursor(cls):
        """
        Get the database cursor
        """
        return cls.__cursor

    @ classmethod
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
            print("Initializing database")
            with current_app.open_resource("models/schema.sql") as f:
                self.get_cursor().execute(
                    "DROP DATABASE IF EXISTS " + os.getenv("DB_NAME") + ";"
                )
                self.get_cursor().execute(
                    "CREATE DATABASE " + os.getenv("DB_NAME") + ";"
                )
                self.close_db()
                self.__init__(os.getenv("DB_NAME"))
                self.executeSchema()
                return self
        else:
            Database.__connection = None
            Database.__cursor = None
            raise Exception("Database connection failed")

    def executeSchema(self):
        """
        Execute the schema
        """
        with current_app.open_resource("models/schema.sql") as f:
            self.get_cursor().execute(f.read().decode("utf8"))

    @ classmethod
    def close_db(cls):
        """
        Close the database connection
        """
        cls.__cursor.close()
        cls.__connection.close()
        cls.__connection = None
        cls.__cursor = None

        print("Database connection closed")


db_connection = Database().init_db()
