from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
import sqlite3
import hashlib
import datetime
import random
import string

app = Flask(__name__)

# 内存中的cookie表
cookie_table = []

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def find_user_id(cookie):
    current_timestamp = datetime.datetime.now().timestamp()
    # 在cookie_table中查找对应的用户id
    for user_id, token, expiration_time in cookie_table:
        if token == cookie and expiration_time > current_timestamp:
            return user_id

    # 如果未找到或已过期，返回None
    return None

def get_classroom_reservations(classroom_id):
    # 查询数据库获取教室的预约信息
    conn = sqlite3.connect('classroom_reservation.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT reservation.start_time, reservation.end_time, account.student_id
        FROM reservation
        JOIN account ON reservation.account_id = account.id
        WHERE reservation.classroom_id = ?
        ORDER BY reservation.start_time
    ''', (classroom_id,))
    reservations = cursor.fetchall()
    conn.close()
    return reservations
@app.route('/')
def home():
    user_id = find_user_id(request.cookies.get('token'))
    if user_id is not None:
        return redirect(url_for('book'))
    else:
        return redirect(url_for('login'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = int(request.form.get('username'))
        password = request.form.get('password')

        # 查询数据库验证用户名和密码
        conn = sqlite3.connect('classroom_reservation.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM account WHERE id = ? AND is_enabled = 1', (id,))
        user = cursor.fetchone()

        if user and hashlib.sha256(password.encode()).hexdigest() == user[1]:
            # 生成并存储用户token
            token = generate_token()
            expiration_time = datetime.datetime.now() + datetime.timedelta(hours=12)
            cookie_table.append((user[0], token, expiration_time.timestamp()))
            # 设置cookie
            response = redirect(url_for('book'))
            response.set_cookie('token', token)
            conn.close()
            return response
        else:
            error = "用户名或密码错误，或者用户被禁用。"
            conn.close()
            return render_template('login.html', title='西安科技大学教室预约系统', error=error)
    return render_template('login.html', title='西安科技大学教室预约系统')


@app.route('/logout', methods=['POST'])
def logout():
    try:
        token_to_remove = request.args.get('token')
        # 从cookie_table中移除对应记录
        global cookie_table
        cookie_table = [cookie for cookie in cookie_table if not (cookie[1] == token_to_remove)]

        response = make_response(redirect(url_for('login')))
        # 删除客户端cookie
        response.delete_cookie('token')
        response.delete_cookie('user_id')
        return response
    finally:
        return redirect(url_for('book'))

@app.route('/book', methods=['GET', 'POST'])
def book():
    # 获取当前用户信息
    cookie = request.cookies.get('token')
    user_id = find_user_id(cookie)
    if id is not None:
        # 获取教室列表
        classrooms = get_classrooms()
        # 获取当前用户的预约记录
        reservations = get_user_reservations(user_id)
        return render_template('book.html', title='预约页面', current_user=user_id, classrooms=classrooms,
                               reservations=reservations)
    else:
        response = redirect(url_for('login'))
        return response

@app.route('/reservations')
def reservations():
    all_reservations = get_specific_classrooms_reservations(cid=str(request.args.get('classroom_id')))
    return jsonify(all_reservations)

def get_classrooms():
    # 查询数据库获取教室列表
    conn = sqlite3.connect('classroom_reservation.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM classroom')
    classrooms = cursor.fetchall()
    conn.close()
    return classrooms

def get_user_reservations(user_id):
    # 查询数据库获取当前用户的预约记录
    conn = sqlite3.connect('classroom_reservation.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT reservation.id, classroom.location, reservation.start_time, reservation.end_time
        FROM reservation
        JOIN classroom ON reservation.classroom_id = classroom.id
        where reservation.id = ?
    ''', (user_id,))
    reservations = cursor.fetchall()
    conn.close()
    return reservations
def get_specific_classrooms_reservations(cid):
    # 查询数据库获取所有教室的预约信息
    conn = sqlite3.connect('classroom_reservation.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT reservation.classroom_id, reservation.start_time, reservation.end_time, account.username
        FROM reservation
        join account on reservation.account_id = account.id
        where reservation.classroom_id = ?
         ORDER BY reservation.classroom_id, reservation.start_time
    ''', (cid,))
    specific_classrooms_reservations = cursor.fetchall()
    conn.close()
    return specific_classrooms_reservations




if __name__ == "__main__":
    app.run(debug=True)
