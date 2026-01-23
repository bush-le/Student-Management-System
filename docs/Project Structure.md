Directory structure:
└── bush-le-student-management-system/
    ├── .env.example                # Template for environment variables (DB credentials, secrets)
    ├── .gitignore                  # Specifies files to be ignored by Git (e.g., venv, __pycache__)
    ├── README.md                   # Project overview, setup instructions, and usage guide
    ├── requirements.txt            # List of Python dependencies (install via pip)
    ├── data/                       # Directory for raw data or seed files
    │   └── students_template.csv   # CSV template for importing student data
    ├── docs/                       # Project documentation
    │   ├── Project Structure.md    # Current file describing the architecture
    │   └── sql_script/             # SQL scripts for database management
    │       ├── optimize_indexes.sql # Scripts to add indexes for performance
    │       ├── reset_passwordtoken.sql # Script to handle password reset tokens
    │       ├── schema.sql          # Main database schema definition
    │       ├── show_db.sql         # Utility to inspect database state
    │       └── update_address.sql  # Migration script for address updates
    ├── logs/                       # Directory for application log files (error.log, app.log)
    │   └── .gitkeep                # Keeps the folder in git even if empty
    ├── scripts/                    # Utility scripts for maintenance and setup
    │   └── db_setup.py             # Script to initialize or reset the database
    ├── src/                        # Source code root directory
    │   ├── config.py               # Configuration settings (loads env vars)
    │   ├── main.py                 # Application entry point
    │   ├── controllers/            # Business logic layer (handles user requests)
    │   │   ├── __init__.py
    │   │   ├── admin_controller.py # Logic for admin operations
    │   │   ├── auth_controller.py  # Logic for authentication (login, logout)
    │   │   ├── lecturer_controller.py # Logic for lecturer operations
    │   │   └── student_controller.py # Logic for student operations
    │   ├── database/               # Database access layer
    │   │   ├── __init__.py
    │   │   ├── connection.py       # Database connection handling (Singleton/Pool)
    │   │   ├── repository.py       # Base repository class
    │   │   └── repositories/       # Specific repositories for each entity
    │   │       ├── announcement_repo.py
    │   │       ├── class_repo.py
    │   │       ├── course_repo.py
    │   │       ├── dashboard_repo.py
    │   │       ├── department_repo.py
    │   │       ├── grade_repo.py
    │   │       ├── lecturer_repo.py
    │   │       ├── semester_repo.py
    │   │       ├── student_repo.py
    │   │       └── user_repo.py
    │   ├── models/                 # Data models (Entities/DTOs)
    │   │   ├── __init__.py
    │   │   ├── academic.py         # Base models for academic entities
    │   │   ├── lecturer.py         # Lecturer entity model
    │   │   ├── student.py          # Student entity model
    │   │   ├── user.py             # Base User entity model
    │   │   └── academic/           # Detailed academic models
    │   │       ├── __init__.py
    │   │       ├── announcement.py
    │   │       ├── course.py
    │   │       ├── course_class.py
    │   │       ├── department.py
    │   │       ├── grade.py
    │   │       └── semester.py
    │   ├── utils/                  # Helper functions and utilities
    │   │   ├── __init__.py
    │   │   ├── cache.py            # Caching mechanism
    │   │   ├── constants.py        # Global constants
    │   │   ├── email_service.py    # Email sending utility
    │   │   ├── pagination.py       # Pagination helper
    │   │   ├── security.py         # Security utils (hashing, OTP, validation)
    │   │   ├── threading_helper.py # Multithreading helpers
    │   │   └── validators.py       # Input validation helpers
    │   └── views/                  # UI Layer (Tkinter/PyQt views)
    │       ├── root_app.py         # Main application window setup
    │       ├── admin/              # Admin specific views
    │       │   ├── __init__.py
    │       │   ├── announcements.py
    │       │   ├── classes.py
    │       │   ├── courses.py
    │       │   ├── dashboard.py
    │       │   ├── lecturers.py
    │       │   ├── semesters.py
    │       │   └── student.py
    │       ├── auth/               # Authentication views
    │       │   ├── __init__.py
    │       │   ├── forgot_password.py
    │       │   └── login_window.py
    │       ├── lecturer/           # Lecturer specific views
    │       │   ├── __init__.py
    │       │   ├── class_manager.py
    │       │   ├── dashboard.py
    │       │   ├── grading.py
    │       │   ├── my_class.py
    │       │   └── schedule.py
    │       └── student/            # Student specific views
    │           ├── __init__.py
    │           ├── dashboard.py
    │           ├── grades.py
    │           ├── notifications.py
    │           ├── profile.py
    │           └── schedule.py
    └── tests/                      # Unit and integration tests
        ├── __init__.py
        ├── conftest.py             # Pytest configuration and fixtures
        ├── unit/                   # Unit tests for individual functions
        └── integration/            # Integration tests for modules