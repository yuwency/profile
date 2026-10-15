from flask import Flask, render_template, request, jsonify
import sqlite3
from database import get_db_connection, init_db
from datetime import datetime

app = Flask(__name__)

# 初始化資料庫
init_db()

@app.route('/')
def index():
    return render_template('index.html')

# 取得所有紀錄與當月統計
@app.route('/api/records', methods=['GET'])
def get_records():
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    conn = get_db_connection()
    
    # 取得指定月份紀錄
    records = conn.execute(
        "SELECT * FROM records WHERE strftime('%Y-%m', date) = ? ORDER BY date DESC, id DESC", 
        (month,)
    ).fetchall()
    
    # 計算當月總收入與總支出
    summary = conn.execute('''
        SELECT 
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
        FROM records 
        WHERE strftime('%Y-%m', date) = ?
    ''', (month,)).fetchone()
    
    # 取得當月預算
    budget_row = conn.execute("SELECT budget_amount FROM budgets WHERE month = ?", (month,)).fetchone()
    budget_amount = budget_row['budget_amount'] if budget_row else 0.0

    # 分類支出統計（畫圖表用）
    category_summary = conn.execute('''
        SELECT category, SUM(amount) as total 
        FROM records 
        WHERE type = 'expense' AND strftime('%Y-%m', date) = ? 
        GROUP BY category
    ''', (month,)).fetchall()

    conn.close()

    total_income = summary['total_income'] or 0.0
    total_expense = summary['total_expense'] or 0.0

    return jsonify({
        'records': [dict(r) for r in records],
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense,
        'budget': budget_amount,
        'category_summary': [dict(c) for c in category_summary]
    })

# 新增紀錄
@app.route('/api/records', methods=['POST'])
def add_record():
    data = request.json
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO records (type, category, amount, date, note) VALUES (?, ?, ?, ?, ?)",
        (data['type'], data['category'], float(data['amount']), data['date'], data.get('note', ''))
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# 刪除紀錄
@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# 設定/更新每月預算
@app.route('/api/budget', methods=['POST'])
def set_budget():
    data = request.json
    month = data['month']
    amount = float(data['amount'])
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO budgets (month, budget_amount) VALUES (?, ?)
        ON CONFLICT(month) DO UPDATE SET budget_amount = excluded.budget_amount
    ''', (month, amount))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)