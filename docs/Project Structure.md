Directory structure:
└── bush-le-student-management-system/
    ├── README.md
    ├── PROJECT_STRUCTURE.md
    ├── requirements.txt
    ├── data/
    │   └── students_template.csv
    ├── docs/
    │   └── Project Structure.md
    └── src/
        ├── config.py
        ├── main.py
        ├── controllers/
        │   ├── __init__.py
        │   ├── admin_controller.py
        │   ├── auth_controller.py
        │   ├── lecturer_controller.py
        │   └── student_controller.py
        ├── database/
        │   ├── __init__.py
        │   ├── connection.py
        │   ├── repository.py
        │   └── repositories/
        │       ├── announcement_repo.py
        │       ├── class_repo.py
        │       ├── course_repo.py
        │       ├── department_repo.py
        │       ├── grade_repo.py
        │       ├── lecturer_repo.py
        │       ├── semester_repo.py
        │       ├── student_repo.py
        │       └── user_repo.py
        ├── models/
        │   ├── __init__.py
        │   ├── academic.py
        │   ├── lecturer.py
        │   ├── student.py
        │   ├── user.py
        │   └── academic/
        │       ├── __init__.py
        │       ├── announcement.py
        │       ├── course.py
        │       ├── course_class.py
        │       ├── department.py
        │       ├── grade.py
        │       └── semester.py
        ├── utils/
        │   ├── __init__.py
        │   ├── cache.py
        │   ├── constants.py
        │   ├── email_service.py
        │   ├── pagination.py
        │   ├── security.py
        │   ├── threading_helper.py
        │   └── validators.py
        └── views/
            ├── root_app.py
            ├── admin/
            │   ├── __init__.py
            │   ├── announcements.py
            │   ├── classes.py
            │   ├── courses.py
            │   ├── dashboard.py
            │   ├── lecturers.py
            │   ├── semesters.py
            │   └── student.py
            ├── auth/
            │   ├── __init__.py
            │   ├── forgot_password.py
            │   └── login_window.py
            ├── lecturer/
            │   ├── __init__.py
            │   ├── class_manager.py
            │   ├── dashboard.py
            │   ├── grading.py
            │   ├── my_class.py
            │   └── schedule.py
            └── student/
                ├── __init__.py
                ├── dashboard.py
                ├── grades.py
                ├── notifications.py
                ├── profile.py
                └── schedule.py
