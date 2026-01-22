class Course:
    def __init__(self, course_id, course_code, course_name, credits, course_type, description, prerequisites_str):
        self.course_id = course_id
        self.course_code = course_code
        self.course_name = course_name
        self.credits = credits
        self.course_type = course_type
        self.description = description
        self.prerequisites_str = prerequisites_str

    @classmethod
    def from_db_row(cls, row):
        if not row: return None
        return cls(
            course_id=row.get('course_id'),
            course_code=row.get('course_code'),
            course_name=row.get('course_name'),
            credits=row.get('credits'),
            course_type=row.get('course_type'),
            description=row.get('description'),
            prerequisites_str=row.get('prerequisites_str')
        )