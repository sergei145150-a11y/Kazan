import vk_api
import sqlite3
import random
import time

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# =========================
# НАСТРОЙКИ
# =========================
TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"

ADMINS = [674691524, 642009529, 547053039]

# =========================
# VK
# =========================
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# =========================
# БД
# =========================
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

# =========================
# STATE
# =========================
states = {}

# =========================
# FUNCTIONS
# =========================
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

# =========================
# КЛАВИАТУРЫ
# =========================
def menu():
    kb = VkKeyboard(one_time=False)

    kb.add_button("🪪 Статистика", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🗂 Заявления", color=VkKeyboardColor.POSITIVE)
    kb.add_line()

    kb.add_button("⚖ Инструктаж", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🆘 SOS", color=VkKeyboardColor.NEGATIVE)

    return kb.get_keyboard()

def zayavki():
    kb = VkKeyboard(one_time=False)

    kb.add_button("📑 Отчёт", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🛩 Неактив", color=VkKeyboardColor.SECONDARY)
    kb.add_line()

    kb.add_button("🔖 Повышение", color=VkKeyboardColor.POSITIVE)
    kb.add_button("🗂 Снятие выговора", color=VkKeyboardColor.PRIMARY)
    kb.add_line()

    kb.add_button("🔕 Пропуск собрания", color=VkKeyboardColor.NEGATIVE)

    return kb.get_keyboard()

# =========================
# MAIN LOOP
# =========================
for event in longpoll.listen():

    if event.type != VkEventType.MESSAGE_NEW:
        continue

    if not event.to_me:
        continue

    uid = event.user_id
    text = event.text.strip()
    low = text.lower()

    reg(uid)

    # =========================
    # STATE SYSTEM
    # =========================
    if uid in states:

        action = states[uid]
        attachment = ""

        try:
            msg_id = event.message_id

            data = vk.messages.getById(message_ids=msg_id)

            items = data["items"][0]["attachments"]

            arr = []

            for item in items:
                if item["type"] == "photo":
                    p = item["photo"]
                    arr.append(f'photo{p["owner_id"]}_{p["id"]}')

            attachment = ",".join(arr)

        except Exception:
            attachment = ""

except Exception as e:
    attachment = ""

        # ОТЧЕТ
        if action == "report":

            for admin in ADMINS:
                send(
                    admin,
                    f"📑 Новый отчёт\n\n👤 id{uid}\n📝 {text if text else 'Без текста'}"
                    attachment=attachment
                )

            send(uid, "✅ Отчёт отправлен.", menu())
            del states[uid]
            continue

        # НЕАКТИВ
        if action == "inactive":

            for admin in ADMINS:
                send(admin, f"🛩 Заявка на неактив\n\n👤 id{uid}\n📝 {text}")

            send(uid, "✅ Неактив отправлен.", menu())
            del states[uid]
            continue

        # ПОВЫШЕНИЕ
        if action == "up":

            for admin in ADMINS:
                send(admin, f"🔖 Заявка на повышение\n\n👤 id{uid}\n📝 {text}")

            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

        # СНЯТИЕ ВЫГОВОРА
        if action == "vigoff":

            for admin in ADMINS:
                send(admin, f"🗂 Снятие выговора\n\n👤 id{uid}\n📝 {text}")

            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

        # ПРОПУСК СОБРАНИЯ
        if action == "skip":

            for admin in ADMINS:
                send(admin, f"🔕 Пропуск собрания\n\n👤 id{uid}\n📝 {text}")

            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

    # =========================
    # COMMANDS
    # =========================
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
        send(
            uid,
            """🗂 Раздел заявлений:

📑 Отчёт
🛩 Неактив
🔖 Повышение
🗂 Снятие выговора
🔕 Пропуск собрания

Выберите кнопку ниже.""",
            zayavki()
        )

    elif low == "⚖ инструктаж":
        send(
            uid,
            """⚖ Инструктаж:

• Правила модерации
• Команды
• Жалобы
• Наказания

Раздел обновляется.""",
            menu()
        )

    elif low == "🆘 sos":

        for admin in ADMINS:
            send(admin, f"🆘 SOS вызов от id{uid}")

        send(uid, "🆘 Администрация вызвана.", menu())

    # =========================
    # ЗАЯВЛЕНИЯ
    # =========================
    elif low == "📑 отчёт":
        states[uid] = "report"
        send(uid, "📑 Отправь текст отчёта.\nМожно с фотографией.")

    elif low == "🛩 неактив":
        states[uid] = "inactive"
        send(uid, "🛩 Напиши причину и срок неактива.")

    elif low == "🔖 повышение":
        states[uid] = "up"
        send(uid, "🔖 Напиши причину повышения.")

    elif low == "🗂 снятие выговора":
        states[uid] = "vigoff"
        send(uid, "🗂 Напиши причину снятия выговора.")

    elif low == "🔕 пропуск собрания":
        states[uid] = "skip"
        send(uid, "🔕 Напиши причину пропуска собрания.")
