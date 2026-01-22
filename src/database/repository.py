from abc import ABC, abstractmethod
from database.connection import DatabaseConnection
import mysql.connector

class BaseRepository(ABC):
    """
    Lớp cha cho các Repository.
    Tận dụng Connection Pooling và Context Manager từ DatabaseConnection.
    """
    
    def __init__(self):
        # Sử dụng class DatabaseConnection của bạn
        self.db = DatabaseConnection

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        Hàm thực thi query chung.
        Sử dụng 'with' để tự động commit/rollback và trả kết nối về pool.
        """
        try:
            # Context Manager của bạn tự động lấy conn, tạo cursor, commit và close
            with self.db.get_cursor(dictionary=True) as cursor:
                cursor.execute(query, params or ())
                
                if fetch_one:
                    return cursor.fetchone()
                
                if fetch_all:
                    return cursor.fetchall()
                
                # Với lệnh INSERT/UPDATE, trả về ID vừa tạo (lastrowid)
                return cursor.lastrowid
                
        except mysql.connector.Error as e:
            # Lỗi sẽ được context manager rollback trước khi văng ra đây
            print(f"Database Error: {e}")
            # Có thể log vào file tại đây nếu muốn
            raise e
        except Exception as e:
            print(f"System Error: {e}")
            raise e

    # --- Các hàm abstract giữ nguyên ---
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