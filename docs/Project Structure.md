StudentManagementSystem/
├── assets/                  # Images, icons, and system logos for UI design
│   ├── images/
│   └── icons/
├── data/                    # CSV templates for importing data (FR-18, UC15)
├── docs/                    # Requirements and design documents
├── src/                     # Main source code of the application
│   ├── main.py              # Entry point to start the app
│   ├── config.py            # Loads settings and environment variables
│   ├── database/            # Manages MySQL database connections (NFR-18)
│   │   ├── __init__.py
│   │   ├── connection.py    # Class to handle DB connection logic
│   │   └── schema.sql       # SQL script to create tables based on Data Model
│   ├── models/              # Defines OOP entities (Class Diagram p. 34)
│   │   ├── __init__.py
│   │   ├── user.py          # Parent User class (Common Module)
│   │   ├── student.py       # Student class inheriting from User
│   │   ├── lecturer.py      # Lecturer class inheriting from User
│   │   └── academic.py      # Classes for Course, Semester, Class, and Grade
│   ├── views/               # User Interfaces (Interface Design p. 35-52)
│   │   ├── __init__.py
│   │   ├── components/      # Shared UI widgets (Buttons, Tables, Headers)
│   │   ├── auth/            # Login and Forgot Password screens
│   │   ├── student/         # Student Dashboard, Schedule, and Grades UI
│   │   ├── lecturer/        # Lecturer Dashboard, Grading, and Roster UI
│   │   └── admin/           # Admin Dashboard and User Management UI
│   ├── controllers/         # Handles logic; bridges Models and Views
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── student_controller.py
│   │   ├── lecturer_controller.py
│   │   └── admin_controller.py
│   └── utils/               # Shared helper tools
│       ├── __init__.py
│       ├── email_service.py # Email handling (Resend/SMTP) (FR-04, UC04)
│       ├── security.py      # Password hashing and session logic (FR-03, NFR-09)
│       └── validators.py    # Checks if input data is valid (FR-06)
├── tests/                   # Folder for Unit and Integration tests
├── requirements.txt         # List of libraries to install (mysql-connector, etc.)
└── .env                     # Private file for secret keys and DB info (NFR-09)