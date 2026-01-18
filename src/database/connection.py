import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv("MYSQLHOST") or os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("MYSQLPORT") or os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("MYSQLUSER") or os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME", "student_management_db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_do_not_use_in_prod")

class DatabaseConnection:
    """
    Manages a pool of database connections to ensure efficient reuse.
    """
    _pool = None

    @classmethod
    def get_pool(cls):
        """Initializes and returns the connection pool singleton."""
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="student_management_pool",
                    pool_size=5,
                    host=Config.DB_HOST,
                    port=Config.DB_PORT,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME
                )
            except mysql.connector.Error as err:
                print(f"Error creating connection pool: {err}")
                raise
        return cls._pool

    @classmethod
    def get_connection(cls):
        """Gets a connection from the pool."""
        pool = cls.get_pool()
        return pool.get_connection()

# This block allows the file to be run directly to test the database connection.
if __name__ == "__main__":
    print("Attempting to test database connection...")
    connection = None
    try:
        connection = DatabaseConnection.get_connection()
        if connection.is_connected():
            print(f"Successfully connected to database '{Config.DB_NAME}' on {Config.DB_HOST}:{Config.DB_PORT}.")
    except Exception as e:
        print(f"Failed to connect to the database. Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Connection returned to the pool.")