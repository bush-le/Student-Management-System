# Configuration settings
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv("MYSQLHOST") or os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("MYSQLPORT") or os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("MYSQLUSER") or os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD", "password")
    DB_NAME = os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME", "student_management_db")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_do_not_use_in_prod")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")