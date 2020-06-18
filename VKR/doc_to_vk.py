from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import requests
import json
import random


version = 5.103
vk_session = vk_api.VkApi(token='0cd84b4d2eaa5261aa68604725ec2caf0e3cad21a64401dba923a64143cb8b4c1eeb381107ad0bc6c596d')
session_api = vk_session.get_api()


def video_messages():
        """ Загрузка doc в сообщения """
        randid = random.randint(-9223372036854775808, +9223372036854775807)
        peer_id=177910403
        url = vk_session.method('video.save',{'peer_id':peer_id})
        print(url)
        r = requests.post(url['upload_url'], files={'video_file': open('video.mp4', 'rb')}).json()
        print(r)
        attachment = 'video'+str(r['owner_id'])+'_'+str(r['video_id'])
        message = vk_session.method('messages.send',{'user_id': peer_id, 'v': version, 'message': 'ИЙАБАБА', 'random_id': randid, 'attachment':attachment})

video_messages()