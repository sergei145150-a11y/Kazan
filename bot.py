# V2.5 SMART STAFF PANEL
# bot.py

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

# =======================
# DATA
# =======================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(mods, f, ensure_ascii=False, indent=4)

mods = load_data()
states = {}

# =======================
# HELPERS
# =======================
def is_admin(uid):
    return uid == ADMIN_ID

def send(uid, text, keyboard=None):
    vk.messages.send(
        user_id=uid,
        random_id=random.randint(1,999999999),
        message=text,
        keyboard=keyboard
    )
def admin_keyboard():
    kb = VkKeyboard(one_time=False)

    kb.add_button("📋 Список модеров", color=VkKeyboardColor.PRIMARY)
    kb.add_button("✏ Изменить данные", color=VkKeyboardColor.POSITIVE)

    kb.add_line()

    kb.add_button("👤 Профиль", color=VkKeyboardColor.SECONDARY)

    return kb.get_keyboard()

def menu(uid):
    kb = VkKeyboard(one_time=False)

    kb.add_button("📋 Профиль", VkKeyboardColor.PRIMARY)
    kb.add_button("📈 Повышение", VkKeyboardColor.POSITIVE)
    kb.add_line()

    kb.add_button("📷 Доказательства", VkKeyboardColor.PRIMARY)
    kb.add_button("📝 Отчёт", VkKeyboardColor.SECONDARY)
    kb.add_line()

    kb.add_button("🏆 Карьера", VkKeyboardColor.SECONDARY)

    if is_admin(uid):
        kb.add_line()
        kb.add_button("👑 Админка", VkKeyboardColor.NEGATIVE)

    return kb.get_keyboard()

def create_mod(uid, nick="Не указано"):
    uid = str(uid)

    if uid not in mods:
        mods[uid] = {
            "nick": nick,
            "post": "Не указано",
            "coins": "Не указано",

            "name": "Не указано",
            "age": "Не указано",
            "birthday": "Не указано",
            "timezone": "Не указано",
            "pc": "Не указано",

            "preds": 0,
            "warns": 0,

            "set_date": datetime.now().strftime("%d.%m.%Y"),
            "raise_date": "Не указано",
            "days_post": "Не указано",
            "days_rank": "Не указано",

            "norm_days": 0,
            "inactive": 0,

            "discord": "Не указано",
            "forum": "Не указано",
            "telegram": "Не указано",

            "role": "Модератор",
            "balls": 0,
            "mutes": 0
        }

        save_data()

# =======================
# SMART ID
# =======================
def parse_user(raw):
    raw = raw.strip()

    raw = raw.replace("https://vk.com/", "")
    raw = raw.replace("http://vk.com/", "")

    if raw.startswith("id"):
        raw = raw.replace("id", "")

    if raw.isdigit():
        return raw

    try:
        user = vk.users.get(user_ids=raw)[0]
        return str(user["id"])
    except:
        return None

# =======================
# PROFILE
# =======================
def profile(uid):
    uid = str(uid)

    if uid not in mods:
        return "❌ Вас нет в составе."

    m = mods[uid]

    return f"""📊 Личная статистика

◻ RP-Nickname: {m.get('nick', 'Не указано')}
◻ Должность: {m.get('post', 'Не указано')}
◻ Coins: {m.get('coins', 'Не указано')}

📋 Личная информация

◻ Имя: {m.get('name', 'Не указано')}
◻ Возраст: {m.get('age', 'Не указано')}
◻ Дата рождения: {m.get('birthday', 'Не указано')}
◻ Часовой пояс: {m.get('timezone', 'Не указано')}
◻ ПК (Да/Нет): {m.get('pc', 'Не указано')}

🪪 Статистика модератора

⛔ Предупреждения: {m.get('preds', 'Не указано')}
⛔ Выговоры: {m.get('warns', 'Не указано')}

◼ Поставлен: {m.get('set_date', 'Не указано')}
◼ Последнее повышение: {m.get('raise_date', 'Не указано')}
◼ Дней на посту: {m.get('days_post', 'Не указано')}
◼ Дней на должности: {m.get('days_rank', 'Не указано')}

✅ Дней выполненной нормы: {m.get('norm_days', 'Не указано')}
❌ Количество неактивов: {m.get('inactive', 'Не указано')}

⚠ Discord: {m.get('discord', 'Не указано')}
⚠ Forum: {m.get('forum', 'Не указано')}
⚠ Telegram: {m.get('telegram', 'Не указано')}
"""

print("V2.5 запущен")

# =======================
# LOOP
# =======================
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:

        msg = event.object.message["text"].strip()
        uid = event.object.message["from_id"]
        low = msg.lower()

        if uid in states:
            step = states[user_id]["step"]

            if step == "set_uid":
                states[user_id]["uid"] = msg
                states[user_id]["step"] = "set_field"
                send(user_id, "Введите поле:")
                continue

            elif step == "set_field":
                states[user_id]["field"] = msg
                states[user_id]["step"] = "set_value"
                send(user_id, "Введите значение:")
                continue

            elif step == "set_value":
                uid = states[user_id]["uid"]
                field = states[user_id]["field"]

                if uid in mods:
                    mods[uid][field] = msg
                    save_data()
                    send(user_id, "✅ Данные изменены.", keyboard=admin_keyboard())
            else:
                send(user_id, "❌ Не найден.")

            del states[user_id]
            continue

        # ===================
        # BUTTONS
        # ===================
        if low == "📋 профиль":
            send(uid, profile(uid), menu(uid))
            continue

        elif low == "📈 повышение":
            states[uid] = "raise"
            send(uid, "✍ Напишите причину заявки:", menu(uid))
            continue

        elif low == "📷 доказательства":
            send(uid, "📷 Отправьте фото с подписью.", menu(uid))
            continue

        elif low == "📝 отчёт":
            states[uid] = "report"
            send(uid, "✍ Напишите отчёт.", menu(uid))
            continue

        elif msg.lower() == "✏ изменить данные":
            if not is_admin(uid):
                send(uid, "❌ Нет доступа.")
                continue

            states[uid] = {"step":"set_uid"}

            send(uid, "Введите ID пользователя:",
                keyboard=admin_keyboard())
            continue

        elif low == "🏆 карьера":
            send(uid,
"""🏆 Карьера:

1. Стажёр
2. Модератор
3. Старший модератор
4. Куратор
5. Руководство""",
            menu(uid))
            continue

        elif low == "👑 админка":
            if is_admin(uid):
                send(uid,
"""👑 Админ-команды:

/addmod ссылка ник
/delmod ссылка
/mods
/warn ссылка причина
/addballs ссылка число
/raise ссылка
/set ссылка поле значение
""",
                menu(uid))
            continue
        # ===================
        # STATES
        # ===================
        if uid in states:
            if states[uid] == "raise":
                send(
                    ADMIN_ID,
                    f"📩 Заявка на повышение\n\n[id{uid}|Пользователь]\n📝 {msg}"
                )
                send(uid, "✅ Заявка отправлена.", menu(uid))
                del states[uid]
                continue

            elif states[uid] == "report":
                send(
                    ADMIN_ID,
                    f"📝 Новый отчёт\n\n[id{uid}|Пользователь]\n📄 {msg}"
                )
                send(uid, "✅ Отчёт отправлен.", menu(uid))
                del states[uid]
                continue

        # ===================
        # COMMANDS
        # ===================
        if not msg.startswith("/"):
            continue

        args = msg.split()
        cmd = args[0].lower()

        if cmd == "/start":
            send(uid, "✅ SMART PANEL активирован.", menu(uid))

        elif cmd == "/mods":
            if not is_admin(uid):
                continue

            text = "👥 Состав:\n\n"

            for x in mods:
                text += f"[id{x}|{mods[x]['nick']}]\n"

            send(uid, text, menu(uid))

        elif cmd == "/addmod":
            if not is_admin(uid):
                continue

            parts = msg.split(maxsplit=2)

            if len(parts) < 3:
                send(uid, "/addmod ссылка ник")
                continue

            target = parse_user(parts[1])
            nick = parts[2]

            if not target:
                send(uid, "❌ Пользователь не найден.")
                continue

            create_mod(target, nick)
            send(uid, "✅ Добавлен.", menu(uid))

        elif cmd == "/delmod":
            if not is_admin(uid):
                continue

            if len(args) < 2:
                continue

            target = parse_user(args[1])

            if target in mods:
                del mods[target]
                save_data()
                send(uid, "✅ Удалён.", menu(uid))

        elif cmd == "/warn":
            if not is_admin(uid):
                continue

            if len(args) < 3:
                continue

            target = parse_user(args[1])

            if target in mods:
                mods[target]["warns"] += 1
                save_data()

                reason = " ".join(args[2:])

                send(uid, "✅ Выговор выдан.", menu(uid))
                send(
                    int(target),
                    f"⚠️ Вам выдан выговор.\nПричина: {reason}",
                    menu(int(target))
                )

        elif cmd == "/addballs":
            if not is_admin(uid):
                continue

            if len(args) < 3:
                continue

            target = parse_user(args[1])

            if target in mods:
                amount = int(args[2])
                mods[target]["balls"] += amount
                save_data()
                send(uid, "✅ Баллы выданы.", menu(uid))

        elif cmd == "/raise":
            if not is_admin(uid):
                continue

            if len(args) < 2:
                continue

            target = parse_user(args[1])

            if target in mods:
                mods[target]["role"] = "Старший модератор"
                save_data()

                send(uid, "✅ Повышен.", menu(uid))
                send(int(target), "🎉 Вас повысили!", menu(int(target)))

        elif cmd == "/set":
            if not is_admin(uid):
                continue

            if len(args) < 4:
                continue

            target = parse_user(args[1])
            field = args[2]
            value = " ".join(args[3:])

            if target in mods and field in mods[target]:
                mods[target][field] = value
                save_data()
                send(uid, "✅ Изменено.", menu(uid))
