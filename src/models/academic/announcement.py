class Announcement:
    def __init__(self, announcement_id, title, content, created_date, officer_id):
        self.announcement_id = announcement_id
        self.title = title
        self.content = content
        self.created_date = created_date
        self.officer_id = officer_id

    @classmethod
    def from_db_row(cls, row):
        if not row: return None
        return cls(
            announcement_id=row.get('announcement_id'),
            title=row.get('title'),
            content=row.get('content'),
            created_date=row.get('created_date'),
            officer_id=row.get('officer_id')
        )