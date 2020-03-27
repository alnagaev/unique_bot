import telebot
from telebot import types
import dbworker
import config
import time
import sql_lite_db
import jsonpickle
import json

bot = telebot.TeleBot(config.api_key)


def render_keyboard(keys):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*[types.InlineKeyboardButton(name, callback_data=name) for name in keys])
    return keyboard


@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.send_message(message.chat.id, 'Я бот-коллекционер, который собирает фотокарточки из чатиков. Введите /start и '
                                      'я вышлю вам только уникальные изображения из выбранного чата')


# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    keyboard = render_keyboard(sql_lite_db.get_chats())
    bot.send_message(message.chat.id, 'Выберите в меню группу, которая вам интересна',
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Вот мои коллекции: ")
    keyboard = render_keyboard(sql_lite_db.get_chats())
    bot.send_message(message.chat.id, 'Выберите в меню что вам интересно!',
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call.message.chat.id)
    bot.answer_callback_query(call.id, "Доставляю")
    try:
        all_data = sql_lite_db.get_values('chat_title', call.data)
        if len(all_data['photos']) > 2:
            bot.send_media_group(call.message.chat.id, (types.InputMediaPhoto(i) for i in all_data['photos']))
        else:
            for i in all_data['photos']:
                bot.send_photo(call.message.chat.id, i)
        if len(all_data['videos']) > 0:
            bot.send_media_group(call.message.chat.id, (types.InputMediaVideo(i) for i in all_data['videos']))
        if len(all_data['gifs']) > 0:
            bot.send_media_group(call.message.chat.id, (types.InputMediaDocument(i) for i in all_data['gifs']))
        if len(all_data['doc_images']) > 0:
            for doc in all_data['doc_images']:
                bot.send_document(call.message.chat.id, doc)

    except Exception as e:
        print(e)
        bot.send_message(call.message.chat.id, 'Что-то пошло не так')


def parse_response(message):
    message = json.loads(jsonpickle.encode(message))
    type_m = message["content_type"]
    if type_m == 'document' and message['document']['mime_type'] == 'video/mp4':
        type_m = 'video/mp4'
    if type_m == 'document' and message['document']['mime_type'] == 'image/jpeg':
        type_m = 'image/jpeg'

    def get_finfo(message):
        if type_m == 'photo':
            return message[type_m][1]["file_id"], message[type_m][1]["file_size"]
        elif type_m == 'video':
            return message[type_m]["file_id"], message[type_m]["file_size"]
        elif type_m == 'video/mp4':
            return message['thumb']["file_id"], message['thumb']["file_size"]
        elif type_m == 'image/jpeg':
            return message['document']["file_id"], message['document']["file_size"]

    file_id, file_size = get_finfo(message)
    chat_id = message["chat"]["id"]
    chat_title = message["chat"]["title"]
    date = message["date"]
    return file_id, date, file_size, type_m, chat_id, chat_title


@bot.message_handler(content_types=['photo', 'video', 'document'])
def check_docs(message):
    print(message)
    row = parse_response(message)
    try:
        sql_lite_db.add_values(row)
    except Exception as e:
        bot.send_message(message.chat.id, 'Data not collected yet')
        print(str(e))


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)  # или просто print(e) если у вас логгера нет,
        # или import traceback; traceback.print_exc() для печати полной инфы
        time.sleep(15)
