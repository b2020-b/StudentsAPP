



# 学生成绩管理系统

## 项目简介

这是一个基于 Python Flask 框架开发的学生成绩管理系统，提供了学生成绩的excel录入、管理、分析等功能。系统采用 Web 界面，支持 Excel 导入导出，并提供了直观的数据可视化分析功能。

## 用户需求

老师提供了学生成绩的excel录入、然后将数据导入到系统中管理、分析等功能。

## 技术栈

- 后端：Python Flask
- 前端：HTML, CSS, JavaScript
- 数据库：MySQL
- 数据处理：pandas
- 图表可视化：ECharts
- Excel处理：pandas

## 功能特点

1. 用户认证
   - 登录/退出功能
   - 默认管理员账号：admin/admin
   - 访问控制和会话管理

2. 成绩管理
   - Excel模板下载
   - 批量导入学生成绩
   - 支持成绩的增删改查
   - 自动计算平均分和综合测评分

3. 数据分析
   - 成绩概览（平均分、最高分、最低分）
   - 成绩分布分析
   - 及格率和优秀率统计
   - 可视化图表展示

## 项目结构



student_management/

├── app.py # 主应用程序

├── database.py # 数据库操作

├── models.py # 数据模型

├── static/

│ ├── style.css # 样式文件

│ └── js/

│ └── echarts.min.js # 图表库

└── templates/

├── login.html # 登录页面

├── index.html # 成绩管理页面

└── visualization.html # 成绩分析页面



## 安装说明

1. 环境要求

   - Python 3.7+
   - MySQL 8.0+

2. 安装依赖

   bash

   pip install flask

   pip install pymysql

   pip install pandas

   pip install openpyxl

3. 数据库配置

   sql

   CREATE DATABASE student_management;



4. 修改数据库连接信息
   在 database.py 中配置：

python

self.conn = pymysql.connect(

host='localhost',

user='your_username',

password='your_password',

database='student_management',

charset='utf8mb4'

)



5. 运行应用

   bash

   python app.py

## 使用说明

1. 系统登录
   - 访问 http://localhost:5000
   - 使用默认账号：admin/admin

2. 成绩管理
   - 下载 Excel 模板
   - 按模板格式填写学生信息
   - 导入 Excel 文件
   - 支持修改和删除学生信息

3. 成绩分析
   - 查看成绩概览图表
   - 查看成绩分布统计
   - 查看详细统计数据

## 数据结构

学生信息包含：

- 学号（主键）
- 姓名
- 院系
- 语文成绩
- 英语成绩
- 数学成绩
- 同学互评分
- 教师评分

综合测评总分计算：

- 考试平均成绩：70%
- 同学互评分：10%
- 教师评分：20%

















