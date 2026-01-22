import customtkinter as ctk
from tkinter import messagebox
from controllers.admin_controller import AdminController

class AnnouncementsFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id):
        super().__init__(parent, fg_color="white")
        self.controller = AdminController(user_id)
        self.user_id = user_id 
        
        self.COLOR_PRIMARY = "#10B981"
        self.COLOR_EDIT = "#9CA3AF"
        self.COLOR_DELETE = "#9CA3AF"

        # 1. Header
        self.create_header()

        # 2. List Container
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # 3. Load Data
        self.load_data()

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(header, text="MANAGE ANNOUNCEMENTS", font=("Arial", 20, "bold"), text_color="#115E59").pack(side="left")
        
        ctk.CTkButton(header, text="+ New Announcement", fg_color=self.COLOR_PRIMARY, hover_color="#059669", 
                      width=160, command=self.open_add_dialog).pack(side="right")

    def load_data(self):
        for w in self.scroll_area.winfo_children(): w.destroy()
        data = self.controller.get_all_announcements()
        
        if not data:
            ctk.CTkLabel(self.scroll_area, text="No announcements found.", text_color="gray").pack(pady=20)
            return

        for item in data:
            self.create_card(item)

    def create_card(self, data):
        # Card Container
        card = ctk.CTkFrame(self.scroll_area, fg_color="white", corner_radius=8, border_width=1, border_color="#E5E7EB")
        card.pack(fill="x", pady=8, ipady=5)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=15)

        # Row 1: Title + Actions
        r1 = ctk.CTkFrame(content, fg_color="transparent")
        r1.pack(fill="x")
        
        # Icon loa thông báo
        ctk.CTkLabel(r1, text="📢", font=("Arial", 14)).pack(side="left", pady=2)
        ctk.CTkLabel(r1, text=data['title'], font=("Arial", 13, "bold"), text_color="#333").pack(side="left", padx=10)

        # Actions (Edit/Delete)
        ctk.CTkButton(r1, text="✎", width=30, fg_color="transparent", text_color=self.COLOR_EDIT, hover_color="#F3F4F6",
                      command=lambda: self.open_edit_dialog(data)).pack(side="right")
        ctk.CTkButton(r1, text="🗑", width=30, fg_color="transparent", text_color=self.COLOR_DELETE, hover_color="#FEF2F2",
                      command=lambda: self.delete_item(data['announcement_id'])).pack(side="right", padx=5)

        # Row 2: Content
        desc_text = data['content'][:150] + "..." if len(data['content']) > 150 else data['content']
        ctk.CTkLabel(content, text=desc_text, font=("Arial", 12), text_color="#555", anchor="w", justify="left").pack(fill="x", padx=35, pady=(5, 10))

        # Row 3: Date
        r3 = ctk.CTkFrame(content, fg_color="transparent")
        r3.pack(fill="x", padx=35)
        ctk.CTkLabel(r3, text=str(data['created_date']), font=("Arial", 11), text_color="gray").pack(side="left")

    def delete_item(self, ann_id):
        if messagebox.askyesno("Confirm", "Delete this announcement?"):
            success, msg = self.controller.delete_announcement(ann_id)
            if success: self.load_data()
            else: messagebox.showerror("Error", msg)

    def open_add_dialog(self):
        AnnouncementDialog(self, "New Announcement", self.controller, self.load_data, user_id=self.user_id)

    def open_edit_dialog(self, data):
        AnnouncementDialog(self, "Edit Announcement", self.controller, self.load_data, data=data, user_id=self.user_id)


# ==========================================
# POPUP FORM (ĐÃ BỎ PRIORITY/TARGET)
# ==========================================
class AnnouncementDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, controller, callback, data=None, user_id=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.data = data
        self.user_id = user_id
        
        self.title(title)
        self.geometry("600x450") # Giảm chiều cao vì bớt field
        self.transient(parent)
        self.configure(fg_color="white")
        
        ctk.CTkLabel(self, text=title, font=("Arial", 18, "bold"), text_color="#333").pack(pady=20, anchor="w", padx=30)

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)

        # 1. Subject / Title
        ctk.CTkLabel(form, text="Subject / Title *", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", pady=(5, 5))
        self.ent_title = ctk.CTkEntry(form, placeholder_text="e.g. Exam Schedule", height=40)
        self.ent_title.pack(fill="x")

        # 2. Content
        ctk.CTkLabel(form, text="Content *", font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", pady=(15, 5))
        self.txt_content = ctk.CTkTextbox(form, height=180, border_width=1, border_color="#E5E7EB")
        self.txt_content.pack(fill="x")

        # 3. Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", height=80)
        btn_frame.pack(fill="x", side="bottom")
        
        inner_btn = ctk.CTkFrame(btn_frame, fg_color="transparent")
        inner_btn.pack(pady=20, padx=30, fill="x")

        ctk.CTkButton(inner_btn, text="Cancel", fg_color="white", border_color="#DDD", border_width=1, text_color="black", command=self.destroy).pack(side="left")
        
        btn_text = "Save Changes" if data else "Post Announcement"
        ctk.CTkButton(inner_btn, text=btn_text, fg_color="#10B981", hover_color="#059669", command=self.save).pack(side="right")

        # Fill Data
        if data:
            self.ent_title.insert(0, data['title'])
            self.txt_content.insert("0.0", data['content'])

        self.lift()
        self.focus_force()
        self.after(100, self.grab_set)

    def save(self):
        title = self.ent_title.get()
        content = self.txt_content.get("0.0", "end").strip()

        if not title or not content:
            messagebox.showwarning("Required", "Please fill in Title and Content", parent=self)
            return

        if self.data: # Update
            success, msg = self.controller.update_announcement(self.data['announcement_id'], title, content)
        else: # Create
            success, msg = self.controller.create_announcement(title, content, self.user_id)

        if success:
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)