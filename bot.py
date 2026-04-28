import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import sqlite3
import json

TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"

ADMINS = [674691524, 642009529, 547053039]

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

states = {}

# =========================
# DATABASE
# =========================
db = sqlite3.connect("base.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
warns INTEGER DEFAULT 0,
vigs INTEGER DEFAULT 0,
coins INTEGER DEFAULT 0
)
""")
db.commit()

# =========================
# FUNCTIONS
# =========================
def reg(uid):
    sql.execute("INSERT OR IGNORE INTO users(id) VALUES(?)", (uid,))
    db.commit()

def get(uid):
    reg(uid)
    sql.execute("SELECT * FROM users WHERE id=?", (uid,))
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

# =========================
# KEYBOARDS
# =========================
def menu():
    kb = VkKeyboard(one_time=False)

    kb.add_button("🪪 Статистика", VkKeyboardColor.PRIMARY)
    kb.add_button("🗃 Заявления", VkKeyboardColor.POSITIVE)
    kb.add_line()

    kb.add_button("⚖ Инструктаж", VkKeyboardColor.SECONDARY)
    kb.add_button("🆘 SOS", VkKeyboardColor.NEGATIVE)

    return kb.get_keyboard()

def apps():
    kb = VkKeyboard(one_time=False)

    kb.add_button("📑 Отчёт", VkKeyboardColor.PRIMARY)
    kb.add_button("🛩 Неактив", VkKeyboardColor.SECONDARY)
    kb.add_line()

    kb.add_button("🔖 Повышение", VkKeyboardColor.POSITIVE)
    kb.add_button("🗂 Снятие выговора", VkKeyboardColor.NEGATIVE)
    kb.add_line()

    kb.add_button("🔕 Пропуск собрания", VkKeyboardColor.SECONDARY)
    kb.add_button("🔙 Назад", VkKeyboardColor.SECONDARY)

    return kb.get_keyboard()

print("Бот запущен.")

# =========================
# LOOP
# =========================
for event in longpoll.listen():

    if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
        continue

    uid = event.user_id
    msg = event.text.strip()
    low = msg.lower()

    reg(uid)

    # =====================
    # STATES
    # =====================
    # =====================
# STATES
# =====================

if uid in states:

    action = states[uid]

    attachment = ""

    try:
        atts = event.message_data["attachments"]

        arr = []

        for a in atts:
            if a["type"] == "photo":
                p = a["photo"]
                arr.append(f'photo{p["owner_id"]}_{p["id"]}')

        attachment = ",".join(arr)

    except:
        pass

            if action == "report":
            for admin in ADMINS:
                send(
                    admin,
                    f"📄 Новый отчёт\n\n👤 id{uid}\n📝 {msg}",
                    attachment=attachment
                )

            send(uid, "✅ Отчёт отправлен.")
            del states[uid]
            continue

    # =====================
    # COMMANDS
    # =====================
    if low == "/start":
        send(uid, "✅ Панель активирована.", menu())

    elif low == "🪪 статистика":
        user = get(uid)

        send(uid,
f"""🪪 Ваша статистика

🆔 ID: {uid}
⚠ Предупреждения: {user[1]}
⛔ Выговоры: {user[2]}
💰 Coins: {user[3]}""",
menu())

    elif low == "🗃 заявления":
        send(uid, "🗃 Раздел заявлений:", apps())

    elif low == "⚖ инструктаж":
        send(uid,
"""⚖ Инструктаж:

• Соблюдать правила
• Быть активным
• Выполнять норму
• Следить за чатом""",
menu())

    elif low == "🆘 sos":
        send_admins(f"🆘 SOS вызов от id{uid}")
        send(uid, "✅ Руководство уведомлено.", menu())

    # =====================
    # APPLICATIONS
    # =====================
    elif low == "📑 отчёт":
        states[uid] = "report"
        send(uid, "📑 Отправьте текст отчёта и/или фото.")

    elif low == "🛩 неактив":
        states[uid] = "inactive"
        send(uid, "🛩 Укажите причину неактива.")

    elif low == "🔖 повышение":
        states[uid] = "raise"
        send(uid, "🔖 Почему вас должны повысить?")

    elif low == "🗂 снятие выговора":
        states[uid] = "vig"
        send(uid, "🗂 Укажите причину снятия.")

    elif low == "🔕 пропуск собрания":
        states[uid] = "meeting"
        send(uid, "🔕 Укажите причину пропуска.")

    elif low == "🔙 назад":
        send(uid, "🏠 Главное меню.", menu())
