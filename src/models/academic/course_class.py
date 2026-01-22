class CourseClass:
    def __init__(self, class_id, course_id, semester_id, room, schedule, max_capacity, lecturer_id=None, 
                 course_name=None, lecturer_name=None, current_enrolled=0):
        self.class_id = class_id
        self.course_id = course_id
        self.semester_id = semester_id
        self.room = room
        self.schedule = schedule
        self.max_capacity = max_capacity
        self.lecturer_id = lecturer_id
        # Fields mở rộng để hiển thị
        self.course_name = course_name
        self.lecturer_name = lecturer_name
        self.current_enrolled = current_enrolled

    @classmethod
    def from_db_row(cls, row):
        if not row: return None
        return cls(
            class_id=row.get('class_id'),
            course_id=row.get('course_id'),
            semester_id=row.get('semester_id'),
            room=row.get('room'),
            schedule=row.get('schedule'),
            max_capacity=row.get('max_capacity'),
            lecturer_id=row.get('lecturer_id'),
            course_name=row.get('course_name'),
            lecturer_name=row.get('lecturer_name'),
            current_enrolled=row.get('current_enrolled', 0)
        )