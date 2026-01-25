class Course:
    def __init__(self, course_id, course_code, course_name, credits, description, prerequisite_id, prerequisite_code=None):
        self.course_id = course_id
        self.course_code = course_code
        self.course_name = course_name
        self.credits = credits
        self.description = description
        self.prerequisite_id = prerequisite_id
        self.prerequisite_code = prerequisite_code

    @classmethod
    def from_db_row(cls, row):
        if not row: return None
        return cls(
            course_id=row.get('course_id'),
            course_code=row.get('course_code'),
            course_name=row.get('course_name'),
            credits=row.get('credits'),
            description=row.get('description'),
            prerequisite_id=row.get('prerequisite_id'),
            prerequisite_code=row.get('prerequisite_code')
        )