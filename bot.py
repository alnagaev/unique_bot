import telebot
from telebot import apihelper
from telebot import types

import config
import dbworker
from pathlib import Path
from images import *
import time
import json

api_key = '909674394:AAFBBZaj84E6gkg6pJljbCJKjws9maUdWzU'
bot = telebot.TeleBot(api_key)

proxy_dict = {'basic_auth': ('sergeychuvakin1_mail', '44f869ef05'), 'proxy_ip': '5.182.118.50:30001'}

apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}


def json_add(key, value):
    try:
        with open("group_dict.json", 'r') as f:
            try:
                obj = json.load(f)
                obj['chats'][key] = value
            except ValueError:
                obj = dict()
                obj['chats'] = {}
                obj['chats'][key] = value

            with open("group_dict.json", "w") as write_file:
                json.dump(obj, write_file)

    except FileNotFoundError:
        with open("group_dict.json", "w") as write_file:
            obj = dict()
            obj['chats'] = {}
            obj['chats'][key] = value
            json.dump(obj, write_file)


def json_key(key):
    with open('group_dict.json', 'r') as read_file:
        data = json.load(read_file)
        return data['chats'][key]


def show_keys():
    with open('group_dict.json', 'r') as read_file:
        data = json.load(read_file)
        return data['chats'].keys()


def render_keyboard(keys):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*[types.InlineKeyboardButton(name, callback_data=name) for name in keys])
    return keyboard


# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.send_message(message.chat.id, "Я обладаю коллекциями следующих фотокарточек: ")
    keyboard = render_keyboard(show_keys())
    bot.send_message(message.chat.id, 'Выберите в меню что вам интересно!',
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Вот мои коллекции: ")
    keyboard = render_keyboard(show_keys())
    bot.send_message(message.chat.id, 'Выберите в меню что вам интересно!',
                     reply_markup=keyboard)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_NAME.value)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id, "Доставляю")
    try:
        photos = get_unique('images', json_key(call.data))
        for i in photos:
            bot.send_photo(call.id, i)
    except Exception as e:
        print(e)
        print(os.getcwd())
        bot.send_message(call.id, 'Что-то пошло не так')


@bot.message_handler(content_types=['text'])
def send_memes(message):
    if message.text.lower() == 'here':
        try:
            if str(message.chat.id) in os.listdir('images'):
                photos = get_unique('images', str(message.chat.id))
                for i in photos:
                    bot.send_photo(message.chat.id, i)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, 'Такого каталога нет')

    if message.text.startswith('here '):
        if message.text.split(' ')[0] == 'here' and message.text.split(' ')[1].startswith('-'):
            try:
                photos = get_unique('images', message.text.split(' ')[1])
                for i in photos:
                    bot.send_photo(message.chat.id, i)
            except Exception as e:
                print(e)
                print(os.getcwd())
                bot.send_message(message.chat.id, 'Что-то пошло не так')


@bot.message_handler(content_types=['text'])
def send_text(message):
    print(message)
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет, мой создатель')
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Прощай, создатель')


@bot.message_handler(content_types=['photo'])
def check_document(message):
    if message.chat.type == 'group':
        name = str(message.chat.id)  # Задумка была другая. Прости, Юра, мы все проебали
        json_add(message.chat.title, name)
    else:
        name = str(message.chat.id)
        json_add(name, name)
    if os.path.basename(os.getcwd()) != 'unique_bot':
        os.chdir('..')
    Path("./images/{}".format(name)).mkdir(parents=True, exist_ok=True)
    print(message)
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    file = bot.get_file(fileID)
    if '{}.jpg'.format(fileID) not in os.listdir('images/{}'.format(name)):
        downloaded_file = bot.download_file(file.file_path)

        with open('images/{}/{}.jpg'.format(name, fileID), 'xb') as new_file:
            try:
                new_file.write(downloaded_file)
            except Exception as e:
                print(str(e))
    else:
        print('already in directory')
    bot.send_message(message.chat.id, 'smells like photo')


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)  # или просто print(e) если у вас логгера нет,
        # или import traceback; traceback.print_exc() для печати полной инфы
        time.sleep(15)
