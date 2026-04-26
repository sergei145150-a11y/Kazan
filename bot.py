from flask import Flask, request
import vk_api
import random
import json
import os
from datetime import datetime

# =========================
# НАСТРОЙКИ
# =========================
TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"
ADMIN_ID = 547053039
CONFIRMATION_TOKEN = "12345"   # потом вставишь из VK Callback API
DATA_FILE = "mods.json"

# =========================
# VK API
# =========================
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

app = Flask(__name__)

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
# ОТПРАВКА
# =========================
def send(user_id, text):
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 999999999)
    )

# =========================
# СОЗДАНИЕ МОДЕРА
# =========================
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
        save_data(mods)

# =========================
# КАРТОЧКА
# =========================
def get_card(uid):
    uid = str(uid)
    if uid not in mods:
        return "❌ Пользователь не найден"

    m = mods[uid]

    text = f"""🎲 Статистика администратора

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
    return text

# =========================
# CALLBACK
# =========================
@app.route("/", methods=["POST"])
def callback():
    data = request.json

    if data["type"] == "confirmation":
        return CONFIRMATION_TOKEN

    if data["type"] == "message_new":
        msg = data["object"]["message"]
        uid = msg["from_id"]
        text = msg["text"].strip()

        # /стата
        if text.lower() == "/стата":
            create_mod(uid)
            send(uid, get_card(uid))

        # Только владелец
        if uid == ADMIN_ID:

            # добавить модератора
            if text.startswith("/addmod"):
                try:
                    target = text.split()[1]
                    create_mod(target)
                    send(uid, f"✅ Модератор {target} добавлен")
                except:
                    send(uid, "Используй: /addmod ID")

            # изменить ник
            elif text.startswith("/setnick"):
                try:
                    arr = text.split(maxsplit=2)
                    target = arr[1]
                    value = arr[2]
                    create_mod(target)
                    mods[str(target)]["nick"] = value
                    save_data(mods)
                    send(uid, "✅ Ник обновлен")
                except:
                    send(uid, "Используй: /setnick ID Ник")

            # возраст
            elif text.startswith("/setage"):
                try:
                    arr = text.split()
                    target = arr[1]
                    value = arr[2]
                    create_mod(target)
                    mods[str(target)]["age"] = value
                    save_data(mods)
                    send(uid, "✅ Возраст обновлен")
                except:
                    send(uid, "Используй: /setage ID 18")

            # пояс
            elif text.startswith("/settz"):
                try:
                    arr = text.split(maxsplit=2)
                    target = arr[1]
                    value = arr[2]
                    create_mod(target)
                    mods[str(target)]["timezone"] = value
                    save_data(mods)
                    send(uid, "✅ Пояс обновлен")
                except:
                    send(uid, "Используй: /settz ID МСК +2")

            # ранг
            elif text.startswith("/setrank"):
                try:
                    arr = text.split(maxsplit=2)
                    target = arr[1]
                    value = arr[2]
                    create_mod(target)
                    mods[str(target)]["rank"] = value
                    save_data(mods)
                    send(uid, "✅ Ранг обновлен")
                except:
                    send(uid, "Используй: /setrank ID Старший")

            # должность
            elif text.startswith("/setpost"):
                try:
                    arr = text.split(maxsplit=2)
                    target = arr[1]
                    value = arr[2]
                    create_mod(target)
                    mods[str(target)]["post"] = value
                    save_data(mods)
                    send(uid, "✅ Должность обновлена")
                except:
                    send(uid, "Используй: /setpost ID Форум")

            # баллы
            elif text.startswith("/setpoints"):
                try:
                    arr = text.split()
                    target = arr[1]
                    value = int(arr[2])
                    create_mod(target)
                    mods[str(target)]["points"] = value
                    save_data(mods)
                    send(uid, "✅ Баллы обновлены")
                except:
                    send(uid, "Используй: /setpoints ID 100")

            # телега
            elif text.startswith("/settg"):
                try:
                    arr = text.split(maxsplit=2)
                    target = arr[1]
                    value = arr[2]
                    create_mod(target)
                    mods[str(target)]["telegram"] = value
                    save_data(mods)
                    send(uid, "✅ Telegram обновлен")
                except:
                    send(uid, "Используй: /settg ID @username")

    return "ok"

# =========================
# ЗАПУСК
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
