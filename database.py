import pymysql
from pymysql import Error

class Database:
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host='localhost',
                user='root',
                password='root',
                database='student_management',
                charset='utf8mb4'
            )
            self.cursor = self.conn.cursor()
            self.create_tables()
        except Error as e:
            print(f"数据库连接错误: {e}")

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                department VARCHAR(50),
                course1_score FLOAT,
                course2_score FLOAT,
                course3_score FLOAT,
                peer_score FLOAT,
                teacher_score FLOAT
            )
        ''')

        # 创建用户表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                role VARCHAR(20) NOT NULL,
                name VARCHAR(50),
                email VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建操作日志表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                operation_type VARCHAR(50) NOT NULL,
                details TEXT,
                ip_address VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

    def add_student(self, student):
        sql = '''INSERT INTO students VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        values = (student.student_id, student.name, student.department,
                 student.course1_score, student.course2_score, student.course3_score,
                 student.peer_score, student.teacher_score)
        self.cursor.execute(sql, values)
        self.conn.commit()

    def get_all_students(self):
        self.cursor.execute("SELECT * FROM students")
        return self.cursor.fetchall()

    def get_student(self, student_id):
        self.cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        return self.cursor.fetchone()

    def update_student(self, student):
        sql = '''UPDATE students SET name=%s, department=%s, course1_score=%s,
                course2_score=%s, course3_score=%s, peer_score=%s, teacher_score=%s
                WHERE student_id=%s'''
        values = (student.name, student.department, student.course1_score,
                 student.course2_score, student.course3_score, student.peer_score,
                 student.teacher_score, student.student_id)
        self.cursor.execute(sql, values)
        self.conn.commit()

    def delete_student(self, student_id):
        self.cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        self.conn.commit()

    def clear_all_students(self):
        self.cursor.execute("DELETE FROM students")
        self.conn.commit()

    def get_all_student_ids(self):
        """获取所有学生的学号列表"""
        self.cursor.execute("SELECT student_id FROM students")
        return [row[0] for row in self.cursor.fetchall()]

    # 用户管理相关方法
    def add_user(self, user):
        sql = '''INSERT INTO users (username, password, role, name, email)
                 VALUES (%s, %s, %s, %s, %s)'''
        values = (user.username, user.password, user.role, user.name, user.email)
        self.cursor.execute(sql, values)
        self.conn.commit()

    def get_user(self, username):
        sql = '''SELECT * FROM users WHERE username = %s'''
        self.cursor.execute(sql, (username,))
        return self.cursor.fetchone()

    def get_all_users(self):
        sql = '''SELECT id, username, role, created_at FROM users'''
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    # 日志记录方法
    def add_log(self, log):
        sql = '''INSERT INTO operation_logs 
                 (user_id, operation_type, details, ip_address)
                 VALUES (%s, %s, %s, %s)'''
        values = (log.user_id, log.operation_type, log.details, log.ip_address)
        self.cursor.execute(sql, values)
        self.conn.commit()

    # 数据导出方法
    def export_student_data(self):
        sql = '''SELECT s.*, 
                 (course1_score + course2_score + course3_score)/3 as avg_score,
                 (course1_score + course2_score + course3_score)/3 * 0.7 + 
                 peer_score * 0.1 + teacher_score * 0.2 as final_score
                 FROM students s'''
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_logs(self):
        self.cursor.execute('''
            SELECT l.*, u.username 
            FROM operation_logs l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC
        ''')
        return self.cursor.fetchall()

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close() 