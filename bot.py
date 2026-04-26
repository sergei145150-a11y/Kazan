import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random

TOKEN = "vk1.a.gvt4eMCrtK9Nfl_6mH_xFQA2MVuJYHFMabOi3q-eB6nGEXCZtDUi5LvyQQF0TBrKN7mfxkPtGSQxrTUlUTJk97CGYv0NwsahZx8Hv_MbSizZoMTmuwwrOEaisQBcZZnBLs5T-fgQNyf0oyWJDGRskMMZ3jPKvLx6bX05nekBoEU8EmaYpYVLoeWiYTFdm5_eUNBjndOzIYyejCR5QyJO2A"
GROUP_ID = 238116016

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

longpoll = VkBotLongPoll(vk_session, GROUP_ID)

print("Бот запущен")

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = event.object.message["from_id"]
        text = event.object.message["text"]

        vk.messages.send(
            user_id=user_id,
            random_id=random.randint(1,99999999),
            message="Команда получена: " + text
        )
