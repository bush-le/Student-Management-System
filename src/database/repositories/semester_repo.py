from database.repository import BaseRepository
from models.academic.semester import Semester

class SemesterRepository(BaseRepository):
    def get_all(self, search_query=None):
        sql = "SELECT * FROM Semesters"
        params = []
        if search_query:
            sql += " WHERE name LIKE %s"
            params.append(f"%{search_query}%")
        sql += " ORDER BY start_date DESC"
        return [Semester.from_db_row(row) for row in self.execute_query(sql, tuple(params), fetch_all=True)]

    def get_by_id(self, semester_id):
        sql = "SELECT * FROM Semesters WHERE semester_id = %s"
        row = self.execute_query(sql, (semester_id,), fetch_one=True)
        return Semester.from_db_row(row) if row else None

    def get_active(self):
        """Get the current active semester (OPEN)"""
        sql = "SELECT * FROM Semesters WHERE status = 'OPEN' ORDER BY start_date DESC LIMIT 1"
        row = self.execute_query(sql, fetch_one=True)
        return Semester.from_db_row(row) if row else None

    def add(self, sem):
        try:
            self.execute_query("INSERT INTO Semesters (name, start_date, end_date, status) VALUES (%s, %s, %s, %s)",
                               (sem.name, sem.start_date, sem.end_date, sem.status))
            return True, "Semester created"
        except Exception as e: return False, str(e)

    def update(self, sem):
        try:
            self.execute_query("UPDATE Semesters SET name=%s, start_date=%s, end_date=%s, status=%s WHERE semester_id=%s",
                               (sem.name, sem.start_date, sem.end_date, sem.status, sem.semester_id))
            return True, "Semester updated"
        except Exception as e: return False, str(e)

    def delete(self, sem_id):
        check = self.execute_query("SELECT COUNT(*) as c FROM Course_Classes WHERE semester_id=%s", (sem_id,), fetch_one=True)
        if check['c'] > 0: return False, "Cannot delete: Classes exist in semester"
        try:
            self.execute_query("DELETE FROM Semesters WHERE semester_id=%s", (sem_id,))
            return True, "Semester deleted"
        except Exception as e: return False, str(e)