import customtkinter as ctk
from datetime import datetime, timedelta
from controllers.lecturer_controller import LecturerController

class LecturerScheduleFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="transparent")
        self.controller = LecturerController(user_id)
        self.cells = {}
        
        self.create_header()
        self.create_grid()
        self.populate_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        # Calculate Week
        today = datetime.now()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        week_txt = f"{start.strftime('%d %b')} - {end.strftime('%d %b %Y')}"
        
        ctk.CTkLabel(header, text="Weekly Schedule", font=("Arial", 20, "bold"), text_color="#111827").pack(side="left")
        ctk.CTkLabel(header, text=week_txt, font=("Arial", 12, "bold"), text_color="#333").pack(side="right")

    def create_grid(self):
        self.grid_frame = ctk.CTkFrame(self, fg_color="#E5E7EB", border_width=1, corner_radius=0)
        self.grid_frame.pack(fill="both", expand=True)

        # 8 Cols (Time + 7 Days)
        for i in range(8): self.grid_frame.grid_columnconfigure(i, weight=0 if i==0 else 1)
        # 13 Rows (Header + 12 Slots)
        for i in range(13): self.grid_frame.grid_rowconfigure(i, weight=1)

        # Header
        days = ["TIME", "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for c, d in enumerate(days):
            bg = "#0F766E" if c > 0 else "#374151"
            lbl = ctk.CTkLabel(self.grid_frame, text=d, fg_color=bg, text_color="white", font=("Arial", 11, "bold"), height=40)
            lbl.grid(row=0, column=c, sticky="nsew", padx=1, pady=1)

        # Time Slots
        times = ["07:00", "07:50", "09:00", "09:50", "10:40", "13:00", "13:50", "14:40", "15:40", "16:30", "17:20", "18:10"]
        for r, t in enumerate(times, 1):
            f = ctk.CTkFrame(self.grid_frame, fg_color="#F3F4F6", corner_radius=0)
            f.grid(row=r, column=0, sticky="nsew", padx=1, pady=1)
            ctk.CTkLabel(f, text=f"Slot {r}", font=("Arial", 10, "bold"), text_color="#333").pack(pady=(5,0))
            ctk.CTkLabel(f, text=t, font=("Arial", 9), text_color="gray").pack()

        # Empty Cells
        for r in range(1, 13):
            for c in range(1, 8):
                cell = ctk.CTkFrame(self.grid_frame, fg_color="white", corner_radius=0)
                cell.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)

    def populate_data(self):
        try:
            data = self.controller.get_teaching_schedule()
            if not data: return
            
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for cls in data:
                raw = cls.get('schedule', '').lower()
                
                day_idx = -1
                for i, d in enumerate(days):
                    if d in raw: day_idx = i; break
                
                if day_idx == -1: continue
                
                try:
                    # Parse "Monday 07:00-09:30"
                    time_part = raw.split(days[day_idx])[1].strip()
                    start_h = int(time_part.split('-')[0].split(':')[0])
                    start_slot = self._hour_to_slot(start_h)
                    
                    if start_slot > 0:
                        self._render_card(day_idx, start_slot, 3, cls) # Duration 3 slots
                except: continue
        except: pass

    def _render_card(self, day_idx, start_slot, duration, data):
        card = ctk.CTkFrame(self.grid_frame, fg_color="#ECFDF5", corner_radius=4)
        card.grid(row=start_slot, column=day_idx+1, rowspan=duration, sticky="nsew", padx=2, pady=2)
        
        # Accent Border
        ctk.CTkFrame(card, width=4, fg_color="#10B981").pack(side="left", fill="y")
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(content, text=data.get('course_name'), font=("Arial", 10, "bold"), text_color="#064E3B", wraplength=100, justify="left").pack(anchor="w")
        ctk.CTkLabel(content, text=f"Room: {data.get('room')}", font=("Arial", 9), text_color="#4B5563").pack(anchor="w")

    def _hour_to_slot(self, h):
        # Simple mapping
        if 6<=h<8: return 1
        if 8<=h<9: return 2
        if 9<=h<10: return 3
        if 10<=h<11: return 4
        if 11<=h<12: return 5
        if 12<=h<14: return 6
        if 14<=h<15: return 7
        if 15<=h<16: return 8
        if 16<=h<17: return 9
        if 17<=h<19: return 10
        return 1