from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
from database import Database
from models import Student, User, OperationLog
import pandas as pd
import os
from functools import wraps
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 设置密钥，用于session加密
db = Database()

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 用户权限装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            return jsonify({"error": "需要管理员权限"}), 403
        return f(*args, **kwargs)
    return decorated_function

# 记录操作日志
def log_operation(operation_type, details):
    if 'user_id' in session:
        log = OperationLog(
            session['user_id'],
            operation_type,
            details,
            request.remote_addr
        )
        db.add_log(log)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['user_id'] = 1  # 假设admin的ID为1
            session['role'] = 'admin'
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/visualization')
@login_required
def visualization():
    return render_template('visualization.html')

@app.route('/api/students', methods=['GET'])
@login_required
def get_students():
    students = db.get_all_students()
    return jsonify(students)

@app.route('/api/download-template')
@login_required
def download_template():
    template_data = {
        'student_id': ['示例：20230001'],
        'name': ['张三'],
        'department': ['计算机系'],
        'course1_score': ['语文成绩示例：90'],
        'course2_score': ['英语成绩示例：85'],
        'course3_score': ['数学成绩示例：88'],
        'peer_score': ['互评分示例：90'],
        'teacher_score': ['教师评分示例：92']
    }
    
    df = pd.DataFrame(template_data)
    df = df.rename(columns={
        'course1_score': '语文',
        'course2_score': '英语',
        'course3_score': '数学',
        'student_id': '学号',
        'name': '姓名',
        'department': '院系',
        'peer_score': '互评分',
        'teacher_score': '教师评分'
    })
    
    template_path = 'static/student_template.xlsx'
    df.to_excel(template_path, index=False)
    
    return send_file(template_path, as_attachment=True, 
                    download_name='学生成绩导入模板.xlsx')

@app.route('/api/import-excel', methods=['POST'])
@login_required
def import_excel():
    try:
        file = request.files['file']
        if not file:
            return jsonify({"message": "请选择文件"}), 400

        df = pd.read_excel(file)
        
        column_mapping = {
            '语文': 'course1_score',
            '英语': 'course2_score',
            '数学': 'course3_score',
            '学号': 'student_id',
            '姓名': 'name',
            '院系': 'department',
            '互评分': 'peer_score',
            '教师评分': 'teacher_score'
        }
        df = df.rename(columns=column_mapping)
        
        required_columns = ['student_id', 'name', 'department', 
                          'course1_score', 'course2_score', 'course3_score',
                          'peer_score', 'teacher_score']
        
        if not all(col in df.columns for col in required_columns):
            return jsonify({"message": "Excel格式不正确，请使用提供的模板"}), 400

        existing_students = db.get_all_student_ids()
        
        success_count = 0
        update_count = 0
        error_count = 0
        
        for _, row in df.iterrows():
            try:
                student = Student(
                    str(row['student_id']),
                    row['name'],
                    row['department'],
                    float(row['course1_score']),
                    float(row['course2_score']),
                    float(row['course3_score']),
                    float(row['peer_score']),
                    float(row['teacher_score'])
                )
                
                if str(row['student_id']) in existing_students:
                    db.update_student(student)
                    update_count += 1
                else:
                    db.add_student(student)
                    success_count += 1
                    
            except Exception as e:
                error_count += 1
                print(f"导入行数据失败: {e}")
                continue
            
        message = f"导入完成。新增: {success_count}条, 更新: {update_count}条"
        if error_count > 0:
            message += f", 失败: {error_count}条"
            
        log_operation('import_excel', message)
        return jsonify({"message": message})
    except Exception as e:
        return jsonify({"message": f"导入失败：{str(e)}"}), 500

@app.route('/api/students/<student_id>', methods=['DELETE'])
@login_required
def delete_student(student_id):
    try:
        db.delete_student(student_id)
        log_operation('delete_student', f'删除学生: {student_id}')
        return jsonify({"message": "删除成功"})
    except Exception as e:
        return jsonify({"message": f"删除失败：{str(e)}"}), 500

@app.route('/api/students/<student_id>', methods=['PUT'])
@login_required
def update_student(student_id):
    try:
        data = request.json
        student = Student(
            student_id,
            data['name'],
            data['department'],
            float(data['course1_score']),
            float(data['course2_score']),
            float(data['course3_score']),
            float(data['peer_score']),
            float(data['teacher_score'])
        )
        db.update_student(student)
        log_operation('update_student', f'更新学生: {student_id}')
        return jsonify({"message": "修改成功"})
    except Exception as e:
        return jsonify({"message": f"修改失败：{str(e)}"}), 500

@app.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    users = db.get_all_users()
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
@admin_required
def add_user():
    data = request.json
    user = User(
        data['username'],
        hashlib.sha256(data['password'].encode()).hexdigest(),
        data.get('role', 'user'),
        data.get('name', ''),
        data.get('email', '')
    )
    db.add_user(user)
    log_operation('add_user', f'添加用户: {user.username}')
    return jsonify({"message": "用户添加成功"})

@app.route('/api/export-data')
@login_required
def export_data():
    try:
        students = db.get_all_students()
        df = pd.DataFrame(students, columns=[
            '学号', '姓名', '院系', '语文', '英语', '数学',
            '互评分', '教师评分'
        ])
        
        # 添加计算列
        df['平均分'] = df[['语文', '英语', '数学']].mean(axis=1)
        df['综合测评'] = df['平均分'] * 0.7 + df['互评分'] * 0.1 + df['教师评分'] * 0.2
        
        # 确保导出目录存在
        os.makedirs('static/exports', exist_ok=True)
        
        filename = f'student_scores_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        export_path = os.path.join('static/exports', filename)
        df.to_excel(export_path, index=False)
        
        log_operation('export_data', f'导出成绩数据: {filename}')
        return send_file(export_path, as_attachment=True)
    except Exception as e:
        return jsonify({"message": f"导出失败：{str(e)}"}), 500

@app.route('/api/batch-update', methods=['POST'])
@admin_required
def batch_update():
    data = request.json
    success_count = 0
    for student_data in data['students']:
        try:
            student = Student(**student_data)
            db.update_student(student)
            success_count += 1
        except Exception as e:
            continue
    
    log_operation('batch_update', f'批量更新学生信息: {success_count}条')
    return jsonify({"message": f"成功更新{success_count}条记录"})

@app.route('/api/logs')
@admin_required
def get_logs():
    logs = db.get_logs()
    return jsonify(logs)

if __name__ == '__main__':
    # 确保static目录存在
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/exports', exist_ok=True)
    app.run(debug=True)