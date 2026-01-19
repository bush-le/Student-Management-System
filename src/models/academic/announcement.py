from datetime import datetime

class Announcement:
    def __init__(self, announcement_id, title, content, officer_id, created_date=None):
        self.announcement_id = announcement_id
        self.title = title
        self.content = content
        self.officer_id = officer_id
        self.created_date = created_date if created_date else datetime.now()