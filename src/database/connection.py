import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
from config import Config


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
                    pool_size=15,
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

    @classmethod
    @contextmanager
    def get_cursor(cls, dictionary=True):
        """
        A context manager to safely handle database connections, cursors, and transactions.
        It automatically commits on success, rolls back on error, and always
        returns the connection to the pool.

        Usage:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute("UPDATE ...") # Writes are automatically committed.
        """
        connection = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor(dictionary=dictionary)
            yield cursor
            connection.commit()  # Commit transaction if block executes successfully
        except Exception as e:
            if connection:
                connection.rollback()  # Rollback on any error within the block
            raise e  # Re-raise the exception to the caller
        finally:
            if connection:
                connection.close()  # This returns the connection to the pool

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