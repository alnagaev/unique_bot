# -*- coding: utf-8 -*-

from enum import Enum
from telebot import apihelper


apihelper.proxy = {'https': 'socks5h://geek:socks@t.geekclass.ru:7777'}

with open('token.txt', 'r') as f:
    try:
        api_key = f.read()
    except FileNotFoundError:
        pass


