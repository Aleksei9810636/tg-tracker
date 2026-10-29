import asyncio
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from telethon import TelegramClient

API_ID = 34439680
API_HASH = '1a9b9c5016e5c7fc2fb2b38b747e6486'
DB_NAME = 'telegram_online.db'

# -------------------------------------------------------------
# Задавай юзернеймы прямо здесь в массиве (можно с '@' или без)
# -------------------------------------------------------------
TARGET_USERNAMES = ['@V_Aleksei', 'katvas', '@cherrylllll']

def get_user_intervals(user_id: int):
    """Считывает события из БД по user_id."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT status, timestamp 
        FROM online_logs 
        WHERE user_id = ? 
        ORDER BY timestamp ASC
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()

    intervals = []
    last_online = None

    for status, ts_str in rows:
        ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
        if status == 'ONLINE':
            last_online = ts
        elif status == 'OFFLINE' and last_online is not None:
            intervals.append((last_online, ts))
            last_online = None

    if last_online is not None:
        intervals.append((last_online, datetime.now()))

    return intervals

async def main():
    if not TARGET_USERNAMES:
        print("Массив TARGET_USERNAMES пуст. Заполните его юзернеймами.")
        return

    # Подключаемся к Telethon, чтобы узнать user_id по юзернеймам
    client = TelegramClient('my_session', API_ID, API_HASH)
    await client.start()

    resolved_targets = []  # Список пар (user_id, display_label)

    print("Получаем ID пользователей из Telegram...")
    for uname in TARGET_USERNAMES:
        clean_uname = uname.strip().lstrip('@')
        try:
            user = await client.get_entity(clean_uname)
            label = f"@{user.username}" if user.username else clean_uname
            resolved_targets.append((user.id, label))
            print(f"Найден @{clean_uname} -> ID: {user.id}")
        except Exception as e:
            print(f"Не удалось найти пользователя @{clean_uname}: {e}")

    await client.disconnect()

    if not resolved_targets:
        print("Ни один пользователь не был найден.")
        return

    # Построение графика
    fig, ax = plt.subplots(figsize=(12, 2 + len(resolved_targets) * 1.5))

    y_ticks = []
    y_labels = []

    for idx, (user_id, label) in enumerate(resolved_targets):
        intervals = get_user_intervals(user_id)
        
        bars = []
        for start, end in intervals:
            start_num = mdates.date2num(start)
            end_num = mdates.date2num(end)
            duration = end_num - start_num
            bars.append((start_num, duration))

        y_pos = idx * 10
        y_ticks.append(y_pos)
        y_labels.append(label)

        if bars:
            ax.broken_barh(bars, (y_pos - 3, 6), facecolors='#2b5c8f', edgecolors='none')
        else:
            print(f"Записи для {label} (ID: {user_id}) не найдены в базе.")

    # Оформление графика
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
    fig.autofmt_xdate()

    ax.set_title("График активности пользователей")
    ax.set_xlabel("Время")
    ax.set_ylabel("Пользователи")
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig("activity_graph.png", dpi=300)
    print("График успешно сохранён в activity_graph.png")
    plt.show()

if __name__ == '__main__':
    asyncio.run(main())