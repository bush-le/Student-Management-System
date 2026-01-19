import customtkinter as ctk
from controllers.student_controller import StudentController

class ScheduleFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.controller = StudentController(user_id)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="white", height=60)
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Weekly Schedule", font=("Arial", 20, "bold"), text_color="#2A9D8F").pack(side="left", padx=20)
        ctk.CTkButton(header, text="Current Week", width=100, fg_color="#264653").pack(side="right", padx=20, pady=10)

        # Lấy dữ liệu từ Controller
        schedule_data = self.controller.view_schedule()
        [cite_start]# [cite: 1045] Data gồm: course_name, room, schedule, lecturer_code

        # Tạo Grid 7 ngày (Minh họa)
        self.grid_container = ctk.CTkFrame(self, fg_color="white")
        self.grid_container.pack(fill="both", expand=True)

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for i, day in enumerate(days):
            self.grid_container.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(self.grid_container, text=day, font=("Arial", 14, "bold"), fg_color="#E0E0E0", corner_radius=5).grid(row=0, column=i, sticky="ew", padx=2, pady=2)

        # Render các lớp học (Demo logic hiển thị)
        if schedule_data:
            for cls in schedule_data:
                # Giả sử cls['schedule'] có dạng "Monday 07:00-09:00"
                # Cần logic parse string để biết đặt vào cột nào. Ở đây demo tĩnh.
                day_str = cls['schedule'].split()[0] # Lấy "Monday"
                if day_str in days:
                    col_idx = days.index(day_str)
                    
                    card = ctk.CTkFrame(self.grid_container, fg_color="#E9F5F3", border_color="#2A9D8F", border_width=2)
                    card.grid(row=1, column=col_idx, padx=5, pady=5, sticky="ew")
                    
                    ctk.CTkLabel(card, text=cls['course_name'], font=("Arial", 12, "bold"), wraplength=100).pack(pady=5)
                    ctk.CTkLabel(card, text=f"📍 {cls['room']}", font=("Arial", 10)).pack()
                    ctk.CTkLabel(card, text=f"🕒 {cls['schedule'].split(' ', 1)[1]}", font=("Arial", 10)).pack(pady=(0,5))
        else:
             ctk.CTkLabel(self.grid_container, text="No classes scheduled.", text_color="gray").grid(row=1, column=0, columnspan=6, pady=20)