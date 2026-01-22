from abc import ABC, abstractmethod
from database.connection import DatabaseConnection
import mysql.connector

class BaseRepository(ABC):
    """
    Lớp trừu tượng cơ sở cho tất cả các Repository.
    Cung cấp các phương thức chung để thao tác với database.
    """
    
    def __init__(self):
        # Sử dụng singleton connection từ class DatabaseConnection cũ của bạn
        self.db = DatabaseConnection

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        Hàm helper để thực thi query an toàn, tự động đóng cursor.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor(dictionary=True) # Luôn trả về dict để dễ map vào Model
        try:
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
                return result
            
            if fetch_all:
                result = cursor.fetchall()
                return result
            
            conn.commit()
            return cursor.lastrowid # Trả về ID vừa insert (nếu có)
            
        except mysql.connector.Error as e:
            print(f"Database Error: {e}")
            conn.rollback()
            raise e # Ném lỗi ra để Controller xử lý thông báo
        finally:
            cursor.close()
            conn.close()

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