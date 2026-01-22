import customtkinter as ctk
from controllers.lecturer_controller import LecturerController

class LecturerClassesFrame(ctk.CTkFrame):
    def __init__(self, parent, dashboard, user_id):
        super().__init__(parent, fg_color="white")
        self.dashboard = dashboard 
        self.controller = LecturerController(user_id)
        
        # --- MÀU SẮC ---
        self.COLOR_TEAL = "#2A9D8F"
        self.COLOR_TEXT_MAIN = "#333"
        self.COLOR_TEXT_SUB = "gray"

        # 1. Header
        ctk.CTkLabel(self, text="MY ASSIGNED CLASSES", font=("Arial", 16, "bold"), text_color=self.COLOR_TEAL).pack(anchor="w", padx=30, pady=(20, 10))
        ctk.CTkFrame(self, height=2, fg_color="#E5E7EB").pack(fill="x", padx=30, pady=(0, 20))

        # 2. Container (Scrollable)
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Grid Layout cho Cards (2 cột)
        self.scroll_area.grid_columnconfigure(0, weight=1)
        self.scroll_area.grid_columnconfigure(1, weight=1)

        # 3. Load Data & Render
        self.load_classes()

    def load_classes(self):
        try:
            # Lấy danh sách lớp từ Controller (Reuse hàm get_teaching_schedule)
            classes = self.controller.get_teaching_schedule()
        except Exception as e:
            print(f"Error loading classes: {e}")
            classes = []

        if not classes:
            ctk.CTkLabel(self.scroll_area, text="No assigned classes found.", font=("Arial", 14), text_color="gray").pack(pady=40)
            return

        for i, cls in enumerate(classes):
            row = i // 2
            col = i % 2
            self.create_class_card(cls, row, col)

    def create_class_card(self, data, r, c):
        # Card Container
        card = ctk.CTkFrame(self.scroll_area, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        card.grid(row=r, column=c, sticky="nsew", padx=10, pady=10)
        
        # --- HEADER CARD ---
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        # Tên môn
        ctk.CTkLabel(header, text=data.get('course_name', 'Unknown'), font=("Arial", 16, "bold"), text_color=self.COLOR_TEAL).pack(anchor="w")
        
        # Mã môn & Term
        sub_header = ctk.CTkFrame(header, fg_color="transparent")
        sub_header.pack(fill="x", pady=(5, 0))
        # Giả sử class_id là mã lớp
        ctk.CTkLabel(sub_header, text=f"ID: {data.get('class_id')}", font=("Arial", 12, "bold"), text_color="#9CA3AF").pack(side="left")
        
        # Tag học kỳ (Giả lập vì DB chưa có cột Term)
        term_lbl = ctk.CTkLabel(sub_header, text="FALL 2024", font=("Arial", 10, "bold"), text_color="#2A9D8F", fg_color="#E0F2F1", corner_radius=4)
        term_lbl.pack(side="right") # padx dùng trong pack của label chứ ko phải frame

        # --- INFO SECTION ---
        info_box = ctk.CTkFrame(card, fg_color="transparent")
        info_box.pack(fill="x", padx=20, pady=5)

        # Enrolled
        curr = data.get('enrolled_count', 0)
        max_cap = data.get('max_capacity', 50)
        self._info_row(info_box, "Enrolled:", f"{curr} / {max_cap}")

        # Schedule
        sched = data.get('schedule', 'TBA')
        self._info_row(info_box, "Schedule:", sched)

        # Room
        room = data.get('room', 'TBA')
        self._info_row(info_box, "Room:", room, is_bold_val=True)

        # --- ACTION BUTTON ---
        btn = ctk.CTkButton(
            card, 
            text="Manage Class", 
            fg_color=self.COLOR_TEAL, 
            hover_color="#238b7e",
            height=40,
            font=("Arial", 13, "bold"),
            command=lambda d=data: self.dashboard.open_class_manager(d)
        )
        btn.pack(fill="x", padx=20, pady=(20, 20))

    def _info_row(self, parent, label, value, is_bold_val=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row, text=label, font=("Arial", 12), text_color="gray").pack(side="left")
        
        font = ("Arial", 12, "bold") if is_bold_val else ("Arial", 12)
        color = "#333" if is_bold_val else "#4B5563"
        ctk.CTkLabel(row, text=value, font=font, text_color=color).pack(side="right")