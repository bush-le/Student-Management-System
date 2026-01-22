from database.repository import BaseRepository
from models.academic.semester import Semester

class SemesterRepository(BaseRepository):
    def get_all(self):
        sql = "SELECT * FROM Semesters ORDER BY start_date DESC"
        return [Semester.from_db_row(row) for row in self.execute_query(sql, fetch_all=True)]

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