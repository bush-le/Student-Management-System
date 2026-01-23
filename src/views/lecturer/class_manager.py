import customtkinter as ctk
from views.lecturer.grading import GradingView

class LecturerClassManager(ctk.CTkFrame):
    def __init__(self, parent, user_id, class_data, on_back_callback):
        super().__init__(parent, fg_color="#F3F4F6")
        self.class_data = class_data
        self.user_id = user_id
        self.on_back = on_back_callback
        
        # Header
        h = ctk.CTkFrame(self, fg_color="transparent", height=50)
        h.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(h, text="Back", fg_color="white", text_color="#333", width=80, command=on_back_callback).pack(side="left")
        ctk.CTkLabel(h, text=f"Managing: {class_data.get('course_name')}", font=("Arial", 18, "bold"), text_color="#111827").pack(side="left", padx=20)

        # Tabs
        tabs = ctk.CTkFrame(self, fg_color="transparent")
        tabs.pack(fill="x", pady=(0, 10))
        self.btn_grad = self._tab_btn(tabs, "Grading Sheet", self.show_grading)
        self.btn_rost = self._tab_btn(tabs, "Class Roster", self.show_roster)

        # Content
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True)
        
        self.show_grading() # Default

    def _tab_btn(self, p, txt, cmd):
        btn = ctk.CTkButton(p, text=txt, fg_color="white", text_color="#333", hover_color="#E5E7EB", width=150, command=cmd)
        btn.pack(side="left", padx=(0, 10))
        return btn

    def show_grading(self):
        for w in self.content.winfo_children(): w.destroy()
        self.btn_grad.configure(fg_color="#0F766E", text_color="white")
        self.btn_rost.configure(fg_color="white", text_color="#333")
        # Load Grading View
        GradingView(self.content, self.user_id, self.class_data).pack(fill="both", expand=True)

    def show_roster(self):
        for w in self.content.winfo_children(): w.destroy()
        self.btn_rost.configure(fg_color="#0F766E", text_color="white")
        self.btn_grad.configure(fg_color="white", text_color="#333")
        ctk.CTkLabel(self.content, text="Roster View Coming Soon").pack(pady=50)