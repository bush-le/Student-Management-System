# Entry point for the application
import customtkinter as ctk
from views.root_app import RootApp

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

if __name__ == "__main__":
    app = RootApp()
    app.mainloop()