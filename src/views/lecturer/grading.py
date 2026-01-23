import customtkinter as ctk
from tkinter import messagebox
from controllers.lecturer_controller import LecturerController
from utils.threading_helper import run_in_background

class GradingView(ctk.CTkFrame):
    def __init__(self, parent, controller, class_data):
        super().__init__(parent, fg_color="white", corner_radius=10)
        self.controller = controller
        self.class_id = class_data['class_id']
        self.entries = {}
        
        # Tools (Header)
        t = ctk.CTkFrame(self, fg_color="transparent", height=50)
        t.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(t, text="Enter Grades (Scale 0-10)", font=("Arial", 12), text_color="gray").pack(side="left")
        
        ctk.CTkButton(
            t, text="Save Grades", fg_color="#0F766E", hover_color="#115E59", 
            width=120, command=self.save
        ).pack(side="right")

        # Table Header
        cols = [("ID", 80), ("Name", 200), ("Att (10%)", 100), ("Mid (40%)", 100), ("Final (50%)", 100), ("Total", 80)]
        h = ctk.CTkFrame(self, fg_color="#F9FAFB", height=40)
        h.pack(fill="x", padx=20)
        
        for i, (txt, w) in enumerate(cols):
            f = ctk.CTkFrame(h, fg_color="transparent", width=w, height=40)
            f.pack(side="left", padx=2)
            f.pack_propagate(False)
            anchor = "center" if i >= 2 else "w"
            ctk.CTkLabel(f, text=txt, font=("Arial", 11, "bold"), text_color="#374151").place(relx=0 if anchor=="w" else 0.5, rely=0.5, anchor=anchor)

        # --- FIX HERE: Use regular Frame ---
        self.list_container = ctk.CTkFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        self.load_students_async()

    def load_students_async(self):
        # Clear old widgets
        for w in self.list_container.winfo_children(): w.destroy()
        ctk.CTkLabel(self.list_container, text="Loading students...", text_color="gray").pack(pady=20)

        run_in_background(
            lambda: self.controller.get_class_student_list(self.class_id),
            self._render_students,
            tk_root=self.winfo_toplevel()
        )

    def _render_students(self, students):
        if not self.winfo_exists(): return
        for w in self.list_container.winfo_children(): w.destroy()
        if not students:
            ctk.CTkLabel(self.list_container, text="No students found.", text_color="gray").pack(pady=20)
            return 
        for s in students: self.create_row(s)

    def create_row(self, data):
        # Pack into list_container
        row = ctk.CTkFrame(self.list_container, fg_color="white", height=40)
        row.pack(fill="x", pady=1)
        
        # Info
        code = str(data.get('student_code') or data.get('student_id'))
        self._lbl(row, code, 80)
        self._lbl(row, data.get('full_name', 'Unknown'), 200)
        
        # Inputs
        e1 = self._ent(row, data.get('attendance_score'), 100) 
        e2 = self._ent(row, data.get('midterm'), 100)
        e3 = self._ent(row, data.get('final'), 100)
        
        # Total
        tot = data.get('total')
        self._lbl(row, str(tot) if tot is not None else "-", 80, color="#0F766E", is_bold=True)
        
        self.entries[data['student_id']] = (e1, e2, e3)

    def _lbl(self, p, txt, w, color="#333", is_bold=False):
        f = ctk.CTkFrame(p, fg_color="transparent", width=w, height=40)
        f.pack(side="left", padx=2); f.pack_propagate(False)
        font = ("Arial", 12, "bold") if is_bold else ("Arial", 12)
        anchor = "center" if w <= 100 else "w"
        relx = 0.5 if anchor == "center" else 0
        ctk.CTkLabel(f, text=txt, text_color=color, font=font).place(relx=relx, rely=0.5, anchor=anchor)

    def _ent(self, p, val, w):
        f = ctk.CTkFrame(p, fg_color="transparent", width=w, height=40)
        f.pack(side="left", padx=2); f.pack_propagate(False)
        e = ctk.CTkEntry(f, height=30, width=80, border_color="#E5E7EB", justify="center")
        if val is not None: e.insert(0, str(val))
        e.place(relx=0.5, rely=0.5, anchor="center")
        return e

    def save(self):
        # Collect data from UI first (must be on main thread)
        data_to_save = []
        for sid, (e1, e2, e3) in self.entries.items():
            try:
                v1 = float(e1.get() or 0)
                v2 = float(e2.get() or 0)
                v3 = float(e3.get() or 0)
                data_to_save.append((sid, v1, v2, v3))
            except ValueError: pass
        
        def _save_task():
            # OPTIMIZATION: Use bulk update instead of looping input_grade
            return self.controller.update_class_grades(self.class_id, data_to_save)

        def _on_complete(result):
            success, msg = result
            if success: 
                messagebox.showinfo("Success", msg)
                self.load_students_async() # Reload to confirm data integrity
            else: messagebox.showerror("Error", msg)

        run_in_background(_save_task, _on_complete, tk_root=self.winfo_toplevel())