# -*- coding: utf-8 -*-

from enum import Enum
from telebot import apihelper


db_file = "database.vdb"
apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}

with open('token.txt', 'r') as f:
    api_key = f.read()


class States(Enum):
    """
    Задел на масштабирование для хранения состояний
    """
    S_START = "0"  # Начало нового диалога
    S_ENTER_NAME = "1"
    S_ENTER_AGE = "2"
    S_SEND_PIC = "3"