
# bot.py
# V3 SQLite VK Moderator Bot

import vk_api
import sqlite3
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# =========================
# CONFIG
# =========================

TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"
GROUP_ID = 238116016
ADMIN_ID = 547053039

# =========================
# DATABASE
# =========================

db = sqlite3.connect("database.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS moderators (
    uid INTEGER PRIMARY KEY,
    nick TEXT,
    rank TEXT,
    coins INTEGER,
    warns INTEGER,
    vigovors INTEGER,
    name TEXT,
    age TEXT,
    birthday TEXT,
    timezone TEXT,
    pc TEXT,
    discord TEXT,
    forum TEXT,
    telegram TEXT
)
""")

db.commit()

# =========================
# VK
# =========================

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# =========================
# MEMORY
# =========================

states = {}

# =========================
# FUNCTIONS
# =========================

def send(uid, text, keyboard=None):
    vk.messages.send(
        user_id=uid,
        random_id=random.randint(1, 999999999),
        message=text,
        keyboard=keyboard
    )

def is_admin(uid):
    return uid == ADMIN_ID

def add_mod(uid, nick):
    sql.execute("""
    INSERT OR REPLACE INTO moderators
    (uid, nick, rank, coins, warns, vigovors,
    name, age, birthday, timezone, pc,
    discord, forum, telegram)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        nick,
        "Модератор",
        0,
        0,
        0,
        "Не указано",
        "Не указано",
        "Не указано",
        "Не указано",
        "Нет",
        "Не указано",
        "Не указано",
        "Не указано"
    ))
    db.commit()

def del_mod(uid):
    sql.execute("DELETE FROM moderators WHERE uid=?", (uid,))
    db.commit()

def get_mod(uid):
    sql.execute("SELECT * FROM moderators WHERE uid=?", (uid,))
    return sql.fetchone()

def get_all_mods():
    sql.execute("SELECT uid,nick,rank FROM moderators")
    return sql.fetchall()

def update_field(uid, field, value):
    allowed = [
        "nick","rank","coins","warns","vigovors",
        "name","age","birthday","timezone","pc",
        "discord","forum","telegram"
    ]

    if field not in allowed:
        return False

    sql.execute(f"UPDATE moderators SET {field}=? WHERE uid=?", (value, uid))
    db.commit()
    return True

def menu():
    kb = VkKeyboard(one_time=False)

    kb.add_button("📋 Профиль", VkKeyboardColor.PRIMARY)
    kb.add_button("📈 Повышение", VkKeyboardColor.POSITIVE)

    kb.add_line()

    kb.add_button("📷 Доказательства", VkKeyboardColor.SECONDARY)
    kb.add_button("👑 Админка", VkKeyboardColor.NEGATIVE)

    return kb.get_keyboard()

def admin_kb():
    kb = VkKeyboard(one_time=False)

    kb.add_button("📄 Список модеров", VkKeyboardColor.PRIMARY)
    kb.add_button("✏ Изменить данные", VkKeyboardColor.POSITIVE)

    return kb.get_keyboard()

def profile(uid):
    m = get_mod(uid)

    if not m:
        return "❌ Вы не являетесь модератором."

    return f"""
📋 Профиль

🆔 ID: {m[0]}
🏷 Ник: {m[1]}
🎖 Ранг: {m[2]}
💰 Монеты: {m[3]}
⚠ Преды: {m[4]}
📛 Выговоры: {m[5]}

👤 Имя: {m[6]}
🎂 Возраст: {m[7]}
📅 ДР: {m[8]}
🌍 Часовой пояс: {m[9]}
💻 ПК: {m[10]}

💬 Discord: {m[11]}
🌐 Forum: {m[12]}
📱 Telegram: {m[13]}
"""

# =========================
# START
# =========================

print("V3 SQLite запущен")

# =========================
# LOOP
# =========================

for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:

        msg = event.object.message["text"].strip()
        uid = event.object.message["from_id"]
        low = msg.lower()

        # =====================
        # STATES
        # =====================

        if uid in states:

            step = states[uid]["step"]

            if step == "set_uid":
                states[uid]["target"] = int(msg)
                states[uid]["step"] = "set_field"
                send(uid, "Введите поле:")
                continue

            elif step == "set_field":
                states[uid]["field"] = msg
                states[uid]["step"] = "set_value"
                send(uid, "Введите значение:")
                continue

            elif step == "set_value":
                target = states[uid]["target"]
                field = states[uid]["field"]

                ok = update_field(target, field, msg)

                if ok:
                    send(uid, "✅ Данные изменены.")
                else:
                    send(uid, "❌ Неверное поле.")

                del states[uid]
                continue

            elif step == "raise":
                send(ADMIN_ID, f"📩 Заявка на повышение\n\nОт: {uid}\nПричина: {msg}")
                send(uid, "✅ Заявка отправлена.")
                del states[uid]
                continue

        # =====================
        # BUTTONS
        # =====================

        if low == "📋 профиль":
            send(uid, profile(uid), menu())
            continue

        elif low == "📈 повышение":
            states[uid] = {"step":"raise"}
            send(uid, "✍ Напишите причину заявки:")
            continue

        elif low == "📷 доказательства":
            send(uid, "📷 Отправьте доказательства администрации.", menu())
            continue

        elif low == "👑 админка":

            if not is_admin(uid):
                continue

            send(uid,
"""👑 Админ-команды

/addmod id nick
/delmod id
/mods
/set
""", admin_kb())
            continue

        elif low == "📄 список модеров":

            if not is_admin(uid):
                continue

            rows = get_all_mods()

            text = "📄 Состав:\n\n"

            for x in rows:
                text += f"[id{x[0]}|{x[1]}] — {x[2]}\n"

            send(uid, text, admin_kb())
            continue

        elif low == "✏ изменить данные":

            if not is_admin(uid):
                continue

            states[uid] = {"step":"set_uid"}
            send(uid, "Введите ID пользователя:", admin_kb())
            continue

        # =====================
        # COMMANDS
        # =====================

        if not msg.startswith("/"):
            continue

        args = msg.split()
        cmd = args[0].lower()

        if cmd == "/start":
            send(uid, "✅ Панель активирована.", menu())

        elif cmd == "/addmod":

            if not is_admin(uid):
                continue

            if len(args) < 3:
                send(uid, "/addmod id nick")
                continue

            target = int(args[1])
            nick = args[2]

            add_mod(target, nick)

            send(uid, "✅ Модератор добавлен.")

        elif cmd == "/delmod":

            if not is_admin(uid):
                continue

            if len(args) < 2:
                continue

            target = int(args[1])

            del_mod(target)

            send(uid, "✅ Модератор удалён.")

        elif cmd == "/mods":

            rows = get_all_mods()

            text = "📄 Состав:\n\n"

            for x in rows:
                text += f"[id{x[0]}|{x[1]}] — {x[2]}\n"

            send(uid, text)

        elif cmd == "/set":

            if not is_admin(uid):
                continue

            states[uid] = {"step":"set_uid"}
            send(uid, "Введите ID пользователя:")
