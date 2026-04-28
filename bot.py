import vk_api
import random
import sqlite3
import time

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# ==================================
# НАСТРОЙКИ
# ==================================

TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"

ADMINS = [
    674691524,
    642009529,
    547053039
]

# ==================================
# VK
# ==================================

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# ==================================
# БАЗА
# ==================================

db = sqlite3.connect("base.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER,
warns INTEGER,
vigs INTEGER,
coins INTEGER
)
""")
db.commit()

# ==================================
# ФУНКЦИИ
# ==================================

def reg(uid):
    user = sql.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if user is None:
        sql.execute(
            "INSERT INTO users VALUES(?,?,?,?)",
            (uid, 0, 0, 0)
        )
        db.commit()

def get(uid):
    return sql.execute(
        "SELECT * FROM users WHERE id=?",
        (uid,)
    ).fetchone()

def send(uid, text, keyboard=None, attachment=None):
    vk.messages.send(
        user_id=uid,
        message=text,
        random_id=random.randint(1, 999999999),
        keyboard=keyboard,
        attachment=attachment
    )

def menu():
    kb = VkKeyboard(one_time=False)

    kb.add_button("🪪 Статистика", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🗃 Заявления", color=VkKeyboardColor.POSITIVE)
    kb.add_line()

    kb.add_button("⚖ Инструктаж", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🆘 SOS", color=VkKeyboardColor.NEGATIVE)

    return kb.get_keyboard()

# ==================================
# STATES
# ==================================

states = {}

# ==================================
# START
# ==================================

print("BOT STARTED")

for event in longpoll.listen():

    if event.type != VkEventType.MESSAGE_NEW:
        continue

    if not event.to_me:
        continue

    uid = event.user_id
    msg = event.text.strip()
    low = msg.lower()

    reg(uid)

    # ==================================
    # STATES
    # ==================================

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

        # ОТЧЁТ
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

        # НЕАКТИВ
        if action == "inactive":
            for admin in ADMINS:
                send(admin, f"🛩 Неактив\n\n👤 id{uid}\n📝 {msg}")

            send(uid, "✅ Неактив отправлен.")
            del states[uid]
            continue

        # ПОВЫШЕНИЕ
        if action == "up":
            for admin in ADMINS:
                send(admin, f"🔖 Заявка на повышение\n\n👤 id{uid}\n📝 {msg}")

            send(uid, "✅ Заявка отправлена.")
            del states[uid]
            continue

        # СНЯТИЕ ВЫГОВОРА
        if action == "remove_vig":
            for admin in ADMINS:
                send(admin, f"🗂 Снятие выговора\n\n👤 id{uid}\n📝 {msg}")

            send(uid, "✅ Заявка отправлена.")
            del states[uid]
            continue

        # ПРОПУСК СОБРАНИЯ
        if action == "skip":
            for admin in ADMINS:
                send(admin, f"🔕 Пропуск собрания\n\n👤 id{uid}\n📝 {msg}")

            send(uid, "✅ Заявка отправлена.")
            del states[uid]
            continue

    # ==================================
    # КОМАНДЫ
    # ==================================

    if low == "/start":
        send(uid, "✅ Панель активирована.", menu())
        continue

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
        continue

    elif low == "🗃 заявления":
        send(
            uid,
            """🗃 Раздел заявлений:

📑 Отчёт
🛩 Неактив
🔖 Повышение
🗂 Снятие выговора
🔕 Пропуск собрания

Напиши нужный вариант."""
        )
        continue

    elif low == "📑 отчёт":
        states[uid] = "report"
        send(uid, "📑 Отправь текст отчёта.\nМожно с фотографией.")
        continue

    elif low == "🛩 неактив":
        states[uid] = "inactive"
        send(uid, "🛩 Напиши причину неактива.")
        continue

    elif low == "🔖 повышение":
        states[uid] = "up"
        send(uid, "🔖 Напиши причину повышения.")
        continue

    elif low == "🗂 снятие выговора":
        states[uid] = "remove_vig"
        send(uid, "🗂 Напиши причину снятия выговора.")
        continue

    elif low == "🔕 пропуск собрания":
        states[uid] = "skip"
        send(uid, "🔕 Напиши причину пропуска собрания.")
        continue

    elif low == "⚖ инструктаж":
        send(
            uid,
            """⚖ Полезные материалы:

• Правила модерации
• Команды модерации
• Жалобы
• Наказания

Раздел в разработке.""",
            menu()
        )
        continue

    elif low == "🆘 sos":
        for admin in ADMINS:
            send(admin, f"🆘 SOS вызов от id{uid}")

        send(uid, "🆘 Администрация уведомлена.", menu())
        continue
