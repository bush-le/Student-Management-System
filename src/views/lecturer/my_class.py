import customtkinter as ctk
from controllers.lecturer_controller import LecturerController

class LecturerClassesFrame(ctk.CTkFrame):
    def __init__(self, parent, dashboard, user_id):
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard
        self.controller = LecturerController(user_id)
        
        ctk.CTkLabel(self, text="My Assigned Classes", font=("Arial", 20, "bold"), text_color="#111827").pack(anchor="w", pady=(0, 20))
        
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        self.scroll.grid_columnconfigure(0, weight=1)
        self.scroll.grid_columnconfigure(1, weight=1)
        
        self.load_classes()

    def load_classes(self):
        try:
            classes = self.controller.get_teaching_schedule()
            if not classes:
                ctk.CTkLabel(self.scroll, text="No classes found.", text_color="gray").pack(pady=20)
                return
                
            for i, cls in enumerate(classes):
                self.create_card(cls, i // 2, i % 2)
        except: pass

    def create_card(self, data, r, c):
        card = ctk.CTkFrame(self.scroll, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        card.grid(row=r, column=c, sticky="nsew", padx=10, pady=10)
        
        # Header
        h = ctk.CTkFrame(card, fg_color="transparent")
        h.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(h, text=data.get('course_name'), font=("Arial", 16, "bold"), text_color="#0F766E").pack(anchor="w")
        ctk.CTkLabel(h, text=f"ID: {data.get('class_id')}", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        
        # Info
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=20, pady=5)
        
        self._row(info, "Schedule:", data.get('schedule', 'TBA'))
        self._row(info, "Room:", data.get('room', 'TBA'))
        self._row(info, "Students:", f"{data.get('enrolled_count', 0)} / {data.get('max_capacity', 0)}")
        
        # Btn
        btn = ctk.CTkButton(
            card, text="Manage Class", fg_color="#0F766E", hover_color="#115E59", 
            font=("Arial", 13, "bold"), height=40,
            command=lambda: self.dashboard.open_class_manager(data)
        )
        btn.pack(fill="x", padx=20, pady=(15, 20))

    def _row(self, p, lbl, val):
        f = ctk.CTkFrame(p, fg_color="transparent")
        f.pack(fill="x", pady=2)
        ctk.CTkLabel(f, text=lbl, font=("Arial", 12), text_color="gray").pack(side="left")
        ctk.CTkLabel(f, text=val, font=("Arial", 12, "bold"), text_color="#333").pack(side="right")