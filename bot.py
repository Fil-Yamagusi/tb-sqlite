#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""2024-01-03 Fil - Future code Yandex.Practicum
Исопльзование БД sqlite
Игра про составление слов из длинного слова с рейтингом

@word_constructor_bot
https://t.me/word_constructor_bot
6686217075:AAFVjbHnt5ABTwnazkid4jyP19UvVxgNKhk
"""

__version__ = '0.1'
__author__ = 'Fil Yamagusi'

# import re
from time import sleep, time, strftime
from random import shuffle, seed

from telebot import TeleBot
from telebot import types
from telebot.types import Message

from config import TOKEN
# Случайная случайность для выдачи заданного слова
seed(time())

bot_name = "word_constructor_bot"
bot = TeleBot(TOKEN)

# Быстрая работа с пользователями. Возможно, не пригодится
users = {}


def check_user(uid):
    if uid not in users:
        users[uid] = {
        }
    print(users)


# Пустое меню, пригодится в конце анкеты.
hideKeyboard = types.ReplyKeyboardRemove()

# Синонимы пункта Справка (помощь и т.п.)
menu_help = ['Помощь', 'Справка', 'Описание',]

# Стартовое меню, пригодится в конце анкеты.
menu_main = {
    'add_word': 'Придумал слово!',
    'change_task': 'Изменить задание',
    'stat': 'Статистика',
    'help': menu_help[0],
}

keyboard_main = types.ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True
)
keyboard_main.add(* menu_main.values())


@bot.message_handler(commands=['start'])
def handle_start(m: Message):
    """Приветствие, первое задание"""
    uid = str(m.from_user.id)
    check_user(uid)
    bot.send_message(
        m.from_user.id,
        f"<b>Отличная разминка для ума, {m.from_user.first_name}!</b>\n\n"
        "Составь из букв заданного слова много других. "
        "Например, из слова <b>КАРАТЕ</b> можно составить слова "
        "<i>река</i>, <i>карат</i>, <i>трак</i>,... \n\n"
        "Правила простые:\n"
        "- Имя существительное, длиннее 2 букв, в ед.числе (если есть)\n"
        "- Слово должно быть в <a href='https://gramota.ru/biblioteka/slovari/"
        "russkij-orfograficheskij-slovar'>Русском "
        "орфографическом словаре</a>\n"
        "- и &lt;&gt; й, е &lt;&gt; ё, ь &lt;&gt; ъ\n\n"
        "Подробнее - в справке /help",

        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=keyboard_main
    )


@bot.message_handler(
    content_types=["text"],
    func=lambda m: m.text in menu_help)
@bot.message_handler(commands=['help'])
def handle_help(m: Message):
    """Чуть более подробная справка"""
    bot.send_message(
        m.from_user.id,
        f"<b>Составь из букв заданного слова много других.</b>\n\n"
        "У этой игры разные названия: Наборщик, Конструктор, Перебуква или "
        "даже Анаграмма (хотя обычно анаграмма означает другое).\n\n"
        "Например, из слова <b>КАРАТЕ</b> можно составить слова "
        "<i>река</i>, <i>карат</i>, <i>трак</i>,... \n\n"
        "Правила простые:\n"
        "- Имя существительное, длиннее 2 букв, в ед.числе (если есть)\n"
        "- Слово должно быть в <a href='https://gramota.ru/biblioteka/slovari/"
        "russkij-orfograficheskij-slovar'>Русском "
        "орфографическом словаре</a>\n"
        "- и &lt;&gt; й, е &lt;&gt; ё, ь &lt;&gt; ъ\n\n"
        "При входе в игру я задаю тебе случайное слово. Его можно поменять "
        "командой /change_task\n"
        "Жми команду /add_word или кнопку 'Придумал слово!', чтобы сохранить "
        "новое придуманное слово.\n\n"
        "Я записываю результаты всех игроков. Если интересно, смотри их "
        "в разделе 'Статистика' или командой /stat",

        parse_mode="HTML",
        reply_markup=keyboard_main
    )



print(strftime("%F %T"))
print(bot_name, TOKEN)
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as ex:
        print(ex)
        time.sleep(10)
