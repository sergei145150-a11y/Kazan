# bot.py
# V3 SQLite FULL VERSION
# Старый профиль + поиск по id / ссылке / username / RP nick

import vk_api
import sqlite3
import random

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# ==========================
# CONFIG
# ==========================

TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"
GROUP_ID = 238116016
ADMIN_ID = 547053039

# ==========================
# DATABASE
# ==========================

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

# ==========================
# VK INIT
# ==========================

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# ==========================
# MEMORY
# ==========================

states = {}

# ==========================
# FUNCTIONS
# ==========================

def send(peer_id, text, keyboard=None):
    vk.messages.send(
        peer_id=peer_id,
        message=text,
        random_id=random.randint(1, 999999999),
        keyboard=keyboard
    )

def is_admin(uid):
    return uid == ADMIN_ID

# --------------------------

def add_mod(uid, nick):
    sql.execute("""
    INSERT OR REPLACE INTO moderators
    (uid,nick,rank,coins,warns,vigovors,
    name,age,birthday,timezone,pc,
    discord,forum,telegram)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        nick,
        "Стажёр",
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

    allow = [
        "nick","rank","coins","warns","vigovors",
        "name","age","birthday","timezone","pc",
        "discord","forum","telegram"
    ]

    if field not in allow:
        return False

    sql.execute(f"UPDATE moderators SET {field}=? WHERE uid=?", (value, uid))
    db.commit()
    return True

# --------------------------
# ПОИСК ПОЛЬЗОВАТЕЛЯ
# --------------------------

def find_user(arg):

    arg = arg.strip().lower()

    if arg.isdigit():
        return int(arg)

    arg = arg.replace("https://", "")
    arg = arg.replace("http://", "")
    arg = arg.replace("vk.com/", "")
    arg = arg.replace("/", "")

    if arg.startswith("id") and arg[2:].isdigit():
        return int(arg[2:])

    try:
        data = vk.users.get(user_ids=arg)

        if data:
            return data[0]["id"]
    except:
        pass

    sql.execute("SELECT uid FROM moderators WHERE lower(nick)=?", (arg,))
    row = sql.fetchone()

    if row:
        return row[0]

    return None

# --------------------------
# KEYBOARDS
# --------------------------

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

# --------------------------
# PROFILE (старый стиль)
# --------------------------

def profile(uid):

    m = get_mod(uid)

    if not m:
        return "❌ Вы не являетесь модератором."

    return f"""
▪ RP-Nickname: {m[1]}
▪ Должность: {m[2]}
▪ Coins: {m[3]}

📋 Личная информация

▪ Имя: {m[6]}
▪ Возраст: {m[7]}
▪ Дата рождения: {m[8]}
▪ Часовой пояс: {m[9]}
▪ ПК (Да/Нет): {m[10]}

🪪 Статистика модератора

⛔ Предупреждения: {m[4]}
⛔ Выговоры: {m[5]}

▪ Поставлен: Не указано
▪ Последнее повышение: Не указано
▪ Дней на посту: 0
▪ Дней на должности: 0

✅ Дней выполненной нормы: 0
❌ Количество неактивов: 0

⚠ Discord: {m[11]}
⚠ Forum: {m[12]}
⚠ Telegram: {m[13]}
"""

# ==========================
# START
# ==========================

print("V3 SQLite запущен")

# ==========================
# LOOP
# ==========================

for event in longpoll.listen():

    if event.type != VkBotEventType.MESSAGE_NEW:
        continue

    msg = event.object.message["text"].strip()
    uid = event.object.message["from_id"]
    peer_id = event.object.message["peer_id"]

    if peer_id != uid:

        # убираем упоминание [club123|Test]
        if "]" in msg and msg.startswith("["):
            msg = msg.split("]", 1)[1].strip()

        # если написали Test ...
        elif msg.lower().startswith("test "):
            msg = msg[5:].strip()

        # если не команда — игнор
        elif not msg.startswith("/"):
            continue

    low = msg.lower()

        # ======================
        # STATES
        # ======================

    if uid in states:

        step = states[uid]["step"]

        if step == "raise":

            send(
                    ADMIN_ID,
                    f"📩 Заявка на повышение\n\nОт: {uid}\nПричина: {msg}"
                )

                send(peer_id, "✅ Заявка отправлена.")
                del states[uid]
                continue

            elif step == "set_uid":

                target = find_user(msg)

                if not target:
                    send(peer_id, "❌ Пользователь не найден.")
                    continue

                states[uid]["target"] = target
                states[uid]["step"] = "set_field"

                send(peer_id, "Введите поле:")
                continue

            elif step == "set_field":

                states[uid]["field"] = msg
                states[uid]["step"] = "set_value"

                send(peer_id, "Введите значение:")
                continue

            elif step == "set_value":

                target = states[uid]["target"]
                field = states[uid]["field"]

                ok = update_field(target, field, msg)

                if ok:
                    send(peer_id, "✅ Данные изменены.")
                else:
                    send(peer_id, "❌ Поле не найдено.")

                del states[uid]
                continue

        # ======================
        # BUTTONS
        # ======================

    if low == "📋 профиль":
            send(peer_id, profile(uid), menu())
            continue

        elif low == "📈 повышение":
            states[uid] = {"step":"raise"}
            send(peer_id, "✍ Напишите причину заявки:")
            continue

        elif low == "📷 доказательства":
            send(peer_id, "📷 Отправьте доказательства администрации.", menu())
            continue

        elif low == "👑 админка":

            if not is_admin(uid):
                continue

            send(peer_id,
"""👑 Админ-команды

/addmod ссылка ник
/delmod ссылка
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

            send(peer_id, text, admin_kb())
            continue

        elif low == "✏ изменить данные":

            if not is_admin(uid):
                continue

            states[uid] = {"step":"set_uid"}

            send(peer_id, "Введите ссылку / ID / ник:", admin_kb())
            continue

        # ======================
        # COMMANDS
        # ======================

        if not msg.startswith("/"):
            continue

        args = msg.split()
        cmd = args[0].lower()

        if cmd == "/start":
            send(peer_id, "✅ Панель активирована.", menu())

        elif cmd == "/addmod":

            if not is_admin(uid):
                continue

            if len(args) < 3:
                send(peer_id, "/addmod ссылка ник")
                continue

            target = find_user(args[1])

            if not target:
                send(peer_id, "❌ Пользователь не найден.")
                continue

            nick = " ".join(args[2:])

            add_mod(target, nick)

            send(peer_id, "✅ Модератор добавлен.")

        elif cmd == "/delmod":

            if not is_admin(uid):
                continue

            if len(args) < 2:
                continue

            target = find_user(args[1])

            if not target:
                send(peer_id, "❌ Пользователь не найден.")
                continue

            del_mod(target)

            send(peer_id, "✅ Модератор удалён.")

        elif cmd == "/mods":

            rows = get_all_mods()

            text = "📄 Состав:\n\n"

            for x in rows:
                text += f"[id{x[0]}|{x[1]}] — {x[2]}\n"

            send(peer_id, text)

        elif cmd == "/set":

            if not is_admin(uid):
                continue

            states[uid] = {"step":"set_uid"}

            send(peer_id, "Введите ссылку / ID / ник:")
