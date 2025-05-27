from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import time

app = Flask(__name__)

# 初始化資料庫
def init_db():
    with sqlite3.connect('work_logs.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS work_logs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      task_name TEXT NOT NULL,
                      start_time TEXT NOT NULL,
                      end_time TEXT,
                      duration INTEGER)''')
        conn.commit()

# 啟動時初始化資料庫
init_db()

# 新增工作
@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    task_name = data['task_name']
    with sqlite3.connect('work_logs.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO work_logs (task_name, start_time) VALUES (?, ?)",
                  (task_name, datetime.now().isoformat()))
        conn.commit()
        return jsonify({'id': c.lastrowid})

# 開始計時
@app.route('/start_task/<int:task_id>', methods=['POST'])
def start_task(task_id):
    with sqlite3.connect('work_logs.db') as conn:
        c = conn.cursor()
        # 停止其他正在計時的工作
        c.execute("UPDATE work_logs SET end_time = ?, duration = ? WHERE end_time IS NULL AND id != ?",
                  (datetime.now().isoformat(), int(time.time()), task_id))
        # 開始新計時
        c.execute("INSERT INTO work_logs (task_name, start_time) SELECT task_name, ? FROM work_logs WHERE id = ?",
                  (datetime.now().isoformat(), task_id))
        conn.commit()
        return jsonify({'status': 'started'})

# 停止計時
@app.route('/stop_task/<int:task_id>', methods=['POST'])
def stop_task(task_id):
    with sqlite3.connect('work_logs.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE work_logs SET end_time = ?, duration = ? WHERE id = ? AND end_time IS NULL",
                  (datetime.now().isoformat(), int(time.time()), task_id))
        conn.commit()
        return jsonify({'status': 'stopped'})

# 停止所有計時
@app.route('/stop_all', methods=['POST'])
def stop_all():
    with sqlite3.connect('work_logs.db') as conn:
        c = conn.cursor()
        c.execute("UPDATE work_logs SET end_time = ?, duration = ? WHERE end_time IS NULL",
                  (datetime.now().isoformat(), int(time.time())))
        conn.commit()
        return jsonify({'status': 'all stopped'})

# 取得統計數據
@app.route('/stats/<period>', methods=['GET'])
def get_stats(period):
    with sqlite3.connect('work_logs.db') as conn:
        c = conn.cursor()
        if period == 'day':
            c.execute("SELECT task_name, SUM(duration) as total FROM work_logs WHERE date(start_time) = date('now') GROUP BY task_name")
        elif period == 'week':
            c.execute("SELECT task_name, SUM(duration) as total FROM work_logs WHERE strftime('%W', start_time) = strftime('%W', 'now') GROUP BY task_name")
        elif period == 'month':
            c.execute("SELECT task_name, SUM(duration) as total FROM work_logs WHERE strftime('%m', start_time) = strftime('%m', 'now') GROUP BY task_name")
        else:
            return jsonify({'error': 'Invalid period'}), 400
        data = c.fetchall()
        return jsonify([{'task_name': row[0], 'duration': row[1] / 3600} for row in data])  # 轉換為小時

if __name__ == '__main__':
    app.run(debug=True)