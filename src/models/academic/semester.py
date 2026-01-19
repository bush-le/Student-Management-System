class Semester:
    def __init__(self, semester_id, name, start_date, end_date, status="OPEN"):
        self.semester_id = semester_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.status = status # OPEN, CLOSED

    def is_active(self):
        return self.status == "OPEN"