-- ==============================
-- USE DATABASE
-- ==============================
USE student_management_db;

-- ==============================
-- LIST TABLES
-- ==============================
SHOW TABLES;

-- ==============================
-- BASIC VIEW DATA
-- ==============================

-- Users
SELECT * FROM Users;

-- Departments
SELECT * FROM Departments;

-- Semesters
SELECT * FROM Semesters;

-- Academic_Officers
SELECT * FROM Academic_Officers;

-- Students
SELECT * FROM Students;

-- Lecturers
SELECT * FROM Lecturers;

-- Courses
SELECT * FROM Courses;

-- Course_Classes
SELECT * FROM Course_Classes;

-- Grades
SELECT * FROM Grades;

-- Announcements
SELECT * FROM Announcements;

-- ==============================
-- LIMIT VIEW (SAFE)
-- ==============================
SELECT * FROM Users LIMIT 10;
SELECT * FROM Students LIMIT 10;
SELECT * FROM Lecturers LIMIT 10;
SELECT * FROM Courses LIMIT 10;
SELECT * FROM Grades LIMIT 10;

-- ==============================
-- STRUCTURE CHECK
-- ==============================
DESCRIBE Users;
DESCRIBE Students;
DESCRIBE Lecturers;
DESCRIBE Courses;
DESCRIBE Course_Classes;
DESCRIBE Grades;

-- ==============================
-- RELATIONSHIP CHECK (JOINS)
-- ==============================

-- Student + User + Department
SELECT 
    s.student_id,
    s.student_code,
    u.username,
    u.full_name,
    u.email,
    d.dept_name,
    s.major,
    s.academic_year,
    s.gpa,
    s.academic_status
FROM Students s
JOIN Users u ON s.user_id = u.user_id
LEFT JOIN Departments d ON s.dept_id = d.dept_id;

-- Lecturer + User + Department
SELECT 
    l.lecturer_id,
    l.lecturer_code,
    u.full_name,
    u.email,
    d.dept_name,
    l.degree
FROM Lecturers l
JOIN Users u ON l.user_id = u.user_id
LEFT JOIN Departments d ON l.dept_id = d.dept_id;

-- Class + Course + Semester + Lecturer
SELECT 
    cc.class_id,
    c.course_code,
    c.course_name,
    s.name AS semester_name,
    u.full_name AS lecturer_name,
    cc.room,
    cc.schedule,
    cc.max_capacity
FROM Course_Classes cc
JOIN Courses c ON cc.course_id = c.course_id
JOIN Semesters s ON cc.semester_id = s.semester_id
LEFT JOIN Lecturers l ON cc.lecturer_id = l.lecturer_id
LEFT JOIN Users u ON l.user_id = u.user_id;

-- Grades + Student + Course
SELECT
    u.full_name AS student_name,
    st.student_code,
    c.course_name,
    g.attendance_score,
    g.midterm,
    g.final,
    g.total,
    g.letter_grade,
    g.is_locked,
    g.updated_at
FROM Grades g
JOIN Students st ON g.student_id = st.student_id
JOIN Users u ON st.user_id = u.user_id
JOIN Course_Classes cc ON g.class_id = cc.class_id
JOIN Courses c ON cc.course_id = c.course_id;

-- ==============================
-- DATA COUNT CHECK
-- ==============================
SELECT 'Users' AS table_name, COUNT(*) AS total FROM Users
UNION
SELECT 'Departments', COUNT(*) FROM Departments
UNION
SELECT 'Semesters', COUNT(*) FROM Semesters
UNION
SELECT 'Academic_Officers', COUNT(*) FROM Academic_Officers
UNION
SELECT 'Students', COUNT(*) FROM Students
UNION
SELECT 'Lecturers', COUNT(*) FROM Lecturers
UNION
SELECT 'Courses', COUNT(*) FROM Courses
UNION
SELECT 'Course_Classes', COUNT(*) FROM Course_Classes
UNION
SELECT 'Grades', COUNT(*) FROM Grades
UNION
SELECT 'Announcements', COUNT(*) FROM Announcements;
