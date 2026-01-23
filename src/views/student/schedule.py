import customtkinter as ctk
from datetime import datetime, timedelta
from controllers.student_controller import StudentController
from utils.threading_helper import run_in_background

class ScheduleFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        # --- COLOR CONFIGURATION ---
        self.COLOR_HEADER = "#45818E"     # Teal
        self.COLOR_WEEKEND = "#FFF9C4"    # Light Yellow
        self.COLOR_BG = "white"
        self.COLOR_CARD_BG = "#E3F2FD"    # Light Blue (Card)
        self.COLOR_CARD_BORDER = "#2196F3" 
        self.COLOR_TEXT_MAIN = "#0D47A1"  

        # State: Current date being viewed (Defaults to today)
        
        self.current_date = datetime.now()
        
        self.cells = {}         # Cells containing course cards
        self.day_labels = []    # Header labels (Day/Date) for text updates
        self.lbl_week_range = None # Label displaying the week's date range

        # 1. Header (Navigation)
        self.create_header()

        # 2. Grid Structure (4 Slots)
        self.create_grid_structure()

        # 3. Legend
        self.create_legend()

        # 4. Populate data for the first time
        self.load_schedule_async()

        # 5. Update dates in the Header for the current week
        self.update_week_view()

    # ==================================================
    # 1. HEADER & NAVIGATION LOGIC
    # ==================================================
    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", pady=(0, 15))
        # Date Picker (Date display button, not deeply interactive in this version)
        self.btn_date_display = ctk.CTkButton(
            header, text="",
            fg_color="white", text_color="#333", border_color="#D1D5DB", border_width=1,
            width=140, height=35, font=("Arial", 12, "bold"),
            state="disabled" # For display only
        )
        self.btn_date_display.pack(side="left")

        # Navigation Controls
        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right")
        
        # Previous Week Button
        self._btn_nav(nav, "<", command=self.prev_week)
        
        # Today Button
        # Refresh Button
        ctk.CTkButton(
            nav, text="↻", width=35, height=30,
            fg_color="white", text_color=self.COLOR_HEADER, border_width=1, border_color=self.COLOR_HEADER,
            font=("Arial", 14, "bold"), command=lambda: self.load_schedule_async(force=True)
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            nav, text="TODAY", fg_color=self.COLOR_HEADER,
            width=80, font=("Arial", 11, "bold"),
            command=self.go_today
        ).pack(side="left", padx=5)
        
        self._btn_nav(nav, ">", command=self.next_week)
        
    def _btn_nav(self, parent, txt, command):
        ctk.CTkButton(
            parent, text=txt, width=35, height=30, 
            fg_color=self.COLOR_HEADER, font=("Arial", 12, "bold"),
            command=command
        ).pack(side="left")

    # --- NAVIGATION LOGIC ---
    def prev_week(self):
        self.current_date -= timedelta(days=7)
        self.update_week_view()

    def next_week(self):
        self.current_date += timedelta(days=7)
        self.update_week_view()

    def go_today(self):
        self.current_date = datetime.now()
        self.update_week_view()

    def update_week_view(self):
        """Calculates the start/end of the week and updates the UI"""
        # Find the Monday of the selected week
        # weekday(): 0=Mon, 6=Sun
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # 1. Update the date display button in the top left (e.g., Jan 2026)
        self.btn_date_display.configure(text=start_of_week.strftime("%B %Y"))

        # 2. Update Header columns (Mon 05/01, Tue 06/01...)
        days_name = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        
        for i, lbl in enumerate(self.day_labels):
            # Calculate the date for the i-th column
            current_day = start_of_week + timedelta(days=i)
            day_str = current_day.strftime("%d/%m") # e.g., 05/01

            # Update text: Day name, new line, Date
            lbl.configure(text=f"{days_name[i]}\n{day_str}")
            
            is_today_real = current_day.date() == datetime.now().date()
            if is_today_real:
                lbl.configure(fg_color="#F59E0B")
            else:
                # Revert to default color (Sat, Sun light yellow, weekdays blue)
                bg = "#F59E0B" if i >= 5 else self.COLOR_HEADER
                lbl.configure(fg_color=bg)

    # ==================================================
    # 2. GRID STRUCTURE
    # ==================================================
    def create_grid_structure(self):
        self.grid_container = ctk.CTkFrame(self, fg_color="white", border_width=1, border_color="#E5E7EB")
        self.grid_container.pack(fill="both", expand=True)

        # Column 0 (Session): Fixed width 80px
        self.grid_container.grid_columnconfigure(0, weight=0, minsize=80)
        # Columns 1-7 (Days): Expand equally
        for i in range(1, 8):
            self.grid_container.grid_columnconfigure(i, weight=1)

        # Rows 0-4
        for r in range(5):
            self.grid_container.grid_rowconfigure(r, weight=1)

        # --- HEADER ROW ---
        self._create_header_cell(0, 0, "Session", width=None)

        # Create empty header labels, save to list for later update
        self.day_labels = [] 
        for i in range(7):
            # i+1 because column 0 is for session
            lbl = self._create_header_cell(0, i+1, "", bg_color=self.COLOR_HEADER)
            self.day_labels.append(lbl)

        # --- SESSION LABELS --- (Morning, Afternoon)
        self._create_session_label(1, "Morning")   # Slot 1, 2
        self._create_session_label(3, "Afternoon") # Slot 3, 4

        # --- EMPTY SLOTS ---
        for r in range(1, 5): 
            for c in range(1, 8):
                bg = self.COLOR_WEEKEND if c >= 6 else "white"
                
                cell = ctk.CTkFrame(self.grid_container, fg_color=bg, corner_radius=0, border_width=1, border_color="#F3F4F6")
                cell.grid(row=r, column=c, sticky="nsew")
                
                ctk.CTkLabel(cell, text=f"Slot {r}", font=("Arial", 9), text_color="#E5E7EB").pack(anchor="nw", padx=5, pady=2)
                # Store reference: Key = (day_index_0_6, slot_1_4)
                self.cells[(c-1, r)] = cell

    def create_legend(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=10)
        self._legend_item(frame, "Weekend Slot", self.COLOR_WEEKEND, "#D1D5DB")
        ctk.CTkFrame(frame, width=20, fg_color="transparent").pack(side="left")
        self._legend_item(frame, "Registered Class", self.COLOR_CARD_BG, self.COLOR_CARD_BORDER)

    def _legend_item(self, parent, text, bg, border):
        box = ctk.CTkFrame(parent, width=15, height=15, fg_color=bg, border_width=1, border_color=border, corner_radius=2)
        box.pack(side="left")
        ctk.CTkLabel(parent, text=text, font=("Arial", 11), text_color="gray").pack(side="left", padx=(5, 0))

    # ==================================================
    # 3. DATA POPULATION
    # ==================================================
    def load_schedule_async(self, force=False):
        run_in_background(
            lambda: self.controller.view_schedule(force_update=force),
            self._render_schedule,
            tk_root=self.winfo_toplevel()
        )

    def _render_schedule(self, data):
        if not self.winfo_exists(): return
        if not data: return

        days_map = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

        for item in data: # Iterate through schedule items
            raw_sched = item.get('schedule', '').lower() # Get raw schedule string
            if not raw_sched: continue
            
            # 1. Tìm ngày
            day_idx = -1
            for i, d in enumerate(days_map):
                if d in raw_sched:
                    day_idx = i
                    break
            
            if day_idx == -1: continue

            # 2. Find Slot
            try:
                # Parse: "Monday 07:00-..."
                # Optimization: Split once
                parts = raw_sched.split(days_map[day_idx])
                if len(parts) < 2: continue
                
                time_part = parts[1].strip()
                if not time_part: continue
                start_hour = int(time_part.split('-')[0].split(':')[0])
                
                slot_idx = -1
                if 6 <= start_hour < 9: slot_idx = 1
                elif 9 <= start_hour < 12: slot_idx = 2
                elif 12 <= start_hour < 15: slot_idx = 3
                elif 15 <= start_hour < 18: slot_idx = 4
                
                # 3. Render Card
                if slot_idx > 0 and (day_idx, slot_idx) in self.cells:
                    target_cell = self.cells[(day_idx, slot_idx)]
                    self._render_card(target_cell, item)
            except Exception:
                continue

    def _render_card(self, parent, data):
        # Clear old widgets
        for w in parent.winfo_children():
            if isinstance(w, ctk.CTkLabel) and "Slot" in w.cget("text"): continue
            w.destroy()

        card = ctk.CTkFrame(parent, fg_color=self.COLOR_CARD_BG, corner_radius=4, border_width=1, border_color=self.COLOR_CARD_BORDER)
        card.pack(fill="both", expand=True, padx=4, pady=(15, 4)) 

        ctk.CTkFrame(card, width=4, fg_color=self.COLOR_CARD_BORDER, corner_radius=0).pack(side="left", fill="y", padx=(0, 5))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(content, text=data.get('course_name', 'Unknown'), font=("Arial", 10, "bold"), text_color=self.COLOR_TEXT_MAIN, wraplength=120, justify="left").pack(anchor="w")
        ctk.CTkLabel(content, text=data.get('course_code', ''), font=("Arial", 9, "bold"), text_color="#1E3A8A").pack(anchor="w")
        
        raw_sched = data.get('schedule', '')
        time_only = raw_sched.split(' ', 1)[1] if ' ' in raw_sched else ""
        ctk.CTkLabel(content, text=f"Time: {time_only}", font=("Arial", 9), text_color="#555").pack(anchor="w", pady=(2,0))
        
        ctk.CTkLabel(content, text=f"Room: {data.get('room', 'TBA')}", font=("Arial", 9), text_color="#555").pack(anchor="w")
        
        if data.get('lecturer_name'):
            ctk.CTkLabel(content, text=f"Lecturer: {data['lecturer_name']}", font=("Arial", 9, "italic"), text_color="#64748B", wraplength=120, justify="left").pack(anchor="w")

    # ==================================================
    # 4. HELPERS
    # ==================================================
    def _create_header_cell(self, r, c, txt, bg_color=None, width=None):
        if bg_color is None: bg_color = self.COLOR_HEADER
        
        if width:
            f = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0, height=45, width=width)
            f.grid_propagate(False)
        else:
            f = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0, height=45)
            
        f.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
        
        lbl = ctk.CTkLabel(f, text=txt, text_color="white", font=("Arial", 10, "bold"))
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        return lbl # <--- Important: return label object

    def _create_session_label(self, start_row, txt):
        lbl = ctk.CTkLabel(self.grid_container, text=txt, fg_color=self.COLOR_HEADER, text_color="white", font=("Arial", 11, "bold"))
        lbl.grid(row=start_row, column=0, rowspan=2, sticky="nswe", padx=1, pady=1)