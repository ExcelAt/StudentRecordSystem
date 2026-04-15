create database student_records_db; 

use student_records_db; 

DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;

use student_records_db; 
create table students (
	student_id int auto_increment primary key, 
	name varchar (100) not null, 
	surname varchar (100) not null,
	email varchar (100) not null unique, 
	# major varchar (100) not null, 
    gender varchar (100) not null, 
	date_of_birth date not null
);


create table courses (
	course_id int auto_increment primary key, 
	course_name varchar (100) not null, 
	major varchar (100) not null, 
	duration_months int not null,
    
    check (duration_months between 1 and 24 )
); 



create table enrollments (
	enrollment_id int auto_increment primary key,
    student_id int,
    course_id int, 
    
    foreign key (student_id) references students (student_id), 
    foreign key (course_id) references courses (course_id)
    
);

create table grades (
	grade_id int auto_increment primary key, 
    enrollment_id int, 
    assignment_grade decimal(5,2) not null, 
    exam_grade decimal(5,2) not null,
    final_grade decimal(5,2) not null, 
    
    check (assignment_grade between 0 and 100), 
    check (exam_grade between 0 and 100), 
    check (final_grade between 0 and 100), 
    
    foreign key (enrollment_id) references enrollments (enrollment_id)

); 

create table attendance (
	attendance_id int auto_increment primary key, 
    enrollment_id int, 
	attendance_percentage decimal(5,2) not null, 
    
    check (attendance_percentage between 0 and 100), 
    
	foreign key (enrollment_id) references enrollments (enrollment_id)
); 


select * from courses; 
select * from students;
select * from attendance;
select * from grades; 
select * from enrollments;




