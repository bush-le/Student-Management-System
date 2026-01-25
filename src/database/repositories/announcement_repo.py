from database.repository import BaseRepository
from models.academic.announcement import Announcement

class AnnouncementRepository(BaseRepository):
    def get_all(self, search_query=None):
        sql = "SELECT * FROM Announcements"
        params = []
        if search_query:
            sql += " WHERE title LIKE %s OR content LIKE %s"
            term = f"%{search_query}%"
            params.extend([term, term])
        sql += " ORDER BY created_date DESC"
        return [Announcement.from_db_row(r) for r in self.execute_query(sql, tuple(params), fetch_all=True)]

    def get_recent(self, user_id=None, limit=3):
        if user_id:
            # Lấy thông báo chung (user_id NULL) HOẶC thông báo riêng của user
            sql = "SELECT * FROM Announcements WHERE user_id IS NULL OR user_id = %s ORDER BY created_date DESC LIMIT %s"
            return [Announcement.from_db_row(r) for r in self.execute_query(sql, (user_id, limit), fetch_all=True)]
        
        sql = "SELECT * FROM Announcements WHERE user_id IS NULL ORDER BY created_date DESC LIMIT %s"
        return [Announcement.from_db_row(r) for r in self.execute_query(sql, (limit,), fetch_all=True)]

    def get_by_id(self, ann_id):
        sql = "SELECT * FROM Announcements WHERE announcement_id = %s"
        row = self.execute_query(sql, (ann_id,), fetch_one=True)
        return Announcement.from_db_row(row) if row else None

    def add(self, ann):
        try:
            self.execute_query("INSERT INTO Announcements (title, content, officer_id, created_date) VALUES (%s, %s, %s, NOW())",
                               (ann.title, ann.content, ann.officer_id))
            return True, "Posted"
        except Exception as e: return False, str(e)

    def add_notification(self, user_id, title, content):
        """Tạo thông báo riêng cho một user cụ thể"""
        try:
            self.execute_query("INSERT INTO Announcements (user_id, title, content, created_date) VALUES (%s, %s, %s, NOW())",
                               (user_id, title, content))
            return True, "Notification sent"
        except Exception as e: return False, str(e)

    def update(self, ann):
        try:
            self.execute_query("UPDATE Announcements SET title=%s, content=%s WHERE announcement_id=%s",
                               (ann.title, ann.content, ann.announcement_id))
            return True, "Updated"
        except Exception as e: return False, str(e)

    def delete(self, ann_id):
        try:
            self.execute_query("DELETE FROM Announcements WHERE announcement_id=%s", (ann_id,))
            return True, "Deleted"
        except Exception as e: return False, str(e)