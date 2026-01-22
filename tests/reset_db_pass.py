import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv

# Load config
load_dotenv()

# --- CẤU HÌNH (Sửa lại cho đúng máy bạn) ---
DB_CONFIG = {
    'host': os.getenv("MYSQLHOST") or os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("MYSQLUSER") or os.getenv("DB_USER", "root"),
    'password': os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD", "password"),
    'database': os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME", "student_management_db"),
    'port': int(os.getenv("MYSQLPORT") or os.getenv("DB_PORT", "3306"))
}

# Mật khẩu chung cho tất cả tài khoản
PLAIN_PASSWORD = "Test123!"

def force_update_passwords():
    print("🔄 Đang tạo mã Hash Bcrypt chuẩn...")
    
    # 1. Tạo Hash (Đây là đoạn code giống hệt trong src/utils/security.py)
    pwd_bytes = PLAIN_PASSWORD.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    hashed_string = hashed_bytes.decode('utf-8') # Chuỗi $2b$...

    print(f"🔑 Mật khẩu gốc: {PLAIN_PASSWORD}")
    print(f"🔒 Mã Hash mới:  {hashed_string}")
    print("-" * 50)

    try:
        # 2. Kết nối DB
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 3. Danh sách email cần sửa
        target_emails = [
            'student@test.com',
            'lecturer@test.com', 
            'admin@test.com',
            'tidk54737@gmail.com',
        ]

        # 4. Thực hiện Update
        print("⚡ Đang ghi đè mật khẩu trong Database...")
        for email in target_emails:
            # Kiểm tra xem user có tồn tại không
            cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                # Update
                sql = "UPDATE Users SET password = %s, status = 'ACTIVE', failed_login_attempts = 0 WHERE email = %s"
                cursor.execute(sql, (hashed_string, email))
                print(f"✅ Đã cập nhật thành công cho: {email}")
            else:
                print(f"⚠️ Không tìm thấy email: {email}")

        conn.commit()
        print("-" * 50)
        print("🎉 THÀNH CÔNG! Bây giờ bạn hãy chạy App và đăng nhập.")
        print(f"👉 Email: student@test.com")
        print(f"👉 Pass:  {PLAIN_PASSWORD}")

    except mysql.connector.Error as err:
        print(f"❌ LỖI KẾT NỐI DATABASE: {err}")
        print("👉 Hãy kiểm tra lại username/password trong biến DB_CONFIG ở đầu file này.")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    force_update_passwords()