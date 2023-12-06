
import hashlib
import random
import sqlite3
import hashlib
from datetime import datetime, timedelta
def create_tables():
    # 连接数据库，如果不存在则创建
    conn = sqlite3.connect('classroom_reservation.db')
    cursor = conn.cursor()

    # 创建账号表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(20) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL,
            is_enabled BOOLEAN DEFAULT 1
        )
    ''')

    # 创建教室表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classroom (
            id VARCHAR(20) PRIMARY KEY,
            location VARCHAR(50) NOT NULL
        )
    ''')

    # 创建预约表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            classroom_id VARCHAR(20) NOT NULL,
            account_id INTEGER NOT NULL,
            start_time INTEGER NOT NULL,
            end_time INTEGER NOT NULL,
            FOREIGN KEY (classroom_id) REFERENCES classroom (id),
            FOREIGN KEY (account_id) REFERENCES account (id)
        )
    ''')

    # 提交更改并关闭连接
    conn.commit()
    conn.close()

def insert_sample_data():
    # 连接数据库
    conn = sqlite3.connect('classroom_reservation.db')
    cursor = conn.cursor()

    # 插入账号数据
    for i in range(9):
        username = f'00{i}'
        password = hashlib.sha256('12345'.encode()).hexdigest()
        is_enabled = random.choice([True, False])

        cursor.execute('''
            INSERT INTO account (username, password, is_enabled)
            VALUES (?, ?, ?)
        ''', (username, password, is_enabled))

    # 插入教室数据
    classrooms = [('2-3-101', '三号教学楼'), ('2-3-102', '三号教学楼')]
    cursor.executemany('''
        INSERT INTO classroom (id, location)
        VALUES (?, ?)
    ''', classrooms)

    # 提交更改并关闭连接
    conn.commit()
    conn.close()

def insert_reservation_data():
    # 连接数据库
    conn = sqlite3.connect('classroom_reservation.db')
    cursor = conn.cursor()

    # 查询教室和账号ID以便创建预约数据
    cursor.execute('SELECT id FROM classroom')
    classroom_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute('SELECT id FROM account')
    account_ids = [row[0] for row in cursor.fetchall()]

    # 插入三条预约数据
    for _ in range(8):
        classroom_id = random.choice(classroom_ids)
        account_id = random.choice(account_ids)
        start_time = datetime.now() - timedelta(hours=random.randint(5, 10)) - timedelta(minutes=18) + timedelta(days=random.randint(1, 7))
        end_time = start_time + timedelta(hours=random.randint(1, 3))

        cursor.execute('''
            INSERT INTO reservation (classroom_id, account_id, start_time, end_time)
            VALUES (?, ?, ?, ?)
        ''', (classroom_id, account_id, start_time.timestamp(), end_time.timestamp()))

    # 提交更改并关闭连接
    conn.commit()
    conn.close()

if __name__ == "__main__":
    #create_tables()
    #print("数据库初始化成功！")
    #insert_sample_data()
    #print("数据插入成功！")
    insert_reservation_data()
    print("预约数据插入成功！")
