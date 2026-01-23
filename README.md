# Student-Management-System

Student Management System (Desktop App) built with Python and MySQL, supporting role-based access control and credit-based training process management.

## 🚀 Key Features
- **User Roles**: Admin, Lecturer, Student.
- **Academic Management**: Manage Courses, Classes, Semesters, Departments.
- **Grade Management**: Lecturers enter grades, system calculates GPA, students view transcripts.
- **Utilities**: View schedule, notifications, password security (Bcrypt), OTP authentication.

## 🛠 Technologies Used
- **Language**: Python 3.x
- **Database**: MySQL
- **Interface (GUI)**: Tkinter / CustomTkinter
- **Security**: Bcrypt, Secrets

## 📄 Documentation
- **Project Structure**: [docs/Project Structure.md](docs/Project%20Structure.md)
- **Requirement Specification & Design Document**: [docs/Requirement Specification & Design Document - Group01.pdf](docs/Requirement%20Specification%20%26%20Design%20Document%20-%20Group01.pdf)
- **Requirements**: [requirements.txt](requirements.txt)

## ⚙️ Installation & Run

1. **Clone the project**
   ```bash
   git clone https://github.com/your-username/student-management-system.git
   cd student-management-system
   ```

2. **Setup Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Database**
   - Create MySQL database and run scripts in `docs/sql_script/`.
   - Copy `.env.example` to `.env` and fill in DB connection info.

5. **Run Application**
   ```bash
   python src/main.py
   ```