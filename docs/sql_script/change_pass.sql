USE student_management_db;

-- Cập nhật mật khẩu thành 'Test123!' (đã mã hóa Bcrypt) cho tất cả tài khoản test
UPDATE Users 
SET password = '$2b$12$VAhrFRSHo6hclPxNXw9te.egwghgy09zfjOCCWYVeIwuBmnOtfISy' 
WHERE username IN ('student_test', 'lecturer_test', 'admin_test','test_forgetpassword');