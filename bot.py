import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import os
import random
from datetime import datetime

# ==========================
# НАСТРОЙКИ
# ==========================
TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"
GROUP_ID = 238116016
ADMIN_ID = 547053039
DATA_FILE = "mods.json"

# ==========================
# ПОДКЛЮЧЕНИЕ
# ==========================
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# ==========================
# БАЗА
# ==========================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

mods = load_data()

# ==========================
# ФУНКЦИИ
# ==========================
def send(uid, text):
    vk.messages.send(
        user_id=uid,
        message=text,
        random_id=random.randint(1, 999999999)
    )

def is_admin(uid):
    return uid == ADMIN_ID

def create_mod(uid):
    uid = str(uid)

    if uid not in mods:
        mods[uid] = {
            "nick": "Не указан",
            "age": "-",
            "timezone": "-",
            "role": "Модератор",
            "post": "-",
            "set_date": datetime.now().strftime("%d.%m.%Y"),
            "raise_date": datetime.now().strftime("%d.%m.%Y"),
            "balls": 0,
            "warns": 0,
            "preds": 0,
            "mutes": 0,
            "inactive": 0,
            "discord": "-",
            "forum": "-",
            "telegram": "-"
        }
        save_data(mods)

def profile(uid):
    uid = str(uid)

    if uid not in mods:
        return "❌ Модератор не найден."

    m = mods[uid]

    return f"""🎲 Статистика администратора

🟩 Игровой Ник/VK: [id{uid}|{m['nick']}]
🟩 Возраст: {m['age']}
🟩 Часовой пояс: {m['timezone']}
🟩 Уровень прав: {m['role']}
🟩 Должность: {m['post']}

✳️ Поставлен: {m['set_date']}
✳️ Последнее повышение: {m['raise_date']}

🟪 Количество баллов: {m['balls']}
🟪 Количество выговоров: {m['warns']}
🟪 Количество предов: {m['preds']}
🟪 Количество мутов: {m['mutes']}

🔲 Неактивов: {m['inactive']} дней

🟧 Discord: {m['discord']}
🟧 Форум: {m['forum']}
🟧 Telegram: {m['telegram']}
"""

print("Бот запущен.")

# ==========================
# LONGPOLL
# ==========================
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:

        msg = event.object.message["text"].strip()
        user_id = event.object.message["from_id"]

        if not msg.startswith("/"):
            continue

        args = msg.split()
        cmd = args[0].lower()

        # ==========================
        # ОБЩИЕ
        # ==========================
        if cmd == "/start":
            send(user_id, "✅ Бот работает.")

        elif cmd == "/help":
            send(user_id, """📌 Команды:

/id
/profile [ID]

Админ:
/addmod ссылка ник
/delmod ID
/mods
/set ID поле значение
""")

        elif cmd == "/id":
            send(user_id, f"Ваш ID: {user_id}")

        elif cmd == "/profile":
            uid = str(user_id)

            if len(args) >= 2:
                uid = args[1]

            send(user_id, profile(uid))

        # ==========================
        # АДМИНКА
        # ==========================
        elif cmd == "/addmod":
            if not is_admin(user_id):
                send(user_id, "❌ Нет доступа.")
                continue

            args = msg.split(maxsplit=2)

            if len(args) < 3:
                send(user_id, "Использование:\n/addmod ссылка ник")
                continue

            raw = args[1]
            nick = args[2]

            uid = raw.replace("https://vk.com/id", "")
            uid = uid.replace("vk.com/id", "")
            uid = uid.replace("id", "")

            if not uid.isdigit():
                send(user_id, "❌ Неверная ссылка.")
                continue

            create_mod(uid)
            mods[uid]["nick"] = nick
            save_data(mods)

            send(user_id, f"✅ Модератор {nick} добавлен.")

        elif cmd == "/delmod":
            if not is_admin(user_id):
                send(user_id, "❌ Нет доступа.")
                continue

            if len(args) < 2:
                send(user_id, "/delmod ID")
                continue

            uid = args[1]

            if uid in mods:
                del mods[uid]
                save_data(mods)
                send(user_id, "✅ Удалён.")
            else:
                send(user_id, "❌ Не найден.")

        elif cmd == "/mods":
            if not is_admin(user_id):
                send(user_id, "❌ Нет доступа.")
                continue

            if not mods:
                send(user_id, "Список пуст.")
                continue

            text = "📋 Модераторы:\n\n"

            for uid in mods:
                text += f"{uid} — {mods[uid]['nick']}\n"

            send(user_id, text)

        elif cmd == "/set":
            if not is_admin(user_id):
                send(user_id, "❌ Нет доступа.")
                continue

            if len(args) < 4:
                send(user_id, "/set ID поле значение")
                continue

            uid = args[1]
            field = args[2]
            value = " ".join(args[3:])

            if uid not in mods:
                send(user_id, "❌ Модератор не найден.")
                continue

            if field not in mods[uid]:
                send(user_id, "❌ Нет такого поля.")
                continue

            mods[uid][field] = value
            save_data(mods)

            send(user_id, "✅ Обновлено.")
