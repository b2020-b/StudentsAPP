from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User:
    def __init__(self, username, password, role='user', name='', email=''):
        self.username = username
        self.password = password  # 实际使用时需要加密
        self.role = role  # admin 或 user
        self.name = name
        self.email = email
        self.created_at = datetime.now()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student:
    def __init__(self, student_id, name, department, course1_score, course2_score, 
                 course3_score, peer_score, teacher_score):
        self.student_id = student_id
        self.name = name
        self.department = department
        self.course1_score = course1_score
        self.course2_score = course2_score
        self.course3_score = course3_score
        self.peer_score = peer_score
        self.teacher_score = teacher_score
        
    @property
    def exam_average(self):
        return (self.course1_score + self.course2_score + self.course3_score) / 3
    
    @property
    def final_score(self):
        return (self.exam_average * 0.7 + 
                self.peer_score * 0.1 + 
                self.teacher_score * 0.2) 

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'department': self.department,
            'course1_score': self.course1_score,
            'course2_score': self.course2_score,
            'course3_score': self.course3_score,
            'peer_score': self.peer_score,
            'teacher_score': self.teacher_score,
            'exam_average': self.exam_average,
            'final_score': self.final_score
        }

class OperationLog:
    def __init__(self, user_id, operation_type, details, ip_address):
        self.user_id = user_id
        self.operation_type = operation_type
        self.details = details
        self.ip_address = ip_address
        self.created_at = datetime.now()