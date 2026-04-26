
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import json, os
from datetime import datetime

TOKEN = os.getenv("VK_TOKEN", "PASTE_TOKEN_HERE")
ADMIN_ID = 547053039
DATA_FILE = "mods.json"

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

mods = load_data()

def ensure(uid):
    uid=str(uid)
    if uid not in mods:
        mods[uid]={
            "nick":f"id{uid}","age":"Не указан","timezone":"МСК",
            "role":"Модератор","position":"Не указана",
            "date_add":datetime.now().strftime("%d.%m.%Y"),
            "days_post":0,"last_up":"Нет","norm_days":0,"balls":0,
            "warns":0,"preds":0,"ustniki":0,"inactive":"Нет",
            "inactive_days":0,"discord":"Не указан",
            "forum":"Не указан","telegram":"Не указан"
        }
        save_data(mods)

def card(uid):
    ensure(uid)
    m=mods[str(uid)]
    return f"""🎲 Статистика администратора

🟩 Игровой Ник/VK: {m['nick']}
🟩 Возраст: {m['age']}
🟩 Час пояс: {m['timezone']}
🟩 Уровень прав: {m['role']}
🟩 Должность: {m['position']}

✳ Поставлен: {m['date_add']}
✳ Дней на посту: {m['days_post']}
✳ Последнее повышение: {m['last_up']}

🟪 Дней выполненной нормы: {m['norm_days']}
🟪 Количество баллов: {m['balls']}
🟪 Количество выговоров: {m['warns']}
🟪 Количество предов: {m['preds']}
🟪 Количество устников: {m['ustniki']}

🅰 Действующий неактив: {m['inactive']}
🅰 Количество неактивов за месяц: {m['inactive_days']} дней

🟧 Discord: {m['discord']}
🟧 Форум: {m['forum']}
🟧 Telegram: {m['telegram']}"""

print("Bot started")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.strip()
        low = text.lower()
        uid = event.user_id

        if uid != ADMIN_ID:
            continue

        if low.startswith("/addmod"):
            parts=text.split()
            if len(parts)>1:
                ensure(parts[1]); msg="✅ Добавлен"
            else: msg="Используй /addmod ID"
        elif low.startswith("/card"):
            parts=text.split()
            msg=card(parts[1]) if len(parts)>1 else "Используй /card ID"
        else:
            continue

        vk.messages.send(user_id=uid, random_id=0, message=msg)
