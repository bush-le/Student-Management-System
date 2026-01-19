USE student_management_db;

INSERT IGNORE INTO Departments (dept_id, dept_name, office_location) 
VALUES (1, 'Information Technology', 'Building C, Room 109');


INSERT INTO Users (username, password, full_name, email, phone, role, status) 
VALUES (
    'student_test', 
    '0b14d501a594442a01c6859541bcb3e8164d183d32937b851835442f69d5c94e', 
    'Nguyen Van Student', 
    'student@test.com', 
    '0901111111', 
    'Student', 
    'ACTIVE'
);

INSERT INTO Students (user_id, student_code, dept_id, major, academic_year, gpa, academic_status)
VALUES (
    (SELECT user_id FROM Users WHERE email='student@test.com'), 
    'SV2024001', 
    1, 
    'Software Engineering', 
    '2024-2028',
    3.5,
    'ACTIVE'
);


INSERT INTO Users (username, password, full_name, email, phone, role, status) 
VALUES (
    'lecturer_test', 
    '0b14d501a594442a01c6859541bcb3e8164d183d32937b851835442f69d5c94e', 
    'Dr. Tran Lecturer', 
    'lecturer@test.com', 
    '0902222222', 
    'Lecturer', 
    'ACTIVE'
);

INSERT INTO Lecturers (user_id, lecturer_code, degree, dept_id)
VALUES (
    (SELECT user_id FROM Users WHERE email='lecturer@test.com'), 
    'GV2024001', 
    'PhD', 
    1
);


INSERT INTO Users (username, password, full_name, email, phone, role, status) 
VALUES (
    'admin_test', 
    '0b14d501a594442a01c6859541bcb3e8164d183d32937b851835442f69d5c94e', 
    'Admin Officer', 
    'admin@test.com', 
    '0903333333', 
    'Admin', 
    'ACTIVE'
);

INSERT INTO Academic_Officers (user_id, admin_code)
VALUES (
    (SELECT user_id FROM Users WHERE email='admin@test.com'), 
    'AD2024001'
);