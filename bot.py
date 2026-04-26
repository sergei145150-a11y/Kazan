import vk_api
import json
import os
import random
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# =========================
# НАСТРОЙКИ
# =========================
TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"
GROUP_ID = 238116016
ADMIN_ID = 547053039

DATA_FILE = "mods.json"

# =========================
# ПОДКЛЮЧЕНИЕ
# =========================
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
# ВСПОМОГАТЕЛЬНОЕ
# =========================
def send(user_id, text):
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 999999999)
    )

def create_mod(uid):
    uid = str(uid)
    if uid not in mods:
        mods[uid] = {
            "nick": f"id{uid}",
            "age": "18",
            "timezone": "МСК",
            "role": "Модератор",
            "post": "Не указана",
            "set_date": datetime.now().strftime("%d.%m.%Y"),
            "raise_date": datetime.now().strftime("%d.%m.%Y"),
            "balls": 0,
            "warns": 0,
            "preds": 0,
            "mutes": 0,
            "inactive": 0,
            "discord": "Не указан",
            "forum": "Не указан",
            "telegram": "Не указан"
        }
        save_data(mods)

def profile(uid):
    uid = str(uid)
    if uid not in mods:
        return "❌ Модератор не найден"

    m = mods[uid]

    text = f"""🎲 Статистика администратора

🟩 Игровой Ник/VK: {m['nick']}
🟩 Возраст: {m['age']}
🟩 Час пояс: {m['timezone']}
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
    return text


# =========================
# КОМАНДЫ
# =========================
print("Бот запущен.")

for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.object["message"]["text"]
        user_id = event.object["message"]["from_id"]

        args = msg.split()
        cmd = args[0].lower()

        # старт
        if cmd == "/start":
            send(user_id, "✅ Бот работает.\nКоманды:\n/addmod ID\n/profile ID")

        # добавить модератора
        elif cmd == "/addmod":
            if user_id != ADMIN_ID:
                send(user_id, "❌ Нет доступа")
                continue

            if len(args) < 2:
                send(user_id, "Используй: /addmod ID")
                continue

            uid = args[1]
            create_mod(uid)
            send(user_id, f"✅ Модератор {uid} добавлен")

        # профиль
        elif cmd == "/profile":
            if len(args) < 2:
                uid = user_id
            else:
                uid = args[1]

            send(user_id, profile(uid))

        # изменить поле
        elif cmd == "/set":
            if user_id != ADMIN_ID:
                send(user_id, "❌ Нет доступа")
                continue

            if len(args) < 4:
                send(user_id, "/set ID поле значение")
                continue

            uid = args[1]
            field = args[2]
            value = " ".join(args[3:])

            if uid not in mods:
                send(user_id, "❌ Нет такого модератора")
                continue

            if field in mods[uid]:
                mods[uid][field] = value
                save_data(mods)
                send(user_id, "✅ Обновлено")
            else:
                send(user_id, "❌ Нет такого поля")
