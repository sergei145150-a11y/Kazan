import vk_api
import json
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# =========================
# CONFIG
# =========================
TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"

ADMINS = [
    674691524,
    642009529,
    547053039
]

# =========================
# VK INIT
# =========================
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# =========================
# MEMORY
# =========================
states = {}
users = {}

# =========================
# HELPERS
# =========================
def send(user_id, text, keyboard=None, attachment=None):
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 999999999),
        keyboard=keyboard.get_keyboard() if keyboard else None,
        attachment=attachment
    )

def reg(uid):
    if uid not in users:
        users[uid] = {
            "warns": 0,
            "reprimands": 0,
            "coins": 0
        }

# =========================
# KEYBOARDS
# =========================
def menu():
    kb = VkKeyboard(resize=True)
    kb.add_button("🪪 Статистика", VkKeyboardColor.PRIMARY)
    kb.add_button("📂 Заявления", VkKeyboardColor.POSITIVE)
    kb.add_line()
    kb.add_button("⚖ Инструктаж", VkKeyboardColor.SECONDARY)
    kb.add_button("🆘 SOS", VkKeyboardColor.NEGATIVE)
    return kb

def claims_menu():
    kb = VkKeyboard(resize=True)
    kb.add_button("📑 Отчёт", VkKeyboardColor.PRIMARY)
    kb.add_button("🛩 Неактив", VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("🔖 Повышение", VkKeyboardColor.POSITIVE)
    kb.add_button("🗂 Снятие выговора", VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🔕 Пропуск собрания", VkKeyboardColor.NEGATIVE)
    kb.add_line()
    kb.add_button("⬅ Назад", VkKeyboardColor.SECONDARY)
    return kb

# =========================
# ATTACHMENTS
# =========================
def get_attachments(event):
    try:
        atts = event.message_data["attachments"]
        arr = []

        for a in atts:
            if a["type"] == "photo":
                p = a["photo"]
                arr.append(f'photo{p["owner_id"]}_{p["id"]}')

        return ",".join(arr)
    except:
        return ""

# =========================
# MAIN LOOP
# =========================
for event in longpoll.listen():

    if event.type != VkEventType.MESSAGE_NEW:
        continue

    if not event.to_me:
        continue

    uid = event.user_id
    msg = event.text.strip()
    low = msg.lower()

    reg(uid)

    # =====================
    # STATES
    # =====================
    if uid in states:

        action = states[uid]
        attach = get_attachments(event)

        # REPORT
        if action == "report":
            for admin in ADMINS:
                send(
                    admin,
                    f"📑 Новый отчёт\n\n👤 id{uid}\n📝 {msg}",
                    attachment=attach
                )

            send(uid, "✅ Отчёт отправлен.", menu())
            del states[uid]
            continue

        # INACTIVE
        if action == "inactive":
            for admin in ADMINS:
                send(
                    admin,
                    f"🛩 Заявка на неактив\n\n👤 id{uid}\n📝 {msg}",
                    attachment=attach
                )

            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

        # PROMOTION
        if action == "promo":
            for admin in ADMINS:
                send(
                    admin,
                    f"🔖 Заявка на повышение\n\n👤 id{uid}\n📝 {msg}",
                    attachment=attach
                )

            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

        # REMOVE REPRIMAND
        if action == "remove":
            for admin in ADMINS:
                send(
                    admin,
                    f"🗂 Снятие выговора\n\n👤 id{uid}\n📝 {msg}",
                    attachment=attach
                )

            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

        # MISS MEETING
        if action == "meeting":
            for admin in ADMINS:
                send(
                    admin,
                    f"🔕 Пропуск собрания\n\n👤 id{uid}\n📝 {msg}",
                    attachment=attach
                )

            send(uid, "✅ Заявка отправлена.", menu())
            del states[uid]
            continue

    # =====================
    # COMMANDS
    # =====================

    if low == "/start":
        send(uid, "✅ Панель активирована.", menu())
        continue

    elif low == "🪪 статистика":
        u = users[uid]

        send(
            uid,
            f"""🪪 Ваша статистика

🆔 ID: {uid}
⚠ Предупреждения: {u["warns"]}
⛔ Выговоры: {u["reprimands"]}
💰 Coins: {u["coins"]}""",
            menu()
        )
        continue

    elif low == "📂 заявления":
        send(
            uid,
            """📂 Раздел заявлений:

Выберите нужный вариант ниже.""",
            claims_menu()
        )
        continue

    elif low == "⚖ инструктаж":
        send(
            uid,
            """⚖ Полезные материалы:

• Правила модерации
• Команды модерации
• Жалобы
• Наказания""",
            menu()
        )
        continue

    elif low == "🆘 sos":
        for admin in ADMINS:
            send(admin, f"🆘 SOS вызов от id{uid}")

        send(uid, "✅ Администрация уведомлена.", menu())
        continue

    # =====================
    # CLAIM BUTTONS
    # =====================

    elif low == "📑 отчёт":
        states[uid] = "report"
        send(uid, "📑 Отправь текст отчёта.\nМожно с фотографией.")
        continue

    elif low == "🛩 неактив":
        states[uid] = "inactive"
        send(uid, "🛩 Напиши причину и срок неактива.")
        continue

    elif low == "🔖 повышение":
        states[uid] = "promo"
        send(uid, "🔖 Напиши причину повышения.")
        continue

    elif low == "🗂 снятие выговора":
        states[uid] = "remove"
        send(uid, "🗂 Напиши причину снятия выговора.")
        continue

    elif low == "🔕 пропуск собрания":
        states[uid] = "meeting"
        send(uid, "🔕 Напиши причину пропуска.")
        continue

    elif low == "⬅ назад":
        send(uid, "⬅ Возврат в меню.", menu())
        continue
