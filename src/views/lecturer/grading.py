import customtkinter as ctk
from tkinter import messagebox
from controllers.lecturer_controller import LecturerController

class GradingView(ctk.CTkFrame):
    def __init__(self, parent, user_id, class_data):
        super().__init__(parent, fg_color="white", corner_radius=10)
        self.controller = LecturerController(user_id)
        self.class_id = class_data['class_id']
        self.entries = {}
        
        # Tools
        t = ctk.CTkFrame(self, fg_color="transparent", height=50)
        t.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(t, text="Enter Grades (0-10)", font=("Arial", 12), text_color="gray").pack(side="left")
        ctk.CTkButton(t, text="Save Grades", fg_color="#0F766E", width=120, command=self.save).pack(side="right")

        # Table Header
        cols = [("ID", 80), ("Name", 200), ("Att (10%)", 100), ("Mid (40%)", 100), ("Final (50%)", 100), ("Total", 80)]
        h = ctk.CTkFrame(self, fg_color="#F9FAFB", height=40)
        h.pack(fill="x", padx=20)
        for i, (txt, w) in enumerate(cols):
            f = ctk.CTkFrame(h, fg_color="transparent", width=w, height=40)
            f.pack(side="left", padx=2)
            f.pack_propagate(False)
            ctk.CTkLabel(f, text=txt, font=("Arial", 11, "bold"), text_color="#374151").place(relx=0, rely=0.5, anchor="w")

        # List
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        self.load_students()

    def load_students(self):
        try:
            students = self.controller.get_class_students(self.class_id)
            for s in students: self.create_row(s)
        except: pass

    def create_row(self, data):
        row = ctk.CTkFrame(self.scroll, fg_color="white", height=40)
        row.pack(fill="x", pady=1)
        
        # Info
        self._lbl(row, str(data.get('student_id')), 80)
        self._lbl(row, data.get('full_name'), 200)
        
        # Inputs
        e1 = self._ent(row, data.get('attendance'), 100)
        e2 = self._ent(row, data.get('midterm'), 100)
        e3 = self._ent(row, data.get('final'), 100)
        
        # Total
        tot = data.get('total')
        self._lbl(row, str(tot) if tot else "-", 80, color="#0F766E")
        
        self.entries[data['student_id']] = (e1, e2, e3)

    def _lbl(self, p, txt, w, color="#333"):
        f = ctk.CTkFrame(p, fg_color="transparent", width=w, height=40)
        f.pack(side="left", padx=2); f.pack_propagate(False)
        ctk.CTkLabel(f, text=txt, text_color=color, font=("Arial", 12)).place(relx=0, rely=0.5, anchor="w")

    def _ent(self, p, val, w):
        f = ctk.CTkFrame(p, fg_color="transparent", width=w, height=40)
        f.pack(side="left", padx=2); f.pack_propagate(False)
        e = ctk.CTkEntry(f, height=30, border_color="#E5E7EB", justify="center")
        if val: e.insert(0, str(val))
        e.pack(pady=5)
        return e

    def save(self):
        count = 0
        for sid, (e1, e2, e3) in self.entries.items():
            try:
                v1 = float(e1.get() or 0)
                v2 = float(e2.get() or 0)
                v3 = float(e3.get() or 0)
                self.controller.input_grade(sid, self.class_id, v1, v2, v3)
                count += 1
            except: pass
        messagebox.showinfo("Success", f"Saved {count} students.")