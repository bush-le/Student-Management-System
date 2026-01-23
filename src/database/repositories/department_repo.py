from database.repository import BaseRepository
from models.academic.department import Department

class DepartmentRepository(BaseRepository):
    def get_all(self):
        sql = "SELECT * FROM Departments ORDER BY dept_name ASC"
        return [Department.from_db_row(row) for row in self.execute_query(sql, fetch_all=True)]

    def get_by_id(self, dept_id):
        sql = "SELECT * FROM Departments WHERE dept_id = %s"
        row = self.execute_query(sql, (dept_id,), fetch_one=True)
        return Department.from_db_row(row) if row else None

    def add(self, dept):
        pass # Implement if needed
    def update(self, dept):
        pass
    def delete(self, id):
        pass