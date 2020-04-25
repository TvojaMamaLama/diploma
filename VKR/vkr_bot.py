import threading
import telebot
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import random
from datetime import datetime

bot = telebot.TeleBot('1085290664:AAEfMs9XwhZ1PCwcMLiYR28Kshkk_ctlERU')

# socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
# socket.socket = socks.socksocket

version = 5.103

vk_session = vk_api.VkApi(token='a2e5cc4b92341fcc890999df65b88f4a15dae14a12ba2ce5a83f19e28b07dd4d305890dacc093a26f1443')

session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def to_tg():
    while True:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    print(str(event.user_id))
                    user = vk_session.method('users.get', {'user_ids': event.user_id, 'v': version})
                    for name in user:
                        # print("Пришло в "+ str(datetime.strftime(datetime.now(), "%H:%M:%S")))
                        bot.send_message(443196199, str(event.user_id) + "\n<<" + name.get('first_name') + ' ' + name.get(
                            'last_name') + ">>\n" + event.message)


def listener_messages():
    bot.set_update_listener(to_tg())


def to_vk():
    @bot.message_handler(content_types=['text'])
    def replay(message):
        i = 0
        id = ''
        while message.reply_to_message.text[i] != '\n':
            id += message.reply_to_message.text[i]
            i += 1
        randid = random.randint(-9223372036854775808, +9223372036854775807)
        send_status = vk_session.method('messages.send', {'user_id': id, 'v': version, 'message': message.text, 'random_id': randid})
        bot.send_message(message.chat.id, 'Отправлено!')


potok1 = threading.Thread(target=listener_messages)
potok2 = threading.Thread(target=to_vk)
potok2.start()
potok1.start()
print("ЗАРАБОТАЛО")
bot.polling(none_stop=True)
