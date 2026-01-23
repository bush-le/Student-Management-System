from abc import ABC, abstractmethod
from database.connection import DatabaseConnection
import mysql.connector

class BaseRepository(ABC): 
    def __init__(self):
        self.db = DatabaseConnection

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        try:
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                
                if fetch_one:
                    return cursor.fetchone()
                
                if fetch_all:
                    return cursor.fetchall()
                
                return cursor.lastrowid
                
        except mysql.connector.Error as e:
            print(f"Database Error: {e}")
            raise e
        except Exception as e:
            print(f"System Error: {e}")
            raise e

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def get_by_id(self, id):
        pass

    @abstractmethod
    def add(self, entity):
        pass

    @abstractmethod
    def update(self, entity):
        pass

    @abstractmethod
    def delete(self, id):
        pass