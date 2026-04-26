import sqlite3
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import TOKEN, OWNER_ID

conn = sqlite3.connect("moderation.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS staff (
    vk_id INTEGER PRIMARY KEY,
    nickname TEXT,
    warnings INTEGER DEFAULT 0,
    reprimands INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vk_id INTEGER,
    text TEXT,
    status TEXT DEFAULT 'Ожидает'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS proofs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vk_id INTEGER,
    text TEXT,
    status TEXT DEFAULT 'Ожидает'
)
""")
conn.commit()

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send(uid, text):
    vk.messages.send(user_id=uid, message=text, random_id=0)

def get_staff(uid):
    cursor.execute("SELECT * FROM staff WHERE vk_id=?", (uid,))
    return cursor.fetchone()

def add_staff(uid):
    if not get_staff(uid):
        cursor.execute("INSERT INTO staff(vk_id,nickname) VALUES(?,?)", (uid, f"Игрок_{uid}"))
        conn.commit()

print("Бот запущен")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        msg = event.text
        low = msg.lower()
        uid = event.user_id
        add_staff(uid)

        if low == "/карточка":
            user = get_staff(uid)
            send(uid, f"📋 Личная карточка:\n👤 RP Nickname: {user[1]}\n⚠ Предупреждения: {user[2]}\n🚫 Выговоры: {user[3]}")

        elif low.startswith("/отчет "):
            cursor.execute("INSERT INTO reports(vk_id,text) VALUES(?,?)", (uid, msg[7:]))
            conn.commit()
            send(uid, "✅ Отчёт отправлен.")

        elif low.startswith("/доказательства "):
            cursor.execute("INSERT INTO proofs(vk_id,text) VALUES(?,?)", (uid, msg[16:]))
            conn.commit()
            send(uid, "✅ Доказательства отправлены.")

        elif uid == OWNER_ID:
            if low == "/отчеты":
                cursor.execute("SELECT * FROM reports")
                rows = cursor.fetchall()
                txt = "📄 Отчёты:\n\n" + "\n\n".join([f"ID {r[0]} | VK {r[1]}\n{r[2]}\nСтатус: {r[3]}" for r in rows]) if rows else "Нет отчётов."
                send(uid, txt)

            elif low == "/доказательства":
                cursor.execute("SELECT * FROM proofs")
                rows = cursor.fetchall()
                txt = "📎 Доказательства:\n\n" + "\n\n".join([f"ID {r[0]} | VK {r[1]}\n{r[2]}\nСтатус: {r[3]}" for r in rows]) if rows else "Нет доказательств."
                send(uid, txt)

            elif low.startswith("/пред "):
                target = int(low.split()[1])
                cursor.execute("UPDATE staff SET warnings = warnings + 1 WHERE vk_id=?", (target,))
                conn.commit()
                send(uid, "⚠ Предупреждение выдано.")
                send(target, "⚠ Вам выдано предупреждение.")

            elif low.startswith("/выговор "):
                target = int(low.split()[1])
                cursor.execute("UPDATE staff SET reprimands = reprimands + 1 WHERE vk_id=?", (target,))
                conn.commit()
                send(uid, "🚫 Выговор выдан.")
                send(target, "🚫 Вам выдан выговор.")
