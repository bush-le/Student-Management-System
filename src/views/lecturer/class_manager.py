import customtkinter as ctk
from tkinter import messagebox
from controllers.lecturer_controller import LecturerController

class LecturerClassManager(ctk.CTkFrame):
    def __init__(self, parent, user_id, class_data, on_back_callback):
        super().__init__(parent, fg_color="white")
        self.controller = LecturerController(user_id)
        self.class_data = class_data
        self.on_back = on_back_callback # Hàm để quay lại màn hình trước
        
        self.COLOR_TEAL = "#2A9D8F"
        self.students_data = [] # Cache dữ liệu sinh viên

        # 1. Header (Nút Back + Tên Lớp)
        self.create_header()

        # 2. Tabs (Roster / Grading)
        self.create_tabs()

        # 3. Content Area (Nơi hiển thị Roster hoặc Grading)
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=30, pady=10)

        # Load data sinh viên 1 lần dùng chung
        self.load_student_data()

        # Mặc định hiện Roster
        self.show_roster()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="white", height=50)
        header.pack(fill="x", padx=30, pady=(20, 10))

        # Back Button
        btn_back = ctk.CTkButton(
            header, text="← Back to Classes", 
            fg_color="transparent", text_color="gray", hover_color="#F3F4F6",
            width=100, anchor="w", command=self.on_back
        )
        btn_back.pack(side="left")

        # Class Title
        title = f"{self.class_data.get('course_name')} ({self.class_data.get('class_id')})"
        ctk.CTkLabel(header, text=title, font=("Arial", 18, "bold"), text_color="#333").pack(side="left", padx=20)

    def create_tabs(self):
        tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_frame.pack(fill="x", padx=30, pady=(0, 10))

        # Tab Buttons
        self.btn_roster = self._create_tab_btn(tab_frame, "Class Roster", self.show_roster)
        self.btn_grading = self._create_tab_btn(tab_frame, "📊 Grading", self.show_grading)

        # Line separator
        ctk.CTkFrame(self, height=2, fg_color="#E5E7EB").pack(fill="x", padx=30)

    def _create_tab_btn(self, parent, text, command):
        btn = ctk.CTkButton(
            parent, text=text, 
            fg_color="transparent", text_color="gray", 
            hover_color="#E0F2F1", font=("Arial", 14, "bold"),
            width=120, height=35, corner_radius=0,
            command=command
        )
        btn.pack(side="left", padx=(0, 10))
        return btn

    def load_student_data(self):
        # Gọi controller lấy danh sách sinh viên và điểm
        try:
            self.students_data = self.controller.get_class_student_list(self.class_data['class_id'])
        except Exception as e:
            print(f"Error: {e}")
            self.students_data = []

    # --- VIEW SWITCHING LOGIC ---
    def _reset_tabs(self):
        self.btn_roster.configure(text_color="gray", fg_color="transparent")
        self.btn_grading.configure(text_color="gray", fg_color="transparent")
        # Xóa nội dung cũ
        for widget in self.content_area.winfo_children(): widget.destroy()

    def show_roster(self):
        self._reset_tabs()
        # Highlight Roster Tab (Style gạch chân giả lập bằng màu teal)
        self.btn_roster.configure(text_color=self.COLOR_TEAL)
        
        # Load View
        RosterView(self.content_area, self.students_data).pack(fill="both", expand=True)

    def show_grading(self):
        self._reset_tabs()
        # Highlight Grading Tab
        self.btn_grading.configure(text_color=self.COLOR_TEAL)
        
        # Load View
        GradingView(self.content_area, self.controller, self.class_data['class_id'], self.students_data).pack(fill="both", expand=True)


# ==========================================
# SUB-VIEW: CLASS ROSTER (Image 7.3.4)
# ==========================================
class RosterView(ctk.CTkFrame):
    def __init__(self, parent, students):
        super().__init__(parent, fg_color="white")
        
        # Search Bar
        search_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", border_width=1, border_color="#E5E7EB")
        search_frame.pack(fill="x", pady=(0, 20), ipady=5)
        ctk.CTkLabel(search_frame, text="🔍", text_color="gray").pack(side="left", padx=10)
        ctk.CTkEntry(search_frame, placeholder_text="Search students by name, ID...", border_width=0, fg_color="transparent", width=300).pack(side="left")

        # Table Header
        self.create_table_header()

        # Student List
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        if not students:
            ctk.CTkLabel(scroll, text="No students enrolled.").pack(pady=20)
        
        for stu in students:
            self.create_student_row(scroll, stu)

    def create_table_header(self):
        headers = ["ID", "FULL NAME", "EMAIL", "STATUS"]
        h_frame = ctk.CTkFrame(self, fg_color="#F3F4F6", height=40)
        h_frame.pack(fill="x")
        
        # Grid config
        h_frame.grid_columnconfigure(0, weight=1) # ID
        h_frame.grid_columnconfigure(1, weight=3) # Name
        h_frame.grid_columnconfigure(2, weight=3) # Email
        h_frame.grid_columnconfigure(3, weight=1) # Status

        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, font=("Arial", 11, "bold"), text_color="gray", anchor="w").grid(row=0, column=i, sticky="ew", padx=10, pady=10)

    def create_student_row(self, parent, data):
        row = ctk.CTkFrame(parent, fg_color="white", border_width=0)
        row.pack(fill="x", pady=1)
        
        # Grid config matching header
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=3)
        row.grid_columnconfigure(2, weight=3)
        row.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(row, text=data['student_id'], font=("Arial", 12, "bold"), text_color="#2A9D8F", anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(row, text=data['full_name'], font=("Arial", 12, "bold"), anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=f"{data['student_code']}@university.edu", text_color="gray", anchor="w").grid(row=0, column=2, sticky="ew", padx=10)
        
        # Status Badge
        status_frame = ctk.CTkFrame(row, fg_color="#DCFCE7", corner_radius=10, height=25)
        status_frame.grid(row=0, column=3, padx=10, sticky="w")
        ctk.CTkLabel(status_frame, text="Active", text_color="#166534", font=("Arial", 10, "bold")).pack(padx=10, pady=2)
        
        ctk.CTkFrame(parent, height=1, fg_color="#F3F4F6").pack(fill="x") # Separator line


# ==========================================
# SUB-VIEW: GRADING INTERFACE (Image 7.3.5)
# ==========================================
class GradingView(ctk.CTkFrame):
    def __init__(self, parent, controller, class_id, students):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.class_id = class_id
        self.students = students
        self.entry_refs = {} # Lưu tham chiếu các ô nhập điểm {student_id: {mid: entry, final: entry...}}

        # Actions Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(toolbar, text="Lock Grades", fg_color="white", text_color="#333", border_width=1, border_color="#E5E7EB", width=100).pack(side="right", padx=10)
        ctk.CTkButton(toolbar, text="Save Grades", fg_color="#10B981", hover_color="#059669", width=100, command=self.save_all_grades).pack(side="right")

        # Table Header
        self.create_table_header()

        # Students List with Inputs
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for stu in students:
            self.create_grading_row(scroll, stu)

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", height=45)
        h_frame.pack(fill="x")
        
        cols = [
            ("STUDENT ID", 1.5, "w"), ("NAME", 3, "w"), 
            ("ATTENDANCE\n(10%)", 1.2, "center"), ("MIDTERM\n(30%)", 1.2, "center"), 
            ("FINAL EXAM\n(60%)", 1.2, "center"), ("TOTAL", 1, "center")
        ]
        
        for i, (text, w, anchor) in enumerate(cols):
            h_frame.grid_columnconfigure(i, weight=int(w*10))
            ctk.CTkLabel(h_frame, text=text, font=("Arial", 10, "bold"), text_color="gray", anchor=anchor).grid(row=0, column=i, sticky="ew", padx=5, pady=5)

    def create_grading_row(self, parent, data):
        row = ctk.CTkFrame(parent, fg_color="white")
        row.pack(fill="x", pady=2)
        
        # Grid config matching header weights (approx)
        weights = [15, 30, 12, 12, 12, 10]
        for i, w in enumerate(weights): row.grid_columnconfigure(i, weight=w)

        # 1. Info
        ctk.CTkLabel(row, text=data['student_id'], text_color="gray", anchor="w").grid(row=0, column=0, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=data['full_name'], font=("Arial", 12, "bold"), anchor="w").grid(row=0, column=1, sticky="ew", padx=5)

        # 2. Inputs Helper
        def create_input(col, key, default_val):
            ent = ctk.CTkEntry(row, width=60, justify="center", border_color="#E5E7EB")
            ent.insert(0, str(default_val) if default_val is not None else "")
            ent.grid(row=0, column=col, padx=5, pady=10)
            return ent

        # 3. Create Inputs & Store Refs
        # Lấy điểm hiện tại từ data (nếu có)
        att = data.get('attendance_score')
        mid = data.get('midterm')
        fin = data.get('final')
        tot = data.get('total')

        entry_att = create_input(2, 'att', att)
        entry_mid = create_input(3, 'mid', mid)
        entry_fin = create_input(4, 'fin', fin)

        # Total Label (Tự động tính hoặc hiển thị từ DB)
        lbl_total = ctk.CTkLabel(row, text=str(tot) if tot is not None else "-", font=("Arial", 12, "bold"), text_color="#DC2626")
        lbl_total.grid(row=0, column=5)

        # Lưu tham chiếu để nút Save lấy dữ liệu
        self.entry_refs[data['student_id']] = {
            'att': entry_att, 'mid': entry_mid, 'fin': entry_fin, 'total_lbl': lbl_total
        }
        
        ctk.CTkFrame(parent, height=1, fg_color="#F3F4F6").pack(fill="x")

    def save_all_grades(self):
        success_count = 0
        error_count = 0

        for student_id, widgets in self.entry_refs.items():
            try:
                # Lấy dữ liệu từ ô nhập
                s_att = widgets['att'].get()
                s_mid = widgets['mid'].get()
                s_fin = widgets['fin'].get()

                # Skip nếu để trống toàn bộ (hoặc xử lý tùy logic)
                if not s_att and not s_mid and not s_fin: continue

                # Convert float
                val_att = float(s_att) if s_att else 0.0
                val_mid = float(s_mid) if s_mid else 0.0
                val_fin = float(s_fin) if s_fin else 0.0

                # Gọi Controller cập nhật
                # input_grade(student_id, class_id, attendance, midterm, final)
                ok, msg = self.controller.input_grade(student_id, self.class_id, val_att, val_mid, val_fin)
                
                if ok: 
                    success_count += 1
                    # Cập nhật tạm thời label Total (Logic đơn giản để UI phản hồi ngay)
                    # Total = 10% + 30% + 60%
                    new_total = (val_att * 0.1) + (val_mid * 0.3) + (val_fin * 0.6)
                    widgets['total_lbl'].configure(text=f"{new_total:.1f}")
                else:
                    print(f"Failed {student_id}: {msg}")
                    error_count += 1

            except ValueError:
                error_count += 1
                print(f"Invalid format for student {student_id}")

        if error_count == 0:
            messagebox.showinfo("Success", f"Saved grades for {success_count} students.")
        else:
            messagebox.showwarning("Partial Save", f"Saved: {success_count}, Errors: {error_count}. Check inputs.")