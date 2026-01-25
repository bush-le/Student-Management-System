from database.repository import BaseRepository
from models.academic.course import Course

class CourseRepository(BaseRepository):
    def get_all(self, page=None, per_page=None, search_query=None):
        sql = "SELECT SQL_CALC_FOUND_ROWS * FROM Courses"
        params = []
        
        if search_query:
            sql += " WHERE (course_code LIKE %s OR course_name LIKE %s) "
            term = f"%{search_query}%"
            params.extend([term, term])
            
        sql += " ORDER BY course_code ASC"
        
        # Add LIMIT OFFSET if pagination is enabled
        if page is not None and per_page is not None:
            offset = (page - 1) * per_page
            sql += " LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            cursor.execute("SELECT FOUND_ROWS() as total")
            total = cursor.fetchone()['total']
            return [Course.from_db_row(row) for row in rows], total
        finally:
            conn.close()

    def get_by_id(self, course_id):
        sql = "SELECT * FROM Courses WHERE course_id = %s"
        row = self.execute_query(sql, (course_id,), fetch_one=True)
        return Course.from_db_row(row) if row else None

    def add(self, course):
        count = self.execute_query("SELECT COUNT(*) as c FROM Courses WHERE course_code = %s", (course.course_code,), fetch_one=True)
        if count['c'] > 0: return False, "Course code exists"
        
        sql = """INSERT INTO Courses (course_code, course_name, credits, course_type, description, prerequisites_id) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        try:
            self.execute_query(sql, (
                course.course_code, 
                course.course_name, 
                course.credits, 
                getattr(course, 'course_type', 'Core'), 
                course.description, 
                course.prerequisites_id
            ))
            return True, "Course created"
        except Exception as e: return False, str(e)

    def update(self, course):
        sql = """UPDATE Courses SET course_code=%s, course_name=%s, credits=%s, course_type=%s, description=%s, prerequisites_id=%s 
                 WHERE course_id=%s"""
        try:
            self.execute_query(sql, (
                course.course_code, 
                course.course_name, 
                course.credits, 
                getattr(course, 'course_type', 'Core'), 
                course.description, 
                course.prerequisites_id, 
                course.course_id
            ))
            return True, "Course updated"
        except Exception as e: return False, str(e)

    def delete(self, course_id):
        check = self.execute_query("SELECT COUNT(*) as c FROM Course_Classes WHERE course_id=%s", (course_id,), fetch_one=True)
        if check and check['c'] > 0: return False, "Cannot delete: Course has active classes"
        try:
            self.execute_query("DELETE FROM Courses WHERE course_id=%s", (course_id,))
            return True, "Course deleted"
        except Exception as e: return False, str(e)

    def count_all(self):
        try:
            result = self.execute_query("SELECT COUNT(*) as total FROM Courses", fetch_one=True)
            return result['total'] if result else 0
        except Exception as e:
            print(f"Error counting courses: {e}")
            return 0