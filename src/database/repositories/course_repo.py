from database.repository import BaseRepository
from models.academic.course import Course

class CourseRepository(BaseRepository):
    def get_all(self):
        sql = "SELECT * FROM Courses ORDER BY course_code ASC"
        return [Course.from_db_row(row) for row in self.execute_query(sql, fetch_all=True)]

    def add(self, course):
        count = self.execute_query("SELECT COUNT(*) as c FROM Courses WHERE course_code = %s", (course.course_code,), fetch_one=True)
        if count['c'] > 0: return False, "Course code exists"
        
        sql = """INSERT INTO Courses (course_code, course_name, credits, course_type, description, prerequisites_str) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        try:
            self.execute_query(sql, (course.course_code, course.course_name, course.credits, course.course_type, course.description, course.prerequisites_str))
            return True, "Course created"
        except Exception as e: return False, str(e)

    def update(self, course):
        sql = """UPDATE Courses SET course_code=%s, course_name=%s, credits=%s, course_type=%s, description=%s, prerequisites_str=%s 
                 WHERE course_id=%s"""
        try:
            self.execute_query(sql, (course.course_code, course.course_name, course.credits, course.course_type, course.description, course.prerequisites_str, course.course_id))
            return True, "Course updated"
        except Exception as e: return False, str(e)

    def delete(self, course_id):
        check = self.execute_query("SELECT COUNT(*) as c FROM Course_Classes WHERE course_id=%s", (course_id,), fetch_one=True)
        if check['c'] > 0: return False, "Cannot delete: Course has active classes"
        try:
            self.execute_query("DELETE FROM Courses WHERE course_id=%s", (course_id,))
            return True, "Course deleted"
        except Exception as e: return False, str(e)