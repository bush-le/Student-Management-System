class Course:
    def __init__(self, course_id, course_code, course_name, credits, dept_id, description="", prerequisite_id=None):
        self.course_id = course_id
        self.course_code = course_code # Course Code (e.g., CS101)
        self.course_name = course_name
        self.credits = int(credits)
        self.dept_id = dept_id
        self.description = description
        self.prerequisite_id = prerequisite_id # Prerequisite course ID (if any)