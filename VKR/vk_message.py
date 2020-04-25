from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from datetime import datetime
import json

version = 5.103


vk_session = vk_api.VkApi(token='f8ba6ec850c69b68345aa5d53a220624bf01c2e376eef5db9b762d214bdc3afacbdc4de221ab8fd5b219b')


session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            print(str(event.user_id))
            user = vk_session.method('users.get', {'user_ids':event.user_id, 'v': version})
            for name in user:
                print("Сообщение от: "+name.get('first_name')+' '+name.get('last_name'))
            print("Пришло в "+ str(datetime.strftime(datetime.now(), "%H:%M:%S")))
            print("Текст сообщения: "+ str(event.message))

