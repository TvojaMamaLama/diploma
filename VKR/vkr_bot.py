import config
import threading
import telebot
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import random
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from telebot import apihelper

apihelper.proxy = {'https': config.PROXY }
bot = telebot.TeleBot(config.TOKEN)


version = 5.103

vk_session = vk_api.VkApi(token=config.VK_TOKEN)

session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def get_vk_id(message):
    id = ''
    i = 0
    if message.reply_to_message.text:
        while message.reply_to_message.text[i] != '\n':
            id += message.reply_to_message.text[i]
            i += 1
    else:
        while message.reply_to_message.caption[i] != '\n':
            id += message.reply_to_message.caption[i]
            i += 1

    return id


def photo_messages(peer_id,text):
        """ Загрузка изображений в сообщения"""
        randid = random.randint(-9223372036854775808, +9223372036854775807)
        url = vk_session.method('photos.getMessagesUploadServer',{'peer_id':peer_id})
        r = requests.post(url['upload_url'], files={'photo': open('photo_to_vk/photo.jpg', 'rb')}).json()
        photo = vk_session.method('photos.saveMessagesPhoto',{'server':r['server'],'photo':r['photo'],'hash':r['hash']})
        attachment = 'photo'+str(photo[0]['owner_id'])+'_'+str(photo[0]['id'])
        message = vk_session.method('messages.send',{'user_id': peer_id, 'v': version, 'message': text, 'random_id': randid, 'attachment':attachment})


def video_messages(peer_id,text):
        """ Загрузка видео в сообщения"""
        randid = random.randint(-9223372036854775808, +9223372036854775807)
        peer_id=177910403
        url = vk_session.method('video.save',{'peer_id':peer_id})
        r = requests.post(url['upload_url'], files={'video_file': open('video_to_vk/video.mp4', 'rb')}).json()
        attachment = 'video'+str(r['owner_id'])+'_'+str(r['video_id'])
        message = vk_session.method('messages.send',{'user_id': peer_id, 'v': version, 'message': text, 'random_id': randid, 'attachment':attachment})


def get_url(url):
    r = requests.get(url).text
    soup = BeautifulSoup(r,features='html.parser')

    video_url = soup.findAll('source')[1].get('src').split('?')[0]
    return video_url


def download_video(url):
    r = requests.get(url,stream=True)

    with open ('video/video.mp4','wb') as file:
        for chunk in r.iter_content(1024000):
            file.write(chunk)


def getAttachments( msg ):
    attachList = []
    msg = msg['items']
    for att in msg[0]['attachments'][0:]:
        attType = att.get( 'type' )
        attachment = att[attType]
        if attType == 'photo': # Проверка на тип фотографии
            for photoType in attachment.get('sizes')[0:]:
                if photoType.get('type') == 'x': # <=604x604
                    attachments = photoType.get('url')
                if photoType.get('type') == 'y': # >605x605
                    attachments = photoType.get('url')
                if photoType.get('type') == 'z': # <=1280x720
                    attachments = photoType.get('url')
                if photoType.get('type') == 'w':# >1280x720
                    attachments = photoType.get('url') # <=2560x1440
                    attType = 'other'

        elif attType == 'doc': # Проверка на тип документа:
            docType = attachment.get( 'type' )
            if docType != 3 and docType != 4 and docType != 5:
                attType = 'other'
            if attachment.get( 'url' ):
                attachments = attachment.get( 'url' )

        elif attType == 'sticker': # Проверка на стикеры:
            for sticker in attachment.get( 'images' )[0:]:
            # Можно 256 или 512, но будет слишком огромная пикча
                if sticker.get('width') == 128:
                    attachments = sticker.get( 'url' )

        elif attType == 'audio':
            attachments = str ( '𝅘𝅥𝅮 ' + attachment.get('artist') + ' - ' +
            attachment.get('title') + ' 𝅘𝅥𝅮' )
            attType = 'other'

        elif attType == 'audio_message':
            attachments = attachment.get('link_ogg')

        elif attType == 'video':
            ownerId = str( attachment.get( 'owner_id' ) )
            videoId = str( attachment.get( 'id' ) )
            accesskey = str( attachment.get( 'access_key' ) )
            fullURL = str( ownerId + '_' + videoId + '_' + accesskey)
            linkattach = vk_session.method('video.get',{'videos': fullURL })
            attachments = linkattach['items'][0].get('player')

    # Неизвестный тип?
        else:
            attachments = None
        
        attachList.append( { 'type':attType,'link':attachments } )

    return attachList


def to_tg():
    while True:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                print(str(event.user_id))
                user = vk_session.method('users.get', {'user_ids': event.user_id, 'v': version})
                name = user[0]
                msg = vk_session.method('messages.getById',{'message_ids':[event.message_id]})
                attachments = getAttachments(msg)
                if attachments == []:
                    bot.send_message(443196199, str(event.user_id) + "\n<<" + name.get('first_name') + ' ' + name.get('last_name') + ">>\n" + event.message)
                else:
                    for j in attachments[0:]:
                        attType = j.get( 'type' )
                        link = j.get( 'link' )
                        if attType == 'photo' or attType == 'sticker':
                            bot.send_photo(443196199, link, caption=str(event.user_id) + "\n<<" + name.get('first_name') + ' ' + name.get('last_name') + ">>\n" + event.message )
                        
                        elif attType == 'doc' or attType == 'gif' or attType == 'audio_message':
                            bot.send_document(443196199, link,caption=str(event.user_id) + "\n<<" + name.get('first_name') + ' ' + name.get('last_name') + ">>\n" + event.message)

                        elif attType == 'other':
                            bot.send_message(443196199,  str(event.user_id) + "\n<<" + name.get('first_name') + ' ' + name.get('last_name') + ">>\n" + event.message + '\n' + link) 

                        elif attType == 'video':
                            download_video(get_url(link))
                            video = open('video/video.mp4','rb')
                            bot.send_video(443196199, video, caption=str(event.user_id) + "\n<<" + name.get('first_name') + ' ' + name.get('last_name') + ">>\n" + event.message) 

                        else:
                            bot.send_message(443196199, str(event.user_id) + "\n<<" + name.get('first_name') + ' ' + name.get('last_name') + ">>\n" + event.message+'\n'+'(Неудалось обработать)' )


def listener_messages():
    bot.set_update_listener(to_tg())


def to_vk():
    @bot.message_handler(content_types=['text'])
    def replay(message):
        id = get_vk_id(message)
        randid = random.randint(-9223372036854775808, +9223372036854775807)
        send_status = vk_session.method('messages.send', {'user_id': id, 'v': version, 'message': message.text, 'random_id': randid})
        bot.send_message(message.chat.id, 'Отправлено!')
    
    @bot.message_handler(content_types=['photo'])
    def photo(message):
        text = message.caption
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('photo_to_vk/photo.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)
        id = get_vk_id(message)
        photo_messages(id,text)


    @bot.message_handler(content_types=['video'])
    def video(message):
        text = message.caption
        print(message)
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('video_to_vk/video.mp4', 'wb') as new_file:
            new_file.write(downloaded_file)
        id = get_vk_id(message)
        video_messages(id,text)
        
        

potok1 = threading.Thread(target=listener_messages)
potok2 = threading.Thread(target=to_vk)
potok2.start()
potok1.start()
print("ЗАРАБОТАЛО")

bot.polling(none_stop=True)
