from .user import User

class AcademicOfficer(User):
    def __init__(self, user_data, officer_id, admin_code):
        super().__init__(**user_data)
        self.officer_id = officer_id
        self.admin_code = admin_code