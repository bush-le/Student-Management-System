import customtkinter as ctk
from controllers.student_controller import StudentController

class GradesFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.controller = StudentController(user_id)

        # Header
        ctk.CTkLabel(self, text="My Academic Results", font=("Arial", 24, "bold"), text_color="#333").pack(anchor="w", pady=(0, 20))

        # [cite_start]GPA Summary Box [cite: 1049-1050]
        summary = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        summary.pack(fill="x", pady=(0, 20), ipady=10)
        
        # Lấy dữ liệu
        grades_data = self.controller.view_grades()
        # Tính GPA giả định
        current_gpa = "3.65" # Logic tính toán thực tế nằm ở controller

        ctk.CTkLabel(summary, text=f"Cumulative GPA: {current_gpa}", font=("Arial", 20, "bold"), text_color="#2A9D8F").pack(side="left", padx=20)
        ctk.CTkLabel(summary, text="Classification: Excellent", font=("Arial", 14), text_color="gray").pack(side="left", padx=20)

        # Bảng Điểm (Scrollable)
        table_frame = ctk.CTkScrollableFrame(self, fg_color="white", label_text="Course Performance")
        table_frame.pack(fill="both", expand=True)

        # Table Header
        headers = ["Course Name", "Credits", "Midterm (30%)", "Final (60%)", "Total", "Grade"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(table_frame, text=h, font=("Arial", 12, "bold"), width=120, anchor="w").grid(row=0, column=i, padx=5, pady=10)

        # Table Rows
        if grades_data:
            for idx, row in enumerate(grades_data, start=1):
                # row keys: course_name, credits, midterm, final, total, letter_grade
                vals = [row['course_name'], str(row['credits']), str(row['midterm']), str(row['final']), str(row['total']), row['letter_grade']]
                
                for col, val in enumerate(vals):
                    color = "#2A9D8F" if col == 5 else "black" # Tô màu điểm chữ
                    font = ("Arial", 12, "bold") if col == 5 else ("Arial", 12)
                    
                    ctk.CTkLabel(table_frame, text=val if val != "None" else "-", font=font, text_color=color, width=120, anchor="w").grid(row=idx, column=col, padx=5, pady=5)
                    
                # Kẻ dòng (Optional separator)
                separator = ctk.CTkFrame(table_frame, height=1, fg_color="#E0E0E0")
                separator.grid(row=idx, column=0, columnspan=6, sticky="ew")
        else:
             ctk.CTkLabel(table_frame, text="No grade records found.").grid(row=1, column=0, columnspan=6, pady=20)