# V2 STAFF PANEL BOT
# ГОТОВЫЙ bot.py

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import os
import random
from datetime import datetime

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
states = {}

# =========================
# ФУНКЦИИ
# =========================
def is_admin(uid):
    return uid == ADMIN_ID

def send(uid, text, keyboard=None):
    vk.messages.send(
        user_id=uid,
        message=text,
        random_id=random.randint(1, 999999999),
        keyboard=keyboard
    )

def create_mod(uid, nick="Не указан"):
    uid = str(uid)
    if uid not in mods:
        mods[uid] = {
            "nick": nick,
            "role": "Модератор",
            "balls": 0,
            "warns": 0,
            "preds": 0,
            "mutes": 0,
            "inactive": 0,
            "set_date": datetime.now().strftime("%d.%m.%Y")
        }
        save_data(mods)

# =========================
# КНОПКИ
# =========================
def menu(uid):
    kb = VkKeyboard(one_time=False)

    kb.add_button("📋 Профиль", VkKeyboardColor.PRIMARY)
    kb.add_button("📊 Статистика", VkKeyboardColor.SECONDARY)
    kb.add_line()

    kb.add_button("📈 Повышение", VkKeyboardColor.POSITIVE)
    kb.add_button("📷 Доказательства", VkKeyboardColor.PRIMARY)
    kb.add_line()

    kb.add_button("📝 Отчёт", VkKeyboardColor.SECONDARY)
    kb.add_button("🏆 Карьера", VkKeyboardColor.POSITIVE)

    if is_admin(uid):
        kb.add_line()
        kb.add_button("👑 Админка", VkKeyboardColor.NEGATIVE)

    return kb.get_keyboard()

# =========================
# ПРОФИЛЬ
# =========================
def profile(uid):
    uid = str(uid)

    if uid not in mods:
        return "❌ Вас нет в составе."

    m = mods[uid]

    return f"""🎲 Профиль сотрудника

🟩 Ник: [id{uid}|{m['nick']}]
🟩 Должность: {m['role']}
🟪 Баллы: {m['balls']}
🟪 Выговоры: {m['warns']}
🟪 Преды: {m['preds']}
🟪 Муты: {m['mutes']}
🔲 Неактив: {m['inactive']} дней

📅 Назначен: {m['set_date']}
"""

# =========================
# СТАРТ
# =========================
print("V2 Бот запущен")

# =========================
# LONGPOLL
# =========================
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:

        msg = event.object.message["text"].strip()
        uid = event.object.message["from_id"]
        lower = msg.lower()

        # =====================
        # STATE MODE
        # =====================
        if uid in states:

            if states[uid] == "raise":
                send(
                    ADMIN_ID,
                    f"📩 Заявка на повышение\n\n👤 [id{uid}|Пользователь]\n📝 {msg}"
                )
                send(uid, "✅ Заявка отправлена.", menu(uid))
                del states[uid]
                continue

            elif states[uid] == "report":
                send(
                    ADMIN_ID,
                    f"📝 Новый отчёт\n\n👤 [id{uid}|Пользователь]\n📄 {msg}"
                )
                send(uid, "✅ Отчёт отправлен.", menu(uid))
                del states[uid]
                continue

        # =====================
        # КНОПКИ
        # =====================
        if lower == "📋 профиль":
            send(uid, profile(uid), menu(uid))
            continue

        elif lower == "📊 статистика":
            send(uid, profile(uid), menu(uid))
            continue

        elif lower == "📈 повышение":
            states[uid] = "raise"
            send(uid, "✍ Напишите заявку на повышение:", menu(uid))
            continue

        elif lower == "📷 доказательства":
            send(uid, "📷 Отправьте фото одним сообщением с подписью.", menu(uid))
            continue

        elif lower == "📝 отчёт":
            states[uid] = "report"
            send(uid, "✍ Напишите отчёт за день:", menu(uid))
            continue

        elif lower == "🏆 карьера":
            send(uid,
"""🏆 Карьерная лестница:

1. Стажёр
2. Модератор
3. Старший модератор
4. Куратор
5. Заместитель
6. Руководитель""",
            menu(uid))
            continue

        elif lower == "👑 админка":
            if is_admin(uid):
                send(uid,
"""👑 Админ команды:

/addmod ссылка ник
/delmod id
/mods
/set id поле значение
""",
                menu(uid))
            else:
                send(uid, "❌ Нет доступа.", menu(uid))
            continue

        # =====================
        # КОМАНДЫ
        # =====================
        if not msg.startswith("/"):
            continue

        args = msg.split()
        cmd = args[0].lower()

        if cmd == "/start":
            send(uid, "✅ STAFF PANEL V2 активирован.", menu(uid))

        elif cmd == "/addmod":
            if not is_admin(uid):
                continue

            parts = msg.split(maxsplit=2)

            if len(parts) < 3:
                send(uid, "/addmod ссылка ник")
                continue

            raw = parts[1]
            nick = parts[2]

            new_uid = raw.replace("https://vk.com/id", "")
            new_uid = new_uid.replace("vk.com/id", "")
            new_uid = new_uid.replace("id", "")

            if not new_uid.isdigit():
                send(uid, "❌ Ошибка ссылки.")
                continue

            create_mod(new_uid, nick)
            send(uid, f"✅ {nick} добавлен.", menu(uid))

        elif cmd == "/mods":
            if not is_admin(uid):
                continue

            text = "👥 Состав:\n\n"

            for x in mods:
                text += f"[id{x}|{mods[x]['nick']}]\n"

            send(uid, text, menu(uid))

        elif cmd == "/delmod":
            if not is_admin(uid):
                continue

            if len(args) < 2:
                continue

            x = args[1]

            if x in mods:
                del mods[x]
                save_data(mods)
                send(uid, "✅ Удалён.", menu(uid))

        elif cmd == "/set":
            if not is_admin(uid):
                continue

            if len(args) < 4:
                continue

            x = args[1]
            field = args[2]
            value = " ".join(args[3:])

            if x in mods and field in mods[x]:
                mods[x][field] = value
                save_data(mods)
                send(uid, "✅ Изменено.", menu(uid))
