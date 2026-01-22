from database.repository import BaseRepository
from models.academic.announcement import Announcement

class AnnouncementRepository(BaseRepository):
    def get_all(self):
        return [Announcement.from_db_row(r) for r in self.execute_query("SELECT * FROM Announcements ORDER BY created_date DESC", fetch_all=True)]

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