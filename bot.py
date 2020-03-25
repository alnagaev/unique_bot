import telebot
from telebot import types
import os
import dbworker
from pathlib import Path
import images
import config
import time
import bot_utils
import sql_lite_db

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
    keyboard = render_keyboard(bot_utils.show_keys())
    bot.send_message(message.chat.id, 'Выберите в меню группу, которая вам интересна',
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Вот мои коллекции: ")
    keyboard = render_keyboard(bot_utils.show_keys())
    bot.send_message(message.chat.id, 'Выберите в меню что вам интересно!',
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call.message.chat.id)
    bot.answer_callback_query(call.id, "Доставляю")
    try:
        photos = images.get_unique('images', bot_utils.json_key(call.data))
        if len(photos) > 2:
            bot.send_media_group(call.message.chat.id, (types.InputMediaPhoto(i) for i in photos))
        else:
            for i in photos:
                bot.send_photo(call.message.chat.id, i)
    except Exception as e:
        print(e)
        print(os.getcwd())
        bot.send_message(call.message.chat.id, 'Что-то пошло не так')


# @bot.message_handler(content_types=['photo'])
# def check_document(message):
#     # Эту функцию стоит переработать, слишком много действий в одном def
#
#     if message.chat.type == 'group':
#         name = str(message.chat.id)  # Задумка была другая. Прости, Юра, мы все проебали
#         bot_utils.json_add(message.chat.title, name)
#     else:
#         name = str(message.chat.id)
#         bot_utils.json_add(name, name)
#
#     assert os.path.basename(os.getcwd()) == 'unique_bot', 'Directory error'
#
#     Path("./images/{}".format(name)).mkdir(parents=True, exist_ok=True)
#     print(message)
#     fileID = message.photo[-1].file_id
#     print('fileID =', fileID)
#     file = bot.get_file(fileID)
#     if '{}.jpg'.format(fileID) not in os.listdir('images/{}'.format(name)):
#         downloaded_file = bot.download_file(file.file_path)
#
#         with open('images/{}/{}.jpg'.format(name, fileID), 'xb') as new_file:
#             try:
#                 new_file.write(downloaded_file)
#             except Exception as e:
#                 print(str(e))
#     else:
#         print('already in directory')
#     bot.send_message(message.chat.id, 'smells like photo')


def parse_response(message):
    type = message['content_type']
    date = message['date']
    file_id = message[type][1]['file_id']
    file_size = message[type][1]['file_size']
    return file_id, date, file_size, type


@bot.message_handler(content_types=['photo', 'video'])
def check_docs(message):
    print(message)
    fileID = message.photo[-1].file_id
    file = bot.get_file(fileID)
    bot.send_media_group(message.chat.id, [types.InputMediaPhoto(file.file_id, caption=file.file_size)])
    sql_lite_db.add_values(parse_response(message))



while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)  # или просто print(e) если у вас логгера нет,
        # или import traceback; traceback.print_exc() для печати полной инфы
        time.sleep(15)
