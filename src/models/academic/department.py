class Department:
    def __init__(self, dept_id, dept_name, office_location=None, phone=None):
        self.dept_id = dept_id
        self.dept_name = dept_name
        self.office_location = office_location
        self.phone = phone

    @classmethod
    def from_db_row(cls, row):
        if not row: return None
        return cls(
            dept_id=row.get('dept_id'),
            dept_name=row.get('dept_name'),
            office_location=row.get('office_location'),
            phone=row.get('phone')
        )