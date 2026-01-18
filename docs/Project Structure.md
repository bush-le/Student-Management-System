StudentManagementSystem/
├── assets/                  # UI assets like images and icons
│   ├── images/
│   └── icons/
├── data/                    # Templates for bulk data import (e.g., students.csv)
├── docs/                    # Official Requirements and Design documentation
├── src/                     # Core application source code
│   ├── main.py              # Application entry point
│   ├── config.py            # Global settings and environment loader
│   ├── database/            # MySQL storage management
│   │   ├── __init__.py
│   │   ├── connection.py    # Handles database connection sessions
│   │   └── schema.sql       # SQL scripts to build the database tables
│   ├── models/              # OOP Entity definitions
│   │   ├── __init__.py
│   │   ├── user.py          # Base User class (Common Module)
│   │   ├── student.py       # Student class inheriting from User
│   │   ├── lecturer.py      # Lecturer class inheriting from User
│   │   └── academic/        # Sub-package for school-related entities
│   │       ├── __init__.py
│   │       ├── department.py   # Department information
│   │       ├── semester.py     # Academic terms and dates
│   │       ├── course.py       # Course catalog details (Credits, etc.)
│   │       ├── course_class.py # Specific class sections and schedules
│   │       ├── grade.py        # Student scores and GPA calculations
│   │       └── announcement.py # System notifications and alerts
│   ├── views/               # GUI layers separated by user role
│   │   ├── __init__.py
│   │   ├── components/      # Reusable UI widgets (custom buttons, inputs)
│   │   ├── auth/            # Login, Forgot, and Change Password screens
│   │   ├── student/         # Dashboard, Schedule, and Result interfaces
│   │   ├── lecturer/        # Grading and Roster management screens
│   │   └── admin/           # System administration and data management
│   ├── controllers/         # Bridges logic between Models and Views
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── student_controller.py
│   │   ├── lecturer_controller.py
│   │   └── admin_controller.py
│   └── utils/               # Shared helper functions
│       ├── __init__.py
│       ├── email_service.py # Password recovery email handler
│       ├── security.py      # Encryption and hashing for passwords
│       └── validators.py    # Data format validation (email, phone, etc.)
├── tests/                   # Automated tests for each module
├── requirements.txt         # Required Python packages (mysql-connector, etc.)
└── .env                     # Private environment variables