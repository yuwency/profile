import sqlite3

DB_NAME = 'finance.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 讓查詢結果能像 dict 一樣用鍵名存取
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 建立收支紀錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,         -- 'income' 或 'expense'
            category TEXT NOT NULL,     -- 類別（飲食、薪水等）
            amount REAL NOT NULL,       -- 金額
            date TEXT NOT NULL,         -- 日期 (YYYY-MM-DD)
            note TEXT                   -- 備註
        )
    ''')
    
    # 建立每月預算表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            month TEXT PRIMARY KEY,     -- 月份 (YYYY-MM)
            budget_amount REAL NOT NULL -- 預算金額
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("資料庫初始化完成！")