import psycopg2
import os
from dotenv import load_dotenv
from flask import current_app, g
import click

load_dotenv()


class Database:
    def __init__(self):
        self.__connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
        )
        self.__cursor = self.__connection.cursor()
        g.db = self.__connection

    def get_db(self):
        """
        Get the database connection
        """
        if "db" not in g:
            g.db = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USERNAME"),
                password=os.getenv("DB_PASSWORD"),
            )
        return g.db

    def close_db(self, e=None):
        """
        Close the database connection
        """
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def get_cursor(self):
        """
        Get the database cursor
        """
        return self.__cursor

    def init_db(self):
        """
        Initialize the database
        """
        db = self.get_db()

        with current_app.open_resource("models/schema.sql") as f:
            db.cursor().execute(f.read().decode("utf8"))
            db.commit()
