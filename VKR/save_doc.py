import telebot
from telebot import apihelper
from telebot import types


apihelper.proxy = {'https': 'socks5h://207.97.174.134'}
bot = telebot.TeleBot('1085290664:AAGiF_PuARRbdxjleH4s6g3kSVzzBuhmsBI')


@bot.message_handler(commands=["news"])
def geophone(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Новостная лента")
    button_geo = types.KeyboardButton(text="Шедевры рекламы")
    button_geo1 = types.KeyboardButton(text="Кинопоиск")
    keyboard.add(button_phone, button_geo,button_geo1)
    bot.send_message(message.chat.id, "Введите группу или выберите из списка", reply_markup=keyboard)



bot.polling(none_stop=True)