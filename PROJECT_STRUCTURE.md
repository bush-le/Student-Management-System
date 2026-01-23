# Project Structure - Student Management System

This document describes the directory structure and software architecture of the project. The system is built using the **MVC (Model-View-Controller)** pattern combined with the **Repository Pattern** to separate the data access layer.

## 📂 Directory Structure

```text
Student-Management-System/
├── docs/                           # Project documentation & Database scripts
│   └── sql_script/
│       └── create_account_test.sql # Script to create sample data for testing
├── src/                            # Main source code
│   ├── config.py                   # System configuration (Load .env environment variables)
│   ├── main.py                     # Application entry point
│   │
│   ├── controllers/                # Business Logic Layer
│   │   ├── admin_controller.py     # Admin logic (CRUD, Statistics)
│   │   ├── auth_controller.py      # Authentication logic (Login, Reset Password)
│   │   ├── lecturer_controller.py  # Lecturer logic (Teaching schedule, Grading)
│   │   └── student_controller.py   # Student logic (View grades, Schedule)
│   │
│   ├── database/                   # Data Access Layer (Database Access)
│   │   ├── connection.py           # Connection management (Connection Pooling)
│   │   ├── repository.py           # BaseRepository (Parent class with common logic)
│   │   └── repositories/           # Specific Repositories for each Entity
│   │       ├── announcement_repo.py
│   │       ├── class_repo.py
│   │       ├── course_repo.py
│   │       ├── department_repo.py
│   │       ├── grade_repo.py
│   │       ├── lecturer_repo.py
│   │       ├── semester_repo.py
│   │       ├── student_repo.py
│   │       └── user_repo.py
│   │
│   ├── models/                     # Data Models (Map data from DB)
│   │   ├── user.py                 # Base User Model
│   │   ├── student.py              # Student Model
│   │   ├── lecturer.py             # Lecturer Model
│   │   └── academic/               # Academic models
│   │       ├── announcement.py
│   │       ├── course.py
│   │       ├── course_class.py
│   │       ├── department.py
│   │       ├── grade.py
│   │       └── semester.py
│   │
│   ├── utils/                      # Utility helpers
│   │   ├── email_service.py        # Email service (Resend API)
│   │   ├── security.py             # Security (Hash password, OTP)
│   │   └── validators.py           # Input validation (Regex)
│   │
│   └── views/                      # Presentation Layer (UI - CustomTkinter)
│       ├── root_app.py             # Main window management and navigation
│       ├── admin/                  # Admin Interface
│       │   ├── announcements.py
│       │   ├── classes.py
│       │   ├── courses.py
│   │   ├── dashboard.py        # Admin Dashboard
│       │   ├── lecturers.py
│       │   ├── semesters.py
│       │   └── student.py
│       └── student/                # Student Interface
│           └── grades.py           # View grades
│
└── tests/                          # Test scripts
    └── reset_db_pass.py            # Manual password reset tool
```
