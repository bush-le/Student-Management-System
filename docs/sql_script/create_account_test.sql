USE student_management_db;

-- 1. XÓA DỮ LIỆU CŨ SAI HASH
DELETE FROM Students WHERE student_code = 'SV2024001';
DELETE FROM Lecturers WHERE lecturer_code = 'GV2024001';
DELETE FROM Academic_Officers WHERE admin_code = 'AD2024001';
DELETE FROM Users WHERE email IN ('student@test.com', 'lecturer@test.com', 'admin@test.com');

-- 2. TẠO LẠI USER VỚI HASH ĐÚNG CHO 'Test123!'
-- Hash đúng: 54de7f606f2523cba8efac173fab42fb7f59d56ceff974c8fdb7342cf2cfe345

-- STUDENT
INSERT INTO Users (username, password, full_name, email, phone, role, status) 
VALUES ('student_test', '54de7f606f2523cba8efac173fab42fb7f59d56ceff974c8fdb7342cf2cfe345', 'Nguyen Van Student', 'student@test.com', '0901111111', 'Student', 'ACTIVE');

INSERT INTO Students (user_id, student_code, dept_id, major, academic_year, gpa, academic_status)
VALUES ((SELECT user_id FROM Users WHERE email='student@test.com'), 'SV2024001', 1, 'Software Engineering', '2024-2028', 3.5, 'ACTIVE');

-- LECTURER
INSERT INTO Users (username, password, full_name, email, phone, role, status) 
VALUES ('lecturer_test', '54de7f606f2523cba8efac173fab42fb7f59d56ceff974c8fdb7342cf2cfe345', 'Dr. Tran Lecturer', 'lecturer@test.com', '0902222222', 'Lecturer', 'ACTIVE');

INSERT INTO Lecturers (user_id, lecturer_code, degree, dept_id)
VALUES ((SELECT user_id FROM Users WHERE email='lecturer@test.com'), 'GV2024001', 'PhD', 1);

-- ADMIN
INSERT INTO Users (username, password, full_name, email, phone, role, status) 
VALUES ('admin_test', '54de7f606f2523cba8efac173fab42fb7f59d56ceff974c8fdb7342cf2cfe345', 'Admin Officer', 'admin@test.com', '0903333333', 'Admin', 'ACTIVE');

INSERT INTO Academic_Officers (user_id, admin_code)
VALUES ((SELECT user_id FROM Users WHERE email='admin@test.com'), 'AD2024001');

