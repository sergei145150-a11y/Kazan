import vk_api
import sqlite3
import random

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# ==================================
# CONFIG
# ==================================
TOKEN = "vk1.a.FJKFjHTWfHQM-DgOtBH3y35k_8L13uZiaA6kvsUXxJcRG-fvChOWJLzwVcUrphGUWtHsf2i1NxfYagKRVMNxB1brG8c3YX0y2L-VwKzfY5hOnWO7Eex5ysAdSmluSEYWy-1XQgCMCcpCuQxDaRc5c950wWgJTU0_FT-ufn8nsxw6U_ue4VOY7bxbemrcsEsdFYw7PnSBC5vOP8lYT4NqCA"
GROUP_ID = 238116016

ADMINS = [674691524, 642009529, 547053039]

# ==================================
# VK
# ==================================
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# ==================================
# DATABASE
# ==================================
db = sqlite3.connect("base.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS users(
uid INTEGER PRIMARY KEY,
warns INTEGER DEFAULT 0,
vigs INTEGER DEFAULT 0,
coins INTEGER DEFAULT 0
)
""")
db.commit()

# ==================================
# MEMORY
# ==================================
states = {}

# ==================================
# FUNCTIONS
# ==================================
def reg(uid):
    sql.execute("INSERT OR IGNORE INTO users(uid) VALUES(?)", (uid,))
    db.commit()

def get(uid):
    sql.execute("SELECT * FROM users WHERE uid=?", (uid,))
    return sql.fetchone()

def send(uid, text, keyboard=None, attachment=None):
    vk.messages.send(
        user_id=uid,
        random_id=random.randint(1, 999999999),
        message=text,
        keyboard=keyboard,
        attachment=attachment
    )

def send_admins(text, attachment=None):
    for admin in ADMINS:
        send(admin, text, attachment=attachment)

# ==================================
# PHOTO GETTER
# ==================================
def get_photos(msg):
    arr = []

    try:
        # Основной источник
        if "attachments" in msg:

            for item in msg["attachments"]:

                if item["type"] == "photo":
                    p = item["photo"]

                    owner = p["owner_id"]
                    pid = p["id"]
                    key = p.get("access_key")

                    if key:
                        arr.append(f"photo{owner}_{pid}_{key}")
                    else:
                        arr.append(f"photo{owner}_{pid}")

        # Дополнительный источник (иногда VK кладёт сюда)
        if "fwd_messages" in msg:
            for fw in msg["fwd_messages"]:
                if "attachments" in fw:
                    for item in fw["attachments"]:
                        if item["type"] == "photo":
                            p = item["photo"]

                            owner = p["owner_id"]
                            pid = p["id"]
                            key = p.get("access_key")

                            if key:
                                arr.append(f"photo{owner}_{pid}_{key}")
                            else:
                                arr.append(f"photo{owner}_{pid}")

    except Exception as e:
        print("PHOTO ERROR:", e)

    # Убираем дубли, сохраняя порядок
    arr = list(dict.fromkeys(arr))

    # До 10 фото
    return ",".join(arr[:10])

# ==================================
# KEYBOARDS
# ==================================
def menu():
    kb = VkKeyboard(one_time=False)

    kb.add_button("🪪 Статистика", VkKeyboardColor.PRIMARY)
    kb.add_button("🗂 Заявления", VkKeyboardColor.POSITIVE)
    kb.add_line()

    kb.add_button("⚖ Инструктаж", VkKeyboardColor.SECONDARY)
    kb.add_button("🆘 SOS", VkKeyboardColor.NEGATIVE)

    return kb.get_keyboard()

def claims():
    kb = VkKeyboard(one_time=False)

    kb.add_button("📑 Отчёт", VkKeyboardColor.PRIMARY)
    kb.add_button("🛩 Неактив", VkKeyboardColor.SECONDARY)
    kb.add_line()

    kb.add_button("🔖 Повышение", VkKeyboardColor.POSITIVE)
    kb.add_button("🗂 Снятие выговора", VkKeyboardColor.PRIMARY)
    kb.add_line()

    kb.add_button("🔕 Пропуск собрания", VkKeyboardColor.NEGATIVE)
    kb.add_line()

    kb.add_button("⬅ Назад", VkKeyboardColor.SECONDARY)

    return kb.get_keyboard()

# ==================================
# START
# ==================================
print("BOT STARTED")

for event in longpoll.listen():

    if event.type != VkBotEventType.MESSAGE_NEW:
        continue

    msg = event.object["message"]

    uid = msg["from_id"]
    text = msg["text"].strip()
    low = text.lower()

    reg(uid)

    # ==================================
    # STATES
    # ==================================
    if uid in states:

        action = states[uid]
        attachment = get_photos(msg)

        if action == "report":
            send_admins(
                f"📑 Новый отчёт\n\n👤 id{uid}\n📝 {text if text else 'Без текста'}",
                attachment=attachment
            )
            send(uid, "✅ Отчёт отправлен.", menu())
            del states[uid]
            continue

        elif action == "inactive":
            send_admins(f"🛩 Неактив\n\n👤 id{uid}\n📝 {text}")
            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

        elif action == "up":
            send_admins(f"🔖 Повышение\n\n👤 id{uid}\n📝 {text}")
            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

        elif action == "vigoff":
            send_admins(f"🗂 Снятие выговора\n\n👤 id{uid}\n📝 {text}")
            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

        elif action == "skip":
            send_admins(f"🔕 Пропуск собрания\n\n👤 id{uid}\n📝 {text}")
            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

    # ==================================
    # COMMANDS
    # ==================================
    if low == "/start":
        send(uid, "✅ Панель активирована.", menu())

    elif low == "🪪 статистика":
        user = get(uid)

        send(
            uid,
            f"""🪪 Ваша статистика

🆔 ID: {uid}
⚠ Предупреждения: {user[1]}
⛔ Выговоры: {user[2]}
💰 Coins: {user[3]}""",
            menu()
        )

    elif low == "🗂 заявления":
        send(uid, "🗂 Раздел заявлений:", claims())

    elif low == "⚖ инструктаж":
        send(uid,
"""⚖ Инструктаж:

• Соблюдать правила
• Быть активным
• Работать честно
• Уважать состав""",
        menu())

    elif low == "🆘 sos":
        send_admins(f"🆘 SOS вызов от id{uid}")
        send(uid, "✅ Руководство уведомлено.", menu())

    # ==================================
    # BUTTONS
    # ==================================
    elif low == "📑 отчёт":
        states[uid] = "report"
        send(uid, "📑 Отправьте текст отчёта.\nМожно добавить фото.")

    elif low == "🛩 неактив":
        states[uid] = "inactive"
        send(uid, "🛩 Укажите причину и срок неактива.")

    elif low == "🔖 повышение":
        states[uid] = "up"
        send(uid, "🔖 Почему вас нужно повысить?")

    elif low == "🗂 снятие выговора":
        states[uid] = "vigoff"
        send(uid, "🗂 Укажите причину снятия выговора.")

    elif low == "🔕 пропуск собрания":
        states[uid] = "skip"
        send(uid, "🔕 Укажите причину пропуска.")

    elif low == "⬅ назад":
        send(uid, "⬅ Главное меню.", menu())
