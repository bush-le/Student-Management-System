-- ============================================================
-- PERFORMANCE OPTIMIZATION: ADD INDEXES
-- ============================================================
-- Run this script in your MySQL to speed up queries

-- Students table indexes
CREATE INDEX idx_student_code ON Students(student_code);
CREATE INDEX idx_student_dept ON Students(dept_id);
CREATE INDEX idx_student_user ON Students(user_id);

-- Users table indexes
CREATE INDEX idx_user_email ON Users(email);
CREATE INDEX idx_user_username ON Users(username);
CREATE INDEX idx_user_role ON Users(role);

-- Course Classes indexes
CREATE INDEX idx_class_course ON Course_Classes(course_id);
CREATE INDEX idx_class_lecturer ON Course_Classes(lecturer_id);
CREATE INDEX idx_class_semester ON Course_Classes(semester_id);

-- Grades indexes
CREATE INDEX idx_grade_student ON Grades(student_id);
CREATE INDEX idx_grade_class ON Grades(class_id);

-- Announcements indexes
CREATE INDEX idx_ann_date ON Announcements(created_date);

-- Check existing indexes
SHOW INDEX FROM Students;
SHOW INDEX FROM Users;
SHOW INDEX FROM Course_Classes;
SHOW INDEX FROM Grades;
