USE student_management_db;

ALTER TABLE Users 
ADD COLUMN address VARCHAR(255) NULL,
ADD COLUMN dob DATE NULL;

UPDATE Users 
SET address = '123 Vo Van Ngan, Thu Duc, HCMC', dob = '2002-05-15' 
WHERE email = 'student@test.com';