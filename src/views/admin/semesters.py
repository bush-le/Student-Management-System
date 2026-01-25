import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController
from utils.threading_helper import run_in_background

class SemestersFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Fixed column widths for alignment [Name, Start, End, Status, Actions]
        self.col_widths = [250, 150, 150, 120, 150]
        
        # 1. Toolbar
        self.create_toolbar()

        # 2. Table Header
        self.create_table_header()

        # 3. List Container
        self.scroll_area = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.scroll_area.pack(fill="both", expand=True, pady=(0, 20))

        # 4. Load Data
        self.load_data_async()

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent", height=50)
        toolbar.pack(fill="x", pady=(0, 15))
        # Search Entry
        self.search_ent = ctk.CTkEntry(
            toolbar, placeholder_text="Search semester...", 
            width=300, height=40, border_color="#E5E7EB", border_width=1
        )
        self.search_ent.pack(side="left")
        self.search_ent.bind("<Return>", lambda e: self.perform_search())
        
        btn_search = ctk.CTkButton(toolbar, text="Search", width=60, height=40, fg_color="#0F766E", command=self.perform_search)
        btn_search.pack(side="left", padx=5)
        
        # Add Button
        btn_add = ctk.CTkButton(
            toolbar, text="+ New Semester", fg_color="#0F766E", hover_color="#115E59", height=40,
            font=("Arial", 13, "bold"),
            command=self.open_add_dialog
        )
        btn_add.pack(side="right")

    def create_table_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#E5E7EB", height=40, corner_radius=5)
        h_frame.pack(fill="x", pady=(0, 5))
        h_frame.grid_propagate(False)
        
        cols = ["SEMESTER NAME", "START DATE", "END DATE", "STATUS", "ACTIONS"]
        
        for i, text in enumerate(cols):
            ctk.CTkLabel(
                h_frame, text=text, font=("Arial", 11, "bold"), text_color="#374151", anchor="w",
                width=self.col_widths[i]
            ).grid(row=0, column=i, sticky="ew", padx=10, pady=8)

    def perform_search(self):
        self.load_data_async()

    def load_data_async(self):
        for widget in self.scroll_area.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.scroll_area, text="Loading...", text_color="gray").pack(pady=20)
        
        search_query = self.search_ent.get().strip()
        run_in_background(
            lambda: self.controller.get_all_semesters(search_query=search_query),
            self._render_data,
            tk_root=self.winfo_toplevel()
        )

    def _render_data(self, semesters):
        if not self.winfo_exists(): return
        for widget in self.scroll_area.winfo_children(): widget.destroy()
        try:
            for idx, sem in enumerate(semesters):
                self.create_row(sem, idx)
        except Exception as e:
            ctk.CTkLabel(self.scroll_area, text=f"Error: {e}", text_color="red").pack(pady=20)

    def create_row(self, data, idx):
        # Zebra striping
        bg_color = "white" if idx % 2 == 0 else "#F9FAFB"
        
        row = ctk.CTkFrame(self.scroll_area, fg_color=bg_color, corner_radius=0, height=30)
        row.pack(fill="x", pady=0)
        row.grid_propagate(False)
        row.grid_rowconfigure(0, weight=1)
        
        # Data Cells
        ctk.CTkLabel(row, text=data.name, font=("Arial", 12, "bold"), text_color="#333", anchor="w", width=self.col_widths[0]).grid(row=0, column=0, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=str(data.start_date), font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[1]).grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(row, text=str(data.end_date), font=("Arial", 12), text_color="#555", anchor="w", width=self.col_widths[2]).grid(row=0, column=2, sticky="ew", padx=10)
        
        # Status
        status = data.status.upper()
        status_col = "#059669" if status == "OPEN" else "#9CA3AF"
        ctk.CTkLabel(row, text=status, font=("Arial", 11, "bold"), text_color=status_col, anchor="w", width=self.col_widths[3]).grid(row=0, column=3, sticky="ew", padx=10)

        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent", width=self.col_widths[4])
        actions.grid(row=0, column=4, sticky="ew", padx=5)
        actions.pack_propagate(False)
        
        self._action_btn(actions, "Edit", "#3B82F6", lambda: self.open_edit_dialog(data))
        self._action_btn(actions, "Del", "#EF4444", lambda: self.delete_item(data.semester_id))

    def _action_btn(self, parent, text, color, cmd):
        ctk.CTkButton(
            parent, text=text, width=40, height=26, 
            fg_color="transparent", text_color=color, hover_color="#F3F4F6",
            font=("Arial", 11, "bold"), command=cmd
        ).pack(side="left", padx=2)

    def delete_item(self, sem_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this semester?"):
            run_in_background(
                lambda: self.controller.delete_semester(sem_id),
                lambda res: [self.load_data_async(), messagebox.showinfo("Success", res[1])] if res[0] else messagebox.showerror("Error", res[1]),
                tk_root=self.winfo_toplevel()
            )

    def open_add_dialog(self):
        SemesterDialog(self, "Add Semester", controller=self.controller, callback=self.load_data_async)

    def open_edit_dialog(self, data):
        SemesterDialog(self, "Edit Semester", controller=self.controller, callback=self.load_data_async, data=data)


# ==========================================
# POPUP DIALOG (STYLE UPDATE)
# ==========================================
class SemesterDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.title(title)
        self.geometry("450x500")
        self.resizable(False, False)
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 20, "bold"), text_color="#111827").pack(pady=25, anchor="w", padx=40)

        # Name
        self.entry_name = self.create_input("Semester Name", "e.g. Summer 2025")
        
        # Dates
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.pack(fill="x", padx=40, pady=0)
        
        f1 = ctk.CTkFrame(date_frame, fg_color="transparent")
        f1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(f1, text="Start Date", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w")
        self.entry_start = ctk.CTkEntry(f1, placeholder_text="YYYY-MM-DD", height=40, border_color="#E5E7EB")
        self.entry_start.pack(fill="x", pady=5)

        f2 = ctk.CTkFrame(date_frame, fg_color="transparent")
        f2.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(f2, text="End Date", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w")
        self.entry_end = ctk.CTkEntry(f2, placeholder_text="YYYY-MM-DD", height=40, border_color="#E5E7EB")
        self.entry_end.pack(fill="x", pady=5)

        # Status
        ctk.CTkLabel(self, text="Status", font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", padx=40, pady=(15, 5))
        self.combo_status = ctk.CTkComboBox(
            self, values=["OPEN", "CLOSED"], height=40, 
            state="readonly", border_color="#E5E7EB", fg_color="white", text_color="black"
        )
        self.combo_status.pack(fill="x", padx=40)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=40, pady=40)
        
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="white", border_color="#D1D5DB", border_width=1, 
                      text_color="black", hover_color="#F3F4F6", width=100, height=40, command=self.destroy).pack(side="left")
        
        ctk.CTkButton(btn_frame, text="Save", fg_color="#0F766E", hover_color="#115E59", 
                      width=100, height=40, font=("Arial", 13, "bold"), command=self.save).pack(side="right")

        # Fill Data if Edit
        if data:
            self.entry_name.insert(0, data.name)
            self.entry_start.insert(0, str(data.start_date))
            self.entry_end.insert(0, str(data.end_date))
            self.combo_status.set(data.status)

        self.lift()
        self.after(100, lambda: [self.focus_force(), self.grab_set()])

    def create_input(self, label, placeholder):
        ctk.CTkLabel(self, text=label, font=("Arial", 12, "bold"), text_color="#374151").pack(anchor="w", padx=40, pady=(10, 5))
        entry = ctk.CTkEntry(self, placeholder_text=placeholder, height=40, border_color="#E5E7EB")
        entry.pack(fill="x", padx=40)
        return entry

    def save(self):
        name = self.entry_name.get()
        start = self.entry_start.get()
        end = self.entry_end.get()
        status = self.combo_status.get()

        if not name or not start or not end:
            messagebox.showwarning("Warning", "Please fill all fields", parent=self)
            return

        def _save_task():
            if self.data: # Update
                return self.controller.update_semester(self.data.semester_id, name, start, end, status)
            else: # Create
                return self.controller.create_semester(name, start, end)
        
        def _on_complete(result):
            success, msg = result
            if success:
                self.callback()
                self.destroy()
            else:
                messagebox.showerror("Error", msg, parent=self)

        run_in_background(_save_task, _on_complete, tk_root=self.winfo_toplevel())