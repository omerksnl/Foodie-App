import os
import mysql.connector
from mysql.connector import Error


def _get_env(key: str, default: str | None = None, required: bool = False) -> str:
    """Fetch an environment variable with optional default/required validation."""
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Environment variable {key} is required but not set")
    return value


def get_db(auto_commit: bool = False):
    """
    Create a MySQL connection using environment variables.
    Required: DB_USER, DB_PASSWORD, DB_NAME
    Optional: DB_HOST (default: localhost)
    """
    try:
        connection = mysql.connector.connect(
            host=_get_env("DB_HOST", "localhost"),
            user=_get_env("DB_USER", required=True),
            password=_get_env("DB_PASSWORD", required=True),
            database=_get_env("DB_NAME", required=True),
            consume_results=True,
            buffered=True,
            autocommit=auto_commit,
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        raise e

