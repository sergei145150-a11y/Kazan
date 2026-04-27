import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import os
import random
from datetime import datetime

TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"
GROUP_ID = 238116016
ADMIN_ID = 547053039
DATA_FILE = "mods.json"

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)


# =========================
# БАЗА
# =========================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

mods = load_data()


# =========================
# КНОПКИ
# =========================
def get_keyboard(uid):
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button("📋 Профиль", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("🆔 ID", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()

    keyboard.add_button("📚 Помощь", color=VkKeyboardColor.POSITIVE)

    if uid == ADMIN_ID:
        keyboard.add_line()
        keyboard.add_button("👑 Админка", color=VkKeyboardColor.NEGATIVE)

    return keyboard.get_keyboard()


# =========================
# ОТПРАВКА
# =========================
def send(uid, text):
    vk.messages.send(
        user_id=uid,
        message=text,
        random_id=random.randint(1, 999999999),
        keyboard=get_keyboard(uid)
    )


# =========================
# ЛОГИКА
# =========================
def is_admin(uid):
    return uid == ADMIN_ID

def create_mod(uid, nick="Отсутствует"):
    uid = str(uid)

    if uid not in mods:
        mods[uid] = {
            "nick": nick,
            "age": "-",
            "timezone": "-",
            "role": "Модератор",
            "post": "-",
            "set_date": datetime.now().strftime("%d.%m.%Y"),
            "raise_date": "-",
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
        return "❌ Профиль не найден."

    m = mods[uid]

    return f"""🎲 Профиль администратора

🟩 Ник/VK: [id{uid}|{m['nick']}]
🟩 Возраст: {m['age']}
🟩 Часовой пояс: {m['timezone']}
🟩 Уровень прав: {m['role']}
🟩 Должность: {m['post']}

✳️ Поставлен: {m['set_date']}
✳️ Повышен: {m['raise_date']}

🟪 Баллы: {m['balls']}
🟪 Выговоры: {m['warns']}
🟪 Преды: {m['preds']}
🟪 Муты: {m['mutes']}

🔲 Неактив: {m['inactive']} дней

🟧 Discord: {m['discord']}
🟧 Форум: {m['forum']}
🟧 Telegram: {m['telegram']}
"""


print("Бот запущен.")


# =========================
# LONGPOLL
# =========================
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.object.message["text"].strip()
        user_id = event.object.message["from_id"]

        text = msg.lower()

        # КНОПКИ
        if text == "📋 профиль":
            send(user_id, profile(user_id))
            continue

        elif text == "🆔 id":
            send(user_id, f"Ваш ID: {user_id}")
            continue

        elif text == "📚 помощь":
            send(user_id,
"""📌 Команды:

/profile [id]
/id

Админ:
/addmod ссылка ник
/delmod id
/mods
/set id поле значение
""")
            continue

        elif text == "👑 админка":
            if is_admin(user_id):
                send(user_id,
"""👑 Админ панель:

/addmod ссылка ник
/delmod id
/mods
/set id поле значение
""")
            else:
                send(user_id, "❌ Нет доступа.")
            continue

        # СЛЕШ КОМАНДЫ
        if not msg.startswith("/"):
            continue

        args = msg.split()
        cmd = args[0].lower()

        if cmd == "/id":
            send(user_id, f"Ваш ID: {user_id}")

        elif cmd == "/profile":
            uid = user_id
            if len(args) >= 2:
                uid = args[1]
            send(user_id, profile(uid))

        elif cmd == "/addmod":
            if not is_admin(user_id):
                send(user_id, "❌ Нет доступа.")
                continue

            parts = msg.split(maxsplit=2)

            if len(parts) < 3:
                send(user_id, "Использование:\n/addmod ссылка ник")
                continue

            raw = parts[1]
            nick = parts[2]

            uid = raw.replace("https://vk.com/id", "")
            uid = uid.replace("vk.com/id", "")
            uid = uid.replace("id", "")

            if not uid.isdigit():
                send(user_id, "❌ Неверная ссылка.")
                continue

            create_mod(uid, nick)
            send(user_id, f"✅ Модератор {nick} добавлен.")

        elif cmd == "/delmod":
            if not is_admin(user_id):
                send(user_id, "❌ Нет доступа.")
                continue

            if len(args) < 2:
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

            txt = "📋 Модераторы:\n\n"

            for uid in mods:
                txt += f"[id{uid}|{mods[uid]['nick']}]\n"

            send(user_id, txt)

        elif cmd == "/set":
            if not is_admin(user_id):
                send(user_id, "❌ Нет доступа.")
                continue

            if len(args) < 4:
                send(user_id, "/set id поле значение")
                continue

            uid = args[1]
            field = args[2]
            value = " ".join(args[3:])

            if uid not in mods:
                send(user_id, "❌ Не найден.")
                continue

            if field not in mods[uid]:
                send(user_id, "❌ Нет поля.")
                continue

            mods[uid][field] = value
            save_data(mods)

            send(user_id, "✅ Обновлено.")
