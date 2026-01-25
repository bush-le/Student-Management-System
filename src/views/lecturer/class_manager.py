import customtkinter as ctk
from views.lecturer.grading import GradingView
from controllers.lecturer_controller import LecturerController
from utils.threading_helper import run_in_background

class LecturerClassManager(ctk.CTkFrame):
    def __init__(self, parent, controller, class_data, on_back_callback):
        super().__init__(parent, fg_color="#F3F4F6")
        self.class_data = class_data
        self.on_back = on_back_callback
        self.controller = controller
        
        # --- HEADER ---
        h = ctk.CTkFrame(self, fg_color="transparent", height=50)
        h.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(
            h, text="< Back", fg_color="white", text_color="#333", 
            hover_color="#E5E7EB", width=80, 
            command=on_back_callback
        ).pack(side="left")
        
        title = f"{class_data.get('course_name')} ({class_data.get('class_id')})"
        ctk.CTkLabel(h, text=title, font=("Arial", 18, "bold"), text_color="#111827").pack(side="left", padx=20)

        # --- TABS ---
        tabs = ctk.CTkFrame(self, fg_color="transparent")
        tabs.pack(fill="x", pady=(0, 10))
        self.btn_grad = self._tab_btn(tabs, "Grading Sheet", self.show_grading)
        self.btn_rost = self._tab_btn(tabs, "Class Roster", self.show_roster)

        # --- CONTENT AREA ---
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True)
        
        self.show_grading()

    def _tab_btn(self, p, txt, cmd):
        btn = ctk.CTkButton(p, text=txt, fg_color="white", text_color="#333", hover_color="#E5E7EB", width=150, command=cmd)
        btn.pack(side="left", padx=(0, 10))
        return btn

    def show_grading(self):
        for w in self.content.winfo_children(): w.destroy()
        self.btn_grad.configure(fg_color="#0F766E", text_color="white")
        self.btn_rost.configure(fg_color="white", text_color="#333")
        GradingView(self.content, self.controller, self.class_data).pack(fill="both", expand=True)

    def show_roster(self):
        for w in self.content.winfo_children(): w.destroy()
        self.btn_rost.configure(fg_color="#0F766E", text_color="white")
        self.btn_grad.configure(fg_color="white", text_color="#333")
        
        # --- ROSTER VIEW ---
        # Header
        h = ctk.CTkFrame(self.content, fg_color="#F9FAFB", height=40)
        h.pack(fill="x", padx=20, pady=(10, 5))
        
        cols = [("ID", 100), ("Full Name", 250), ("Email", 250), ("Status", 100)]
        for txt, w in cols:
            f = ctk.CTkFrame(h, fg_color="transparent", width=w, height=40)
            f.pack(side="left", padx=5)
            f.pack_propagate(False)
            ctk.CTkLabel(f, text=txt, font=("Arial", 11, "bold"), text_color="#374151", anchor="w").place(relx=0, rely=0.5, anchor="w")

        # List
        scroll = ctk.CTkFrame(self.content, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(scroll, text="Loading roster...", text_color="gray").pack(pady=20)

        run_in_background(
            lambda: self.controller.get_class_student_list(self.class_data['class_id']),
            lambda students: self._render_roster_list(scroll, students),
            tk_root=self.winfo_toplevel()
        )

    def _render_roster_list(self, scroll, students):
        if not self.winfo_exists(): return
        for w in scroll.winfo_children(): w.destroy()
        
        if not students:
            ctk.CTkLabel(scroll, text="No students enrolled.", text_color="gray").pack(pady=20)
            return

        try:
            for i, s in enumerate(students):
                bg = "white" if i % 2 == 0 else "#F9FAFB"
                row = ctk.CTkFrame(scroll, fg_color=bg, height=40)
                row.pack(fill="x", pady=1)
                
                # ID
                self._cell(row, str(s.get('student_code') or s.get('student_id')), 100)
                # Name
                self._cell(row, s.get('full_name', 'Unknown'), 250)
                # Email 
                self._cell(row, s.get('email', '---'), 250)
                # Status 
                self._cell(row, "Enrolled", 100, color="#059669")

        except Exception as e:
            ctk.CTkLabel(scroll, text=f"Error loading roster: {e}", text_color="red").pack(pady=20)

    def _cell(self, parent, text, width, color="#333"):
        f = ctk.CTkFrame(parent, fg_color="transparent", width=width, height=40)
        f.pack(side="left", padx=5)
        f.pack_propagate(False)
        ctk.CTkLabel(f, text=text, font=("Arial", 12), text_color=color, anchor="w").place(relx=0, rely=0.5, anchor="w")