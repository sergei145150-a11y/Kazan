import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random

TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"

ADMINS = [674691524, 642009529, 547053039]

vk = vk_api.VkApi(token=TOKEN)
api = vk.get_api()
longpoll = VkLongPoll(vk)

states = {}

def send(user_id, text, keyboard=None):
    api.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 999999999),
        keyboard=keyboard
    )

def menu():
    kb = VkKeyboard(one_time=False)
    kb.add_button("🪪 Статистика", VkKeyboardColor.PRIMARY)
    kb.add_button("🗃 Заявления", VkKeyboardColor.POSITIVE)
    kb.add_line()
    kb.add_button("⚖ Инструктаж", VkKeyboardColor.SECONDARY)
    kb.add_button("🆘 SOS", VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

def apps_menu():
    kb = VkKeyboard(one_time=False)
    kb.add_button("📑 Отчёт", VkKeyboardColor.PRIMARY)
    kb.add_button("🛩 Неактив", VkKeyboardColor.POSITIVE)
    kb.add_line()
    kb.add_button("🔖 Повышение", VkKeyboardColor.PRIMARY)
    kb.add_button("🗂 Снятие выговора", VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("🔕 Пропуск собрания", VkKeyboardColor.NEGATIVE)
    kb.add_line()
    kb.add_button("🔙 Назад", VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()

def send_to_admins(title, uid, text):
    msg = f"{title}\n\n👤 Пользователь: id{uid}\n📝 Текст: {text}"
    for admin in ADMINS:
        send(admin, msg)

print("Бот запущен")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        uid = event.user_id
        msg = event.text.strip()
        low = msg.lower()

        if uid in states:
            action = states[uid]

            if action == "report":
                send_to_admins("📑 Новый отчёт", uid, msg)
                send(uid, "✅ Отчёт отправлен.", menu())
            elif action == "inactive":
                send_to_admins("🛩 Заявка на неактив", uid, msg)
                send(uid, "✅ Заявка отправлена.", menu())
            elif action == "raise":
                send_to_admins("🔖 Заявка на повышение", uid, msg)
                send(uid, "✅ Заявка отправлена.", menu())
            elif action == "remove_warn":
                send_to_admins("🗂 Снятие выговора", uid, msg)
                send(uid, "✅ Заявка отправлена.", menu())
            elif action == "skip":
                send_to_admins("🔕 Пропуск собрания", uid, msg)
                send(uid, "✅ Заявка отправлена.", menu())

            del states[uid]
            continue

        if low == "/start":
            send(uid, "✅ Панель активирована.", menu())

        elif low == "🪪 статистика":
            send(uid,
                 f"🪪 Ваш профиль\n\n"
                 f"ID: {uid}\n"
                 f"Предупреждения: 0\n"
                 f"Выговоры: 0",
                 menu())

        elif low == "🗃 заявления":
            send(uid, "🗃 Раздел заявлений:", apps_menu())

        elif low == "⚖ инструктаж":
            send(uid,
                 "⚖ Полезные материалы:\n\n"
                 "• Правила модерации\n"
                 "• Команды модерации\n"
                 "• Жалобы",
                 menu())

        elif low == "🆘 sos":
            for admin in ADMINS:
                send(admin, f"🆘 SOS вызов от id{uid}")
            send(uid, "✅ Администрация уведомлена.", menu())

        elif low == "📑 отчёт":
            states[uid] = "report"
            send(uid, "Введите текст отчёта:")

        elif low == "🛩 неактив":
            states[uid] = "inactive"
            send(uid, "Введите причину неактива:")

        elif low == "🔖 повышение":
            states[uid] = "raise"
            send(uid, "Введите причину повышения:")

        elif low == "🗂 снятие выговора":
            states[uid] = "remove_warn"
            send(uid, "Введите причину снятия выговора:")

        elif low == "🔕 пропуск собрания":
            states[uid] = "skip"
            send(uid, "Введите причину пропуска собрания:")

        elif low == "🔙 назад":
            send(uid, "Главное меню", menu())
