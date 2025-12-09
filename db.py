import mysql.connector
from mysql.connector import Error

def get_db(auto_commit=False):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Omer2005Omer2005.',
            database='theapp',
            consume_results=True,
            buffered=True,
            autocommit=auto_commit
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL Database: {e}")
        raise e

