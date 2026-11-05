import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. 建立分帳比例設定表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS split_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_code TEXT UNIQUE,
            member_name TEXT,
            normal_ratio REAL,  -- 無人局 / 代肝 比例 (例如 0.60)
            special_ratio REAL  -- A大模式 比例 (例如 0.70)
        )
    ''')
    
    # 預設寫入初始分帳比例 (En: 60%/70%, 小樂: 30%/30%, 股東: 10%/0%)
    cursor.execute('''
        INSERT OR IGNORE INTO split_configs (role_code, member_name, normal_ratio, special_ratio)
        VALUES 
        ('A', 'En', 0.60, 0.70),
        ('B', '小樂', 0.30, 0.30),
        ('C', '股東', 0.10, 0.00)
    ''')

    # 2. 建立訂單與交易記錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            customer TEXT,
            taker TEXT,
            project_type TEXT, 
            total_income REAL DEFAULT 0,
            cost REAL DEFAULT 0,
            net_profit REAL DEFAULT 0,
            share_a REAL DEFAULT 0, 
            share_b REAL DEFAULT 0, 
            share_c REAL DEFAULT 0  
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 資料庫初始化完成！")

if __name__ == '__main__':
    init_db()
