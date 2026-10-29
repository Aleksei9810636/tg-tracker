import asyncio
import sqlite3
from datetime import datetime
from telethon import TelegramClient, events

API_ID = 111
API_HASH = '222'

TARGET_USERS = [] 

def init_db():
    conn = sqlite3.connect('telegram_online.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS online_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            status TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()

def log_status(user_id: int, display_name: str, status: str):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('telegram_online.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO online_logs (user_id, status, timestamp) VALUES (?, ?, ?)',
        (user_id, status, now_str)
    )
    conn.commit()
    conn.close()
    
    print(f"[{now_str}] {display_name} (ID: {user_id}) -> {status}")

client = TelegramClient('my_session', API_ID, API_HASH)

@client.on(events.UserUpdate)
async def user_update_handler(event):
    if TARGET_USERS and event.user_id not in TARGET_USERS:
        return

    # Получаем сущность из кэша или сервера
    try:
        user = await client.get_entity(event.user_id)
        name_parts = [p for p in [user.first_name, user.last_name] if p]
        full_name = " ".join(name_parts)
        username = f"@{user.username}" if user.username else ""
        
        if full_name and username:
            display_name = f"{full_name} ({username})"
        elif full_name:
            display_name = full_name
        elif username:
            display_name = username
        else:
            display_name = f"User_{event.user_id}"
    except Exception:
        display_name = f"User_{event.user_id}"

    if event.online is True:
        log_status(event.user_id, display_name, 'ONLINE')
    elif event.online is False:
        log_status(event.user_id, display_name, 'OFFLINE')

async def main():
    init_db()
    await client.start()
    
    print("Загружаем контакты и диалоги в кэш...")
    # Подгружает список чатов, чтобы Telethon знал имена и usernames всех контактов
    await client.get_dialogs()
    
    print("Кэш прогрет. Запуск прослушивания событий...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nОтслеживание остановлено.")
