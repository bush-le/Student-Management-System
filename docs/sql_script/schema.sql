CREATE DATABASE IF NOT EXISTS student_management_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE student_management_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY, 
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL, -- Supports Vietnamese via utf8mb4 DB
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    role ENUM('Student', 'Lecturer', 'Admin') NOT NULL,
    status ENUM('ACTIVE', 'LOCKED') DEFAULT 'ACTIVE',
    failed_login_attempts INT DEFAULT 0,
    lockout_time DATETIME
);

-- 2. Departments Table
CREATE TABLE IF NOT EXISTS Departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    office_location VARCHAR(100)
);

-- 3. Semesters Table
CREATE TABLE IF NOT EXISTS Semesters (
    semester_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('OPEN', 'CLOSED') DEFAULT 'OPEN'
);

-- 4. Academic_Officers Table
CREATE TABLE IF NOT EXISTS Academic_Officers (
    officer_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    admin_code VARCHAR(20) UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- 5. Students Table
CREATE TABLE IF NOT EXISTS Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    dept_id INT,
    student_code VARCHAR(20) UNIQUE NOT NULL,
    major VARCHAR(100),
    academic_year VARCHAR(10),
    gpa DECIMAL(3,2) DEFAULT 0.00,
    academic_status ENUM('ACTIVE', 'ON_LEAVE', 'DROPPED', 'GRADUATED') DEFAULT 'ACTIVE',
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (dept_id) REFERENCES Departments(dept_id) ON DELETE SET NULL
);

-- 6. Lecturers Table
CREATE TABLE IF NOT EXISTS Lecturers (
    lecturer_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    dept_id INT,
    lecturer_code VARCHAR(20) UNIQUE NOT NULL,
    degree VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (dept_id) REFERENCES Departments(dept_id) ON DELETE SET NULL
);

-- 7. Courses Table (LOGIC FIXED)
CREATE TABLE IF NOT EXISTS Courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY, -- Changed to INT for easier linking
    course_code VARCHAR(20) UNIQUE NOT NULL,  -- Store 'CS101' code here
    dept_id INT,
    course_name VARCHAR(100) NOT NULL,
    credits INT NOT NULL,
    description TEXT,
    prerequisite_id INT, -- Now INT points to INT correctly
    FOREIGN KEY (dept_id) REFERENCES Departments(dept_id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_id) REFERENCES Courses(course_id) ON DELETE SET NULL
);

-- 8. Course_Classes Table
CREATE TABLE IF NOT EXISTS Course_Classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL, -- Matches INT of Courses
    lecturer_id INT,
    semester_id INT NOT NULL,
    room VARCHAR(20),
    schedule VARCHAR(100),
    max_capacity INT DEFAULT 50,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (lecturer_id) REFERENCES Lecturers(lecturer_id) ON DELETE SET NULL,
    FOREIGN KEY (semester_id) REFERENCES Semesters(semester_id) ON DELETE CASCADE
);

-- 9. Grades Table
CREATE TABLE IF NOT EXISTS Grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    attendance_score DECIMAL(4,2),
    midterm DECIMAL(4,2),
    final DECIMAL(4,2),
    total DECIMAL(4,2),
    letter_grade VARCHAR(2),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_locked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES Course_Classes(class_id) ON DELETE CASCADE
);

-- 10. Announcements Table
CREATE TABLE IF NOT EXISTS Announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    officer_id INT,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (officer_id) REFERENCES Academic_Officers(officer_id) ON DELETE SET NULL
);