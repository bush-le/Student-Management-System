import customtkinter as ctk
import calendar
from datetime import datetime, timedelta
from controllers.lecturer_controller import LecturerController
from utils.threading_helper import run_in_background

class LecturerScheduleFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        # --- COLOR CONFIGURATION (TEAL THEME - LECTURER) ---
        self.COLOR_HEADER = "#0F766E"     # Dark Teal
        self.COLOR_WEEKEND = "#FFF9C4"    # Light Yellow (Sat, Sun)
        self.COLOR_BG = "white"
        
        # Course card color (Light Green - Mint)
        self.COLOR_CARD_BG = "#ECFDF5"    
        self.COLOR_CARD_BORDER = "#059669" 
        self.COLOR_TEXT_MAIN = "#064E3B"  

        # State: Current date being viewed
        self.current_date = datetime.now()
        self.view_mode = "Week" # Default view
        
        # Store references
        self.cells = {}         # Cells containing cards
        self.day_labels = []    # Header day labels for text updates

        self.create_header()

        # Container for the grid (Week or Month)
        self.grid_container = ctk.CTkFrame(self, fg_color="white", border_width=1, border_color="#E5E7EB")
        self.grid_container.pack(fill="both", expand=True)

        self.create_legend()
        self.load_schedule_async()
        self.update_view()

    # ==================================================
    # 1. HEADER & NAVIGATION LOGIC
    # ==================================================
    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", pady=(0, 15))
        
        # Month/Year display button (Top left)
        self.btn_date_display = ctk.CTkButton(
            header, text="", 
            fg_color="white", text_color="#333", border_color="#D1D5DB", border_width=1,
            width=140, height=35, font=("Arial", 12, "bold"),
            state="disabled"
        )
        self.btn_date_display.pack(side="left")
        
        # View Selector (Week / Month)
        self.view_selector = ctk.CTkSegmentedButton(header, values=["Week", "Month"], command=self.on_view_change, width=120)
        self.view_selector.set("Week")
        self.view_selector.pack(side="left", padx=15)

        # Navigation Controls (Top right)
        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right")
        
        self._btn_nav(nav, "<", command=self.prev_period)
        
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
        
        self._btn_nav(nav, ">", command=self.next_period)

    def _btn_nav(self, parent, txt, command):
        ctk.CTkButton(
            parent, text=txt, width=35, height=30, 
            fg_color=self.COLOR_HEADER, font=("Arial", 12, "bold"),
            command=command
        ).pack(side="left")

    def on_view_change(self, value):
        self.view_mode = value
        self.update_view()

    # --- LOGIC ĐIỀU HƯỚNG ---
    def prev_period(self):
        if self.view_mode == "Week":
            self.current_date -= timedelta(days=7)
        else:
            # Go to previous month
            first = self.current_date.replace(day=1)
            self.current_date = (first - timedelta(days=1)).replace(day=1)
        self.update_view()

    def next_period(self):
        if self.view_mode == "Week":
            self.current_date += timedelta(days=7)
        else:
            # Go to next month
            days_in_month = calendar.monthrange(self.current_date.year, self.current_date.month)[1]
            self.current_date = (self.current_date.replace(day=1) + timedelta(days=days_in_month))
        self.update_view()

    def go_today(self):
        self.current_date = datetime.now()
        self.update_view()

    def update_view(self):
        """Rebuilds the grid based on view mode and updates header"""
        # Clear existing grid
        for widget in self.grid_container.winfo_children():
            widget.destroy()
        self.cells = {}
        self.day_labels = []

        if self.view_mode == "Week":
            self.build_week_grid()
            
            # Update Header Text & Labels
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            self.btn_date_display.configure(text=start_of_week.strftime("%B %Y"))
            
            days_name = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
            for i, lbl in enumerate(self.day_labels):
                current_day = start_of_week + timedelta(days=i)
                day_str = current_day.strftime("%d/%m")
                lbl.configure(text=f"{days_name[i]}\n{day_str}")
                if current_day.date() == datetime.now().date():
                    lbl.configure(fg_color="#F59E0B")
        else:
            self.build_month_grid()
            self.btn_date_display.configure(text=self.current_date.strftime("%B %Y"))

        # Re-render data if available
        if hasattr(self, 'cells_data'):
            self._render_schedule(self.cells_data)

    # ==================================================
    # 2. GRID STRUCTURE (4 SLOTS COMPACT)
    # ==================================================
    def build_week_grid(self):
        # Column 0 (Session): Fixed width
        self.grid_container.grid_columnconfigure(0, weight=0, minsize=80)
        # Columns 1-7 (Days): Expand equally
        for i in range(1, 8):
            self.grid_container.grid_columnconfigure(i, weight=1)

        # Rows 0-4 (1 Header + 4 Slots)
        for r in range(5):
            self.grid_container.grid_rowconfigure(r, weight=1)

        # --- HEADER ROW ---
        self._create_header_cell(0, 0, "Session", width=None)

        self.day_labels = [] 
        for i in range(7):
            lbl = self._create_header_cell(0, i+1, "", bg_color=self.COLOR_HEADER)
            self.day_labels.append(lbl)

        # --- SESSION LABELS ---
        self._create_session_label(1, "Morning")   # Slot 1, 2
        self._create_session_label(3, "Afternoon") # Slot 3, 4

        # --- EMPTY SLOTS ---
        for r in range(1, 5): 
            for c in range(1, 8):
                bg = self.COLOR_WEEKEND if c >= 6 else "white"
                
                cell = ctk.CTkFrame(self.grid_container, fg_color=bg, corner_radius=0, border_width=1, border_color="#F3F4F6")
                cell.grid(row=r, column=c, sticky="nsew")
                
                ctk.CTkLabel(cell, text=f"Slot {r}", font=("Arial", 9), text_color="#E5E7EB").pack(anchor="nw", padx=5, pady=2)
                # Store references
                self.cells[(c-1, r)] = cell

    def build_month_grid(self):
        # 7 Columns (Mon-Sun)
        for i in range(7):
            self.grid_container.grid_columnconfigure(i, weight=1)
        
        # Header Row
        days_name = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for i, d in enumerate(days_name):
            self._create_header_cell(0, i, d, bg_color=self.COLOR_HEADER)

        # Calendar Days
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        for r, week in enumerate(cal):
            self.grid_container.grid_rowconfigure(r+1, weight=1)
            for c, day in enumerate(week):
                if day == 0:
                    bg = "#F9FAFB" # Empty
                    txt = ""
                else:
                    bg = "white"
                    txt = str(day)
                
                cell = ctk.CTkFrame(self.grid_container, fg_color=bg, border_width=1, border_color="#F3F4F6", corner_radius=0)
                cell.grid(row=r+1, column=c, sticky="nsew")
                if day != 0:
                    ctk.CTkLabel(cell, text=txt, font=("Arial", 10, "bold"), text_color="#374151").pack(anchor="ne", padx=5, pady=2)
                    self.cells[day] = cell # Store by day of month

    def create_legend(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=10)
        self._legend_item(frame, "Weekend Slot", self.COLOR_WEEKEND, "#D1D5DB")
        ctk.CTkFrame(frame, width=20, fg_color="transparent").pack(side="left")
        self._legend_item(frame, "Teaching Class", self.COLOR_CARD_BG, self.COLOR_CARD_BORDER)

    def _legend_item(self, parent, text, bg, border):
        box = ctk.CTkFrame(parent, width=15, height=15, fg_color=bg, border_width=1, border_color=border, corner_radius=2)
        box.pack(side="left")
        ctk.CTkLabel(parent, text=text, font=("Arial", 11), text_color="gray").pack(side="left", padx=(5, 0))

    # ==================================================
    # 3. DATA POPULATION
    # ==================================================
    def load_schedule_async(self, force=False):
        run_in_background(
            lambda: self.controller.get_teaching_schedule(force_update=force, active_only=True),
            self._render_schedule,
            tk_root=self.winfo_toplevel()
        )

    def _render_schedule(self, data):
        if not self.winfo_exists(): return
        if not data: return

        days_map = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        self.cells_data = data # Store data if needed for refresh

        if self.view_mode == "Month":
            self._render_month_data(data, days_map)
            return

        for item in data:
            raw_sched = item.get('schedule', '').lower()
            
            day_idx = -1
            for i, d in enumerate(days_map):
                if d in raw_sched:
                    day_idx = i
                    break
            
            if day_idx == -1: continue

            # 2. Find Slot (Compact 4 Slot Logic)
            try:
                # Parse: "Monday 07:00-..."
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

    def _render_month_data(self, data, days_map):
        # Get matrix of current month
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Map weekday index to list of days in this month
        # e.g. 0 (Mon) -> [1, 8, 15, 22, 29]
        weekday_dates = {i: [] for i in range(7)}
        for week in cal:
            for day_idx, day_num in enumerate(week):
                if day_num != 0:
                    weekday_dates[day_idx].append(day_num)

        for item in data:
            raw_sched = item.get('schedule', '').lower()
            for i, d in enumerate(days_map):
                if d in raw_sched:
                    # This class happens on weekday 'i'
                    # Render it for all dates in this month that match 'i'
                    for date_num in weekday_dates[i]:
                        if date_num in self.cells:
                            self._render_mini_dot(self.cells[date_num], item)

    def _render_card(self, parent, data):
        # Clear old widgets
        for w in parent.winfo_children():
            if isinstance(w, ctk.CTkLabel) and "Slot" in w.cget("text"): continue
            w.destroy()

        card = ctk.CTkFrame(parent, fg_color=self.COLOR_CARD_BG, corner_radius=4, border_width=1, border_color=self.COLOR_CARD_BORDER)
        card.pack(fill="both", expand=True, padx=4, pady=(15, 4)) 
        # Dark green bar on the left
        # Decorative color bar
        ctk.CTkFrame(card, width=4, fg_color=self.COLOR_CARD_BORDER, corner_radius=0).pack(side="left", fill="y", padx=(0, 5))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(content, text=data.get('course_name', 'Unknown'), font=("Arial", 10, "bold"), text_color=self.COLOR_TEXT_MAIN, wraplength=120, justify="left").pack(anchor="w")
        
        ctk.CTkLabel(content, text=f"ID: {data.get('class_id', '')}", font=("Arial", 9, "bold"), text_color="#047857").pack(anchor="w")
        ctk.CTkLabel(content, text=f"{data.get('semester_name', '')}", font=("Arial", 9, "italic"), text_color="#6B7280").pack(anchor="w")
        
        raw_sched = data.get('schedule', '')
        time_only = raw_sched.split(' ', 1)[1] if ' ' in raw_sched else ""
        ctk.CTkLabel(content, text=f"Time: {time_only}", font=("Arial", 9), text_color="#555").pack(anchor="w", pady=(2,0))
        
        ctk.CTkLabel(content, text=f"Room: {data.get('room', 'TBA')}", font=("Arial", 9), text_color="#555").pack(anchor="w")
        
        # Enrollment (Unlike students, lecturers need to see enrollment count)
        enrolled = data.get('enrolled_count', 0)
        ctk.CTkLabel(content, text=f"Students: {enrolled}", font=("Arial", 9, "bold"), text_color="#059669").pack(anchor="w", pady=(2,0))

    def _render_mini_dot(self, parent, data):
        # Simple list item for month view
        f = ctk.CTkFrame(parent, fg_color=self.COLOR_CARD_BG, height=20, corner_radius=3)
        f.pack(fill="x", padx=2, pady=1)
        ctk.CTkLabel(f, text=data.get('course_name', 'Class'), font=("Arial", 9), text_color=self.COLOR_TEXT_MAIN).pack(side="left", padx=2)

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
        return lbl

    def _create_session_label(self, start_row, txt):
        lbl = ctk.CTkLabel(self.grid_container, text=txt, fg_color=self.COLOR_HEADER, text_color="white", font=("Arial", 11, "bold"))
        lbl.grid(row=start_row, column=0, rowspan=2, sticky="nswe", padx=1, pady=1)