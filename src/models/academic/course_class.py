class CourseClass:
    """
    Represents a specific class section offered in a semester.
    """
    def __init__(self, class_id, course_id, lecturer_id, semester_id, room, schedule, max_capacity, enrolled_count=0):
        self.class_id = class_id
        self.course_id = course_id
        self.lecturer_id = lecturer_id
        self.semester_id = semester_id
        self.room = room        
        self.schedule = schedule
        self.max_capacity = max_capacity
        self.enrolled_count = enrolled_count

    def is_full(self):
        """Check if the class is full (FR-16)"""
        return self.enrolled_count >= self.max_capacity