# Configuration settings
import os
import sys
from dotenv import load_dotenv


# --- IMPORTANT: Path handling for .env file ---
# This ensures that the .env file is found whether running from source code or a frozen executable (e.g., PyInstaller).
if getattr(sys, 'frozen', False):
    # If the application is running as a bundled executable, the path is relative to the executable.
    application_path = os.path.dirname(sys.executable)
else:
    # If running as a normal script, the path is relative to this file.
    application_path = os.path.dirname(os.path.abspath(__file__))

dotenv_path = os.path.join(application_path, '.env')
load_dotenv(dotenv_path)
# ------------------------------------------------

class Config:
    DB_HOST = os.getenv("MYSQLHOST") or os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("MYSQLPORT") or os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("MYSQLUSER") or os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME", "student_management_db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_do_not_use_in_prod")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")