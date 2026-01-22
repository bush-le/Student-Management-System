class Semester:
    def __init__(self, semester_id, name, start_date, end_date, status):
        self.semester_id = semester_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

    @classmethod
    def from_db_row(cls, row):
        if not row: return None
        return cls(
            semester_id=row.get('semester_id'),
            name=row.get('name'),
            start_date=row.get('start_date'),
            end_date=row.get('end_date'),
            status=row.get('status')
        )