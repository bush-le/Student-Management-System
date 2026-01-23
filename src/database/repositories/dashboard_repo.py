from database.connection import DatabaseConnection

class DashboardRepository:
    def get_dashboard_stats(self):
        """
        Retrieves dashboard statistics (student, lecturer, course, class counts)
        using a single, efficient database query.
        """
        query = """
            SELECT 'students' as item, COUNT(*) as count FROM students
            UNION ALL
            SELECT 'lecturers' as item, COUNT(*) as count FROM lecturers
            UNION ALL
            SELECT 'courses' as item, COUNT(*) as count FROM courses
            UNION ALL
            SELECT 'classes' as item, COUNT(*) as count FROM course_classes;
        """
        stats = {'students': 0, 'lecturers': 0, 'courses': 0, 'classes': 0}
        try:
            with DatabaseConnection.get_cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                for row in results:
                    stats[row['item']] = row['count']
            return stats
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
            # Return zeroed stats in case of an error
            return stats
