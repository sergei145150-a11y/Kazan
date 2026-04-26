import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import os
import random
from datetime import datetime

# =======================
# НАСТРОЙКИ
# =======================
TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"
GROUP_ID = 238116016   # ВСТАВЬ ID ГРУППЫ
ADMIN_ID = 547053039

DATA_FILE = "mods.json"

# =======================
# VK INIT
# =======================
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# =======================
# DATA
# =======================
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

mods = load()

# =======================
# SEND
# =======================
def send(uid, text):
    vk.messages.send(
        user_id=uid,
        message=text,
        random_id=random.randint(1, 999999999)
    )

# =======================
# CREATE MOD
# =======================
def create_mod(uid):
    uid = str(uid)

    if uid not in mods:
        mods[uid] = {
            "nick": f"id{uid}",
            "age": "18",
            "timezone": "МСК +0",
            "rank": "Модератор",
            "post": "Не указана",
            "date": datetime.now().strftime("%d.%m.%Y"),
            "points": 0,
            "warns": 0,
            "preds": 0,
            "telegram": "Не указан"
        }
        save(mods)

# =======================
# CARD
# =======================
def card(uid):
    uid = str(uid)

    if uid not in mods:
        return "❌ Пользователь не найден"

    m = mods[uid]

    return f"""🎲 Статистика администратора

🟩 Игровой Ник/VK: {m['nick']}
🟩 Возраст: {m['age']}
🟩 Часовой пояс: {m['timezone']}
🟩 Уровень прав: {m['rank']}
🟩 Должность: {m['post']}

✳ Поставлен: {m['date']}

🟪 Количество баллов: {m['points']}
🟪 Количество выговоров: {m['warns']}
🟪 Количество предов: {m['preds']}

🟧 Telegram: {m['telegram']}
🟧 VK ID: {uid}
"""

# =======================
# START
# =======================
print("Бот запущен")

for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:

        msg = event.object["message"]
        uid = msg["from_id"]
        text = msg["text"].strip()

        # обычный пользователь
        if text.lower() == "/стата":
            create_mod(uid)
            send(uid, card(uid))

        # админ команды
        if uid == ADMIN_ID:

            if text.startswith("/addmod"):
                try:
                    target = text.split()[1]
                    create_mod(target)
                    send(uid, "✅ Модератор добавлен")
                except:
                    send(uid, "Используй: /addmod ID")

            elif text.startswith("/setnick"):
                try:
                    arr = text.split(maxsplit=2)
                    target = arr[1]
                    val = arr[2]
                    create_mod(target)
                    mods[str(target)]["nick"] = val
                    save(mods)
                    send(uid, "✅ Ник изменен")
                except:
                    send(uid, "Используй: /setnick ID Ник")

            elif text.startswith("/setpoints"):
                try:
                    arr = text.split()
                    target = arr[1]
                    val = int(arr[2])
                    create_mod(target)
                    mods[str(target)]["points"] = val
                    save(mods)
                    send(uid, "✅ Баллы изменены")
                except:
                    send(uid, "Используй: /setpoints ID 100")

            elif text.startswith("/setrank"):
                try:
                    arr = text.split(maxsplit=2)
                    target = arr[1]
                    val = arr[2]
                    create_mod(target)
                    mods[str(target)]["rank"] = val
                    save(mods)
                    send(uid, "✅ Ранг изменен")
                except:
                    send(uid, "Используй: /setrank ID Старший")

            elif text.startswith("/setage"):
                try:
                    arr = text.split()
                    target = arr[1]
                    val = arr[2]
                    create_mod(target)
                    mods[str(target)]["age"] = val
                    save(mods)
                    send(uid, "✅ Возраст изменен")
                except:
                    send(uid, "Используй: /setage ID 18")
