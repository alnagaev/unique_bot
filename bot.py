import telebot
from telebot import types, apihelper
import config
import sql_lite_db
import jsonpickle
import json
import logging
import logging.config
from time import sleep
import os
import subprocess

"""test  dev/prod """
from flask import Flask, request, abort
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app)
apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}

print(subprocess.check_output('echo $TOKEN', shell=True))


def get_ngrok_url(port):
    if 'ngrok' in os.listdir():
        with open(os.devnull, 'w') as pipe:
            subprocess.Popen(['./ngrok', 'http', str(port), '--host-header=site.local'], stdout=pipe, stderr=subprocess.STDOUT)
        out = subprocess.check_output('curl http://localhost:4040/api/tunnels | jq ".tunnels[0].public_url"',
                                      shell=True)
        return str(out.strip(), 'utf-8').replace('"', '')
    raise FileNotFoundError


WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')

if os.environ.get('MODE') == 'prod':
     API_TOKEN = os.environ.get('TOKEN')
     HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
     WEBHOOK_HOST = "https://{}.herokuapp.com/".format(HEROKU_APP_NAME)
else:
    API_TOKEN = config.api_key
    WEBHOOK_HOST = get_ngrok_url(WEBHOOK_PORT)


WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
#
WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)
""""""

logging.config.fileConfig('logging.conf')
logger = logging.getLogger("bot")

bot = telebot.TeleBot(API_TOKEN, threaded=False)


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'uniqpic bot test query'


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


def render_keyboard(keys):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*[types.InlineKeyboardButton(name, callback_data=name) for name in keys])
    return keyboard


def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]


@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.send_message(message.chat.id, "Я бот-коллекционер, который собирает фотокарточки из чатов. Введите /start и "
                                      " я вышлю вам только уникальные изображения из выбранного чата. "
                                      " Введите /mode для настройки режима выгрузки изображений: full or last, "
                                      "Команды работают только в личной беседе с ботом. Групповые чаты не место для "
                                      "спама "
                                      "Бот экспериментальный и его использование может привести к тому, что ваши данные"
                                      "окажутся не в тех руках. Будьте бдительны"
                                      "Работа бота может быть прекращена в любой момент на усмотрение его создателя")


# Начало диалога
@bot.message_handler(commands=["start"])
def cmd_start(message):
    logger.info('bot started')
    if message.chat.type != "private":
        logger.info('channel posting is forbidden')
        bot.reply_to(message, 'Я не спамлю группы. Обратитесь ко мне лично')
    else:
        keyboard = render_keyboard(sql_lite_db.get_chats())
        bot.send_message(message.chat.id, 'Выберите в меню группу, которая вам интересна',
                         reply_markup=keyboard)
        logger.info(message)
        if sql_lite_db.get_user_mode(message.chat.id) is None:
            sql_lite_db.set_user_mode(message.chat.id, 'last')
            logger.info(sql_lite_db.get_user_mode(message.chat.id), ' mode was set')


@bot.message_handler(commands=["mode"])
def mode_keyboard(message):
    logger.info('mode menu')
    if message.chat.type != "private":
        logger.info('channel posting is forbidden')
        bot.send_message(message.chat.id, 'Настройки режима недоступны в групповом чате')
    else:
        keyboard = render_keyboard(['full', 'last'])
        bot.send_message(message.chat.id, 'Выберите режим бота', reply_markup=keyboard)
        logger.info(message)


@bot.callback_query_handler(func=lambda call: call.data in ['full', 'last'])
def set_mode(call):
    logger.info(call.message.chat.id)
    sql_lite_db.set_user_mode(call.message.chat.id, call.data)
    logger.info('mode was set to: ', sql_lite_db.get_user_mode(call.message.chat.id))
    bot.send_message(call.message.chat.id,
                     'mode was set to: {}'.format(sql_lite_db.get_user_mode(call.message.chat.id)))


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id, "Доставляю")
    logger.info('uid is {}, name is {} '.format(call.message.chat.id, call.data))
    try:
        all_data = sql_lite_db.get_values(call.data, str(call.message.chat.id))
        logger.info(all_data)
        if len(all_data['photos']) > 2:
            try:
                bot.send_media_group(call.message.chat.id, (types.InputMediaPhoto(i) for i in all_data['photos']))
            except Exception as e:
                '''maybe make some regular for Bad Request or find another way'''
                chunks_ = chunks(all_data['photos'], 10)
                for chunk in chunks_:
                    bot.send_media_group(call.message.chat.id, (types.InputMediaPhoto(i) for i in chunk))
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
        sql_lite_db.session_add((call.message.chat.id, call.message.date))

    except Exception as e:
        logger.error(e)
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
    logger.info(message)
    row = parse_response(message)
    try:
        sql_lite_db.add_values(row)
    except Exception as e:
        bot.send_message(message.chat.id, 'Data not collected yet')
        logger.error(str(e))


# while True:
#     try:
#         bot.polling(none_stop=True)
#
#     except Exception as e:
#         logger.error(str(e))  # или просто print(e) если у вас логгера нет,
#         # или import traceback; traceback.print_exc() для печати полной инфы
#         time.sleep(15)

bot.remove_webhook()

sleep(0.1)
bot.set_webhook(url=WEBHOOK_HOST + WEBHOOK_URL_PATH)

if __name__ == '__main__':
    app.run(port=8443)