import customtkinter as ctk
from controllers.lecturer_controller import LecturerController
from utils.threading_helper import run_in_background

class LecturerClassesFrame(ctk.CTkFrame):
    def __init__(self, parent, dashboard, controller):
        # Change background to transparent to blend with dashboard
        super().__init__(parent, fg_color="transparent")
        self.dashboard = dashboard 
        self.controller = controller
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="My Assigned Classes", font=("Arial", 20, "bold"), text_color="#111827").pack(side="left")
        
        # Refresh Button
        ctk.CTkButton(
            header_frame, text="↻ Refresh", width=100, height=30,
            fg_color="white", text_color="#0F766E", border_width=1, border_color="#CCFBF1",
            font=("Arial", 12, "bold"), command=lambda: self.load_classes(force=True)
        ).pack(side="right")
        
        # --- FIX HERE: Use regular CTkFrame, not ScrollableFrame ---
        self.list_container = ctk.CTkFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True)
        
        # Grid Layout for Cards
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_columnconfigure(1, weight=1)
        self.load_classes()

    def load_classes(self, force=False):
        # 1. Clear old widgets
        for w in self.list_container.winfo_children(): w.destroy()
        
        # 2. Show Loading
        self.loading_lbl = ctk.CTkLabel(self.list_container, text="⏳ Loading classes...", text_color="gray")
        self.loading_lbl.pack(pady=20)
        
        # 3. Run in background
        run_in_background(
            lambda: self._fetch_classes(force),
            self._render_classes,
            tk_root=self.winfo_toplevel()
        )

    def _fetch_classes(self, force):
        try:
            schedule = self.controller.get_teaching_schedule(force_update=force)
            # OPTIMIZATION: Deduplicate classes. 
            # The schedule may contain multiple slots for the same class (e.g. Mon & Wed).
            unique_classes = {}
            for s in schedule:
                cid = s.get('class_id')
                if cid and cid not in unique_classes:
                    unique_classes[cid] = s
            return list(unique_classes.values())
        except:
            return []

    def _render_classes(self, classes):
        if not self.winfo_exists(): return
        if hasattr(self, 'loading_lbl'): self.loading_lbl.destroy()

        if not classes:
            ctk.CTkLabel(self.list_container, text="No classes found.", text_color="gray").pack(pady=20)
            return
            
        for i, cls in enumerate(classes): # Create a card for each class
            self.create_card(cls, i // 2, i % 2)

    def create_card(self, data, r, c):
        # Pack into self.list_container instead of self.scroll
        card = ctk.CTkFrame(self.list_container, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        card.grid(row=r, column=c, sticky="nsew", padx=10, pady=10)
        
        # Header Card
        h = ctk.CTkFrame(card, fg_color="transparent")
        h.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(h, text=data.get('course_name'), font=("Arial", 16, "bold"), text_color="#0F766E").pack(anchor="w")
        ctk.CTkLabel(h, text=f"ID: {data.get('class_id')}", font=("Arial", 12, "bold"), text_color="gray").pack(anchor="w")
        
        # Info
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=20, pady=5)
        # Display schedule, room, and student count
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