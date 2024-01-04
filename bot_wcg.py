#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""2024-01-03 Fil - Future code Yandex.Practicum
Использование БД sqlite
Игра про составление слов из длинного слова с рейтингом

@word_constructor_bot
https://t.me/word_constructor_bot
6686217075:AAHCE3aTVf8mrZolI29Mlj88C5rgzGmInXE
"""

__version__ = '0.1'
__author__ = 'Firip Yamagusi'

# import re
from time import time, strftime
from random import seed, randint

from telebot import TeleBot
from telebot import types
from telebot.types import Message
import sqlite3

from config import TOKEN

# Случайная случайность для выдачи заданного слова
seed(time())

bot_name = "word_constructor_bot"
bot = TeleBot(TOKEN)

"""======================================================================"""
# Создаём подключение к базе данных (файл wcg.db будет создан)
# Устанавливаем соединение с БД.
db_conn = sqlite3.connect('wcg.db')
dbc = db_conn.cursor()

# Создаем таблицу Users
dbc.execute(
    'CREATE TABLE IF NOT EXISTS Users ('
    'id INTEGER PRIMARY KEY, '
    'username TEXT NOT NULL, '
    'email TEXT NOT NULL, '
    'age INTEGER'
    ')'
)

# dbc.execute('CREATE INDEX idx_email ON Users (email)')

# Добавляем нового пользователя
dbc.execute('INSERT INTO Users (username, email, age) '
            'VALUES (?, ?, ?)',
            ('John', 'newuser@example.com', randint(2, 93)))
dbc.execute('INSERT INTO Users (username, email, age) '
            'VALUES (?, ?, ?)',
            ('Jesus', 'admin@all.universe', randint(10, 33)))
dbc.execute('INSERT INTO Users (username, email, age) '
            'VALUES (?, ?, ?)',
            ("Judas", "priest@evangelion.religion", randint(12, 45)))

# Выбираем всех пользователей
dbc.execute('SELECT * FROM Users')
users = dbc.fetchall()

# Выводим результаты
for user in users:
    print(user)

print("delete...")
# dbc.execute('DELETE FROM Users WHERE username = "John"', ())
dbc.execute('DELETE FROM Users WHERE age > 60', ())

# Выбираем всех пользователей
dbc.execute('SELECT * FROM Users')
users = dbc.fetchall()

# Выводим результаты
for user in users:
    print(user)

# Выбираем и сортируем пользователей по возрасту по убыванию
dbc.execute('''
SELECT username, age, AVG(age)
FROM Users
GROUP BY age
HAVING AVG(age) > ?
ORDER BY age DESC
''', (22,))
results = dbc.fetchall()

for row in results:
    print(row)

# Находим пользователей с наибольшим возрастом
dbc.execute('''
SELECT username, age
FROM Users
WHERE age = (SELECT MAX(age) FROM Users)
''')
oldest_users = dbc.fetchall()

# Выводим результаты
for user in oldest_users:
    print(user, user[1])

# Сохраняем изменения и закрываем соединение
db_conn.commit()
db_conn.close()

"""======================================================================"""
# Ссылка на Русский орфографический словарь
r_dict = 'https://gramota.ru/biblioteka/slovari/russkij-orfograficheskij-slovar'

# Быстрая работа с пользователями. Возможно, не пригодится
users = {}


def check_user(uid):
    if uid not in users:
        users[uid] = {
        }
    print(users)


# Пустое меню, может пригодится
hideKeyboard = types.ReplyKeyboardRemove()

# Синонимы пункта Справка (помощь и т.п.)
menu_help = ['Помощь', 'Справка', 'Описание', ]

# Основное меню
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
keyboard_main.add(*menu_main.values())


@bot.message_handler(commands=['start'])
def handle_start(m: Message):
    """Приветствие, первое задание"""
    uid = str(m.from_user.id)
    check_user(uid)
    bot.send_message(
        m.from_user.id,
        f"<b>Отличная разминка для ума, {m.from_user.first_name}!</b>\n\n"
        "Составь из букв заданного слова много других слов.\n"
        "Например, из слова <b>КАРАТЕ</b> получатся "
        "<i>река</i>, <i>карат</i>, <i>трак</i>,... \n\n"
        "<b>Правила для новых слов простые</b>:\n"
        "- Имя существительное в ед.числе (если есть)\n"
        "- длиннее 2 букв\n"
        f"- Должно быть в <a href='{r_dict}'>Русском "
        "орфографическом словаре</a>\n"
        "- Буква 'и' - это не 'й'!, 'е' не 'ё', 'ь' не 'ъ'\n\n"
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
        f"<b>Составь из букв заданного слова другие слова!</b>\n\n"
        "У этой игры разные названия: Наборщик, Конструктор, Перебуква или "
        "даже Анаграмма (хотя обычно анаграмма означает другое).\n\n"
        "Например, из слова <b>КАРАТЕ</b> можно составить слова "
        "<i>река</i>, <i>карат</i>, <i>трак</i>, <i>тара</i>, "
        "<i>каре</i>, <i>карт</i>, <i>кета</i>, <i>теракт</i>\n\n"
        "<b>Правила для новых слов простые</b>:\n"
        "- Имя существительное в ед.числе (если есть)\n"
        "- длиннее 2 букв\n"
        f"- Должно быть в <a href='{r_dict}'>Русском "
        "орфографическом словаре</a>\n"
        "- Буква 'и' - это не 'й'!, 'е' не 'ё', 'ь' не 'ъ'\n\n"
        "При входе в игру я задаю тебе случайное слово-задание. "
        "Его можно поменять командой /change_task\n"
        "Жми команду /add_word или кнопку 'Придумал слово!', чтобы сохранить "
        "новое придуманное слово.\n\n"
        "Я записываю результаты всех игроков. Если интересно, смотри их "
        "в разделе 'Статистика' или командой /stat",

        parse_mode="HTML",
        reply_markup=keyboard_main
    )


print(strftime("%F %T"))
print(bot_name)
print(TOKEN)

bot.polling(none_stop=True)
