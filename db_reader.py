import sqlite3
import pandas as pd

conn = sqlite3.connect('telegram_online.db')

# Вариант с библиотекой pandas (красивая табличка в консоли)
try:
    df = pd.read_sql_query("SELECT * FROM online_logs ORDER BY id DESC LIMIT 30", conn)
    print(df.to_string(index=False))
except Exception:
    # Если pandas не установлен, используем стандартный sqlite3
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM online_logs ORDER BY id DESC LIMIT 30")
    rows = cursor.fetchall()

    print(f"{'ID':<5} | {'User ID':<15} | {'Status':<10} | {'Timestamp':<20}")
    print("-" * 60)
    for row in rows:
        print(f"{row[0]:<5} | {row[1]:<15} | {row[2]:<10} | {row[3]:<20}")

conn.close()