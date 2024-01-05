#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""2024-01-03 Fil - Future code Yandex.Practicum
Использование БД sqlite
Игра про составление слов из длинного слова с рейтингом

@word_constructor_bot
https://t.me/word_constructor_bot
6686217075:AAHCE3aTVf8mrZolI29Mlj88C5rgzGmInXE
"""

# XXX
"""
https://gramota.ru/poisk?query=%D0%B6%D0%B0%D1%80%D0%B3%D0%BE%D0%BD&mode=slovari
https://lexicography.online/explanatory/search?s=%D1%83%D0%BA%D0%BE%D1%81
https://lexicography.online/explanatory/%D1%81/%D1%81%D1%82%D0%B5%D0%BA%D0%BB%D0%BE
"""
# ХХХ
__version__ = '0.1'
__author__ = 'Firip Yamagusi'

# import re
from time import time, strftime, sleep
from random import seed, randint, shuffle
# для проверки новых слов в словаре
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

from telebot import TeleBot
from telebot import types
from telebot.types import Message, User
import sqlite3

from config import TOKEN
from task_word_list import task_words_list

bot_name = "word_constructor_bot"
print(strftime("%F %T"))
print(bot_name)
print(TOKEN)

bot = TeleBot(TOKEN)


# Для простого хранения некоторых данных, чтобы не бегать в БД.
users = {}
task_words = {}


# Создаём подключение к базе данных (файл wcg.db будет создан)
db_conn = sqlite3.connect('wcg.db', check_same_thread=False)
dbc = db_conn.cursor()


# Создаем таблицу Users
dbc.execute(
    'CREATE TABLE IF NOT EXISTS Users ('
#    'id INTEGER PRIMARY KEY, '
    'uid INTEGER PRIMARY KEY, '
    'first_time INTEGER, '
    'last_time INTEGER, '
    'task_word_id INTEGER'
    ')'
)

# Создаем таблицу слов-заданий, если ещё не было.
dbc.execute(
    'CREATE TABLE IF NOT EXISTS Task_words ('
    'id INTEGER PRIMARY KEY AUTOINCREMENT, '
    'task_word TEXT UNIQUE'
    ')'
)

# Создаем таблицу составленных слов, если ещё не было.
dbc.execute(
    'CREATE TABLE IF NOT EXISTS New_words ('
    'id INTEGER PRIMARY KEY AUTOINCREMENT, '
    'new_word TEXT UNIQUE'
    ')'
)

# Создаем таблицу составленных слов, если ещё не было.
dbc.execute(
    'CREATE TABLE IF NOT EXISTS bad_New_words ('
    'id INTEGER PRIMARY KEY AUTOINCREMENT, '
    'bad_new_word TEXT UNIQUE'
    ')'
)

# Создаем таблицу связей 'юзер-задание-слово', если ещё не было.
dbc.execute(
    'CREATE TABLE IF NOT EXISTS Users_to_New_words ('
    'uid INTEGER, '
    'task_word_id INTEGER, '
    'new_word_id INTEGER,'
    'PRIMARY KEY (uid, task_word_id, new_word_id)'
    ')'
)

db_conn.commit()


# функция проверки новых слов в интернет
def check_word_in_russian_dictionary(check_word: str) -> bool:
    """ Ищем русское слово и проверяем его в словаре """
    words = check_word.lower().split()
    check_result = False
    has_russian_word = False
    find_word = ""
    vowels = list('аяуюоёэеыи')

    # Отсекаем короткие или без гласных или некириллические
    for word in words:
        if len(word) < 4:
            continue
        if not any(char in vowels for char in word):
            continue
        if bool(re.fullmatch(r'(?i)[а-яё]+', word)):
            has_russian_word = True
            find_word = word
            break

    #  XXX тут проверка в таблице уже добавленных и проверенных слов.
    #  Тут проверка через словарь.
    # https://gramota.ru/poisk?query={0}&mode=slovari&dicts[]=71
    if has_russian_word:

        url = ("https://gramota.ru/poisk?query={0}&mode=slovari&dicts[]=50"
               .format(quote(find_word)))
        print(url)
        request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with (urlopen(request_site) as dict_site):
                webpage = dict_site.read().decode('utf-8')
                pattern = r'class="title uppercase">(.+)</a>'
                match = re.findall(pattern, webpage)
                print(match[0], match)

                # перешёл с орфографического на словарь только существительных
                # the_noun = '<div class="gram" id="gram">Существительное'
                # print(f"Помечено как существительное? {the_noun in webpage}")
                # if check_word == match[0] and the_noun in webpage:
                if check_word == match[0]:
                    check_result = True
        except Exception as ex:
            print(ex)

    return check_result

# Для модератора простой способ добавить слова-задания. Дубликаты не добавятся.
for tw in task_words_list:
    try:
        dbc.execute("INSERT INTO Task_words (task_word) "
                    "VALUES (?)", (tw,))
        lrid = dbc.lastrowid
        print(f"Слово '{tw}' добавлено в таблицу СЛОВ-ЗАДАНИЙ. ({lrid})")
    except sqlite3.IntegrityError:
        print(f"Слово '{tw}' уже есть в таблице СЛОВ-ЗАДАНИЙ.")

    for w in task_words_list[tw].split():
        try:
            dbc.execute('SELECT id '
                        'FROM New_words '
                        'WHERE new_word=? LIMIT 1', (w,))
            user_db = dbc.fetchone()
            if user_db is not None:
                print(f"Слово {w} уже в таблице НОВЫХ слов. Skip")
                continue

            dbc.execute('SELECT id '
                        'FROM bad_New_words '
                        'WHERE bad_new_word=? LIMIT 1', (w,))
            user_db = dbc.fetchone()
            if user_db is not None:
                print(f"Слово {w} уже в таблице ПЛОХИХИ НОВЫХ слов. Skip")
                continue

            if check_word_in_russian_dictionary(w):
                dbc.execute("INSERT INTO New_words (new_word) "
                            "VALUES (?)", (w,))
                lrid = dbc.lastrowid
                print(f"Слово '{w}' есть в словаре существительных. "
                      f"Добавляем в таблицу НОВЫХ слов. {lrid}")
                sleep(5)
            else:
                dbc.execute("INSERT INTO bad_New_words (bad_new_word) "
                            "VALUES (?)", (w,))
                lrid = dbc.lastrowid
                print(f"Слова '{w}' нет в словаре существительных. "
                      f"Добавляем в таблицу ПЛОХИХ НОВЫХ слов. {lrid}")
        except sqlite3.IntegrityError:
            print(f"Слово '{w}' уже есть в таблице НОВЫХ слов. Skip")

db_conn.commit()


# Как и users, храним слова-задания из БД в словаре
dbc.execute('SELECT id, task_word FROM Task_words ORDER BY id')
for tw in dbc.fetchall():
    task_words[tw[0]] = tw[1]
#print(task_words)


# Ссылка на Русский орфографический словарь
r_dict = ('https://gramota.ru/biblioteka/slovari/'
          'bolshoj-tolkovyj-slovar-russkikh-sushhestvitelnykh')

# Быстрая работа с пользователями. Возможно, не пригодится
users = {}

# Пустое меню, может пригодится
hideKeyboard = types.ReplyKeyboardRemove()

# Основное меню
menu_main = {
    'add_word': 'Придумал слово!',
    'change_task': 'Изменить задание',
    'stat': 'Статистика',
    'help': 'Помощь',
}

keyboard_main = types.ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True
)
keyboard_main.add(*menu_main.values())

# Основное меню
menu_yes_no = {
    'yes': 'Да',
    'no': 'Нет',
}

keyboard_yes_no = types.ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True
)
keyboard_yes_no.add(*menu_yes_no.values())


@bot.message_handler(commands=['start'])
def handle_start(m: Message):
    """Приветствие, регистрация, первое задание"""

    # Ищем пользователя. Если не нашли, то создаём и даём ему случайное задание
    uid = m.from_user.id
    if uid not in users:
        users[uid] = {}

    with sqlite3.connect('wcg.db') as db_conn:
        dbc = db_conn.cursor()
        dbc.execute('SELECT task_word_id '
                    'FROM Users '
                    'WHERE uid=? LIMIT 1', (uid,))
        user_db = dbc.fetchone()

        # Если пользователь существует в базе, то слово-задание оттуда.
        if user_db:
            users[uid]['task_word_id'] = user_db[0]
            users[uid]['task_word'] = task_words[user_db[0]]
            print(f"Пользователь {uid} НАЙДЕН. "
                  f"Задание для него: {users[uid]['task_word']}")
        # Иначе добавляем пользователя и выдаём случайное слово-задание.
        else:
            tw_rnd_id = randint(0, len(task_words) - 1)
            users[uid]['task_word_id'] = tw_rnd_id
            users[uid]['task_word'] = task_words[tw_rnd_id]
            now = int(time())
            dbc.execute("INSERT INTO Users "
                        "(uid, first_time, last_time, task_word_id) "
                        "VALUES (?, ?, ?, ?)",
                        (m.from_user.id, now, now, tw_rnd_id))
            print(f"Пользователь {uid} СОЗДАН. "
                  f"Задание для него: {users[uid]['task_word']}")
            db_conn.commit()

    bot.send_message(
        m.from_user.id,
        f"<b>Отличная разминка для ума, {m.from_user.first_name}!</b>\n\n"
        "Составь из букв заданного слова много других слов.\n"
        "Например, из слова <b>КАРАТЕ</b> получатся "
        "<i>река</i>, <i>карат</i>, <i>трак</i>,... \n\n"
        "<b>Правила для новых слов простые</b>:\n"
        "- Имя существительное в ед.числе (если есть)\n"
        "- длиннее 3 букв и без дефисов\n"
        f"- Должно быть в <a href='{r_dict}'>Большом толковом словаре "
        f"русских существительных</a>\n"
        "- Буква 'и' - это не 'й'!, 'е' не 'ё', 'ь' не 'ъ'\n\n"
        "Подробнее - в справке /help",

        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=keyboard_main
    )

    bot.send_message(
        m.from_user.id,
        f"Твоё слово-задание - <b>{users[uid]['task_word'].upper()}</b>\n"
        f"Придумал слово? - жми '{menu_main['add_word']}'",

        parse_mode="HTML",
        reply_markup=keyboard_main
    )


@bot.message_handler(
    content_types=["text"],
    func=lambda m: m.text == menu_main['add_word'])
@bot.message_handler(commands=['add_word'])
def handle_add_word(m: Message):
    """готовимся принять слово"""
    uid = m.from_user.id
    if uid not in users:
        bot.send_message(
            m.from_user.id,
            "<b>Странная ошибка</b>:\n"
            "или пользователь зашёл в игру без /start,\n"
            "или не получил слово-задание /change_task",

            parse_mode="HTML",
            reply_markup=keyboard_main
        )
        return

    bot.register_next_step_handler(m, add_word)
    bot.send_message(
        m.from_user.id,
        f"Твоё слово-задание: <b>{users[uid]['task_word'].upper()}</b>\n"
        f"Что получилось из него составить?\n",

        parse_mode="HTML",
        reply_markup=keyboard_main
    )


def add_word(m: Message):
    """Добавляем слово по правилам"""
    # Приходится обработать команды, если не к месту их нажали
    if m.text in [menu_main['add_word'], '/add_word']:
        bot.register_next_step_handler(m, add_word)
        bot.send_message(
            m.from_user.id,
            "<b>Так что же?</b>",

            parse_mode="HTML",
            reply_markup=keyboard_main
        )
        return
    if m.text in [menu_main['change_task'], '/change_task']:
        handle_change_task(m)
        return
    if m.text in [menu_main['stat'], '/stat']:
        handle_help(m)
        return
    if m.text in [menu_main['help'], '/help']:
        handle_help(m)
        return

    # Если при перезагрузке бота кто-то был в этом меню.
    uid = m.from_user.id
    if uid not in users:
        handle_start(m)
        return
    if 'task_word' not in users[uid]:
        handle_start(m)
        return

    # Уф, ну теперь вроде просто слово обрабатываем. Сначала правила:
    new_word = m.text.strip().lower()
    is_error = False
    error_msg = ""
    new_word_is_in_db = "Твоё новое слово"

    if new_word == users[uid]['task_word']:
        is_error = True
        error_msg += "🤡 Это же исходное заданное слово!\n"

    if len(new_word) < 4:
        is_error = True
        error_msg += "4️⃣ У нас по-взрослому: cлова не короче 4 букв.\n"

    if len(new_word) > len(users[uid]['task_word']):
        is_error = True
        error_msg += "🤥 Ваше слово слишком длинное.\n"

    if not all(new_word.count(x) <= users[uid]['task_word'].count(x)
       for x in new_word):
        is_error = True
        error_msg += "🔤 В заданном слове не хватает букв для вашего.\n"

    if is_error:
        bot.register_next_step_handler(m, add_word)
        bot.send_message(
            m.from_user.id,
            f"🛑 Нет, <b>{new_word}</b> не годится.\n"
            f"Слово-задание: <b>{users[uid]['task_word'].upper()}</b>\n"
            f"{error_msg}",

            parse_mode="HTML",
            reply_markup=keyboard_main
        )
    else:
        # Слово вроде хорошее.
        # Если оно есть в таблице New_words, то сразу одобряем.
        # Если нет, то проверяем в интернет-словаре.

        bot.register_next_step_handler(m, add_word)
        is_in_new_words = False
        with sqlite3.connect('wcg.db') as db_conn:
            dbc = db_conn.cursor()
            dbc.execute('SELECT id '
                        'FROM New_words '
                        'WHERE new_word=?', (new_word,))
            if dbc.fetchone() is not None:
                is_in_new_words = True

            if not is_in_new_words:
                print(f"{new_word} - приходится проверять в интернете")
                bot.send_message(
                    m.from_user.id,
                    f"⏳ Погоди, проверю слово в словаре...\n",
                )
                if not check_word_in_russian_dictionary(new_word):
                    bot.send_message(
                        m.from_user.id,
                        f"🛑 Нет, <b>{new_word}</b> не годится.\n"
                        f"Такого существительного нет в <a href='{r_dict}'>"
                        f"Большом толковом словаре русских существительных"
                        f"</a>. см. /help для подробностей.",

                        parse_mode="HTML",
                        disable_web_page_preview = True,
                        reply_markup=keyboard_main
                    )
                    return
                # Хорошее слово добавляем в таблицу New_words, чтобы
                # лишний раз не проверять в интернете.
                try:
                    dbc.execute("INSERT INTO New_words (new_word) "
                                "VALUES (?)", (new_word,))
                    db_conn.commit()
                    print(f"'{new_word}' добавлено в таблицу новых слов")
                except sqlite3.OperationalError:
                    print(f"'{new_word}' database is locked")
                    bot.send_message(
                        m.from_user.id,
                        f"🙏🏻 Извините, ошибка в программе.\n"
                        f"Попробуйте ещё раз добавить это слово.",
                    )
                except sqlite3.IntegrityError:
                    print(f"'{new_word}' уже есть в таблице новых слов")

            dbc.execute('SELECT id '
                        'FROM New_words '
                        'WHERE new_word=?', (new_word,))
            new_word_db = dbc.fetchone()
            try:
                dbc.execute("INSERT INTO Users_to_New_words "
                            "(uid, task_word_id, new_word_id) "
                            "VALUES (?, ?, ?)",
                            (uid, users[uid]['task_word_id'],
                             new_word_db[0],))
                db_conn.commit()
            except sqlite3.IntegrityError:
                print(f"Связь {uid}, {users[uid]['task_word_id']}, "
                      f"{new_word_db[0]} уже есть в таблице связей")
                new_word_is_in_db = "Слово (уже было)"

            dbc.execute('SELECT nw.new_word '
                        'FROM Users_to_New_words u2n '
                        'INNER JOIN New_words nw '
                        'ON nw.id = u2n.new_word_id '
                        'WHERE u2n.uid=? AND u2n.task_word_id=? ',
                        (uid, users[uid]['task_word_id']))
            all_new_words_db = [str(w[0]) for w in dbc.fetchall()]
            all_new_words = str(len(all_new_words_db)) + ": "
            all_new_words += ", ".join(sorted(all_new_words_db))

        bot.send_message(
            m.from_user.id,
            f"👍🏻 Неплохо, неплохо!\n"
            f"Слово-задание: <b>{users[uid]['task_word'].upper()}</b>\n"
            f"{new_word_is_in_db}: <b>{new_word}</b>\n\n"
            f"<b>{all_new_words}</b>",

            parse_mode="HTML",
            reply_markup=keyboard_main
        )


@bot.message_handler(
    content_types=["text"],
    func=lambda m: m.text == menu_main['change_task'])
@bot.message_handler(commands=['change_task'])
def handle_change_task(m: Message):
    """Запрос на замену слова-задания"""
    # Используйте /change_task N для установки слова-задания №N
    uid = m.from_user.id
    print(m.text)
    m_text_list = m.text.split()
    if len(m_text_list) == 2:
        print("Выбор задания явно, а не случайно")
        with (sqlite3.connect('wcg.db') as db_conn):
            dbc = db_conn.cursor()
            try:
                num = int(m_text_list[1])
                print(f"пробуем найти задание с id={num}")
                dbc.execute('SELECT id, task_word '
                            'FROM Task_words '
                            'WHERE id=? ', (num,))
                tw_db = dbc.fetchone()
                print(tw_db)
                if tw_db is not None:
                    print(f"Вроде нашли, пробуем переписать в БД и в users")
                    now = int(time())
                    dbc.execute("UPDATE Users "
                                "SET last_time=?, task_word_id=? "
                                "WHERE uid=?",
                                (now, tw_db[0], uid,)
                                )
                    db_conn.commit()
                    dbc.execute('SELECT * '
                                'FROM Users '
                                'WHERE uid=? ', (uid,))
                    users[uid]['task_word_id'] = tw_db[0]
                    users[uid]['task_word'] = tw_db[1]
                    print(users)

                    tw_db = dbc.fetchone()
                    print(tw_db)
                    handle_add_word(m)
                    return
            except Exception as e:
                print("Выбрано несуществующее слово. Выходим без изменений.")

    bot.register_next_step_handler(m, change_task)
    bot.send_message(
        m.from_user.id,
        f"<b>Точно меняем слово-задание?</b>\n\n"
        "Если 'Да', то твоя статистика сохранится, и ты получишь новое "
        "случайное задание.\n"
        "Кстати, нынешнее задание однажды снова тебе попадётся, и ты сможешь "
        "добавить новые слова из его букв!",

        parse_mode="HTML",
        reply_markup=keyboard_yes_no
    )


def change_task(m: Message):
    """Меняем задание по запросу пользователя"""
    if m.from_user.id not in users:
        handle_start(m)
        return
    if m.text not in menu_yes_no.values():
        handle_change_task(m)
        return

    if m.text == menu_yes_no['yes']:
        with (sqlite3.connect('wcg.db') as db_conn):
            uid = m.from_user.id
            dbc = db_conn.cursor()
            dbc.execute('SELECT id '
                        'FROM Task_words '
                        'WHERE id!=? '
                        'ORDER BY RANDOM() '
                        'LIMIT 1', (users[uid]['task_word_id'],))
            tw_db = dbc.fetchone()

            users[uid]['task_word_id'] = tw_db[0]
            users[uid]['task_word'] = task_words[tw_db[0]]
            now = int(time())
            dbc.execute("UPDATE Users "
                        "SET last_time=?, task_word_id=? "
                        "WHERE uid=?",
                        (now, tw_db[0], uid,)
                        )
            bot.register_next_step_handler(m, handle_add_word)
            bot.send_message(
                m.from_user.id,
                f"Новое слово-задание: "
                f"<b>{users[uid]['task_word'].upper()}</b>\n"
                # f"Давай составлять из него другие слова!"
                f"Придумал слово? - жми '{menu_main['add_word']}'",

                parse_mode="HTML",
                reply_markup=keyboard_main
            )

    if m.text == menu_yes_no['no']:
        bot.register_next_step_handler(m, handle_add_word)
        bot.send_message(
            m.from_user.id,
            f"Ок, продолжаем",

            parse_mode="HTML",
            reply_markup=keyboard_main
        )


@bot.message_handler(
    content_types=["text"],
    func=lambda m: m.text == menu_main['help'])
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
        "- длиннее 3 букв и без дефисов\n"
        f"- Должно быть в <a href='{r_dict}'>Большом толковом словаре "
        f"русских существительных</a> *\n"
        "- Буква 'и' - это не 'й'!, 'е' не 'ё', 'ь' не 'ъ'\n\n"
        "* Без ограничений игра наполнится всякой дичью типа <i>куконор</i>, "
        "<i>виссохан</i>, <i>простеки</i> и т.п.\n\n"
        "При входе в игру я задаю тебе случайное слово-задание. "
        "Его можно поменять командой /change_task\n"
        "Жми команду /add_word или кнопку 'Придумал слово!', чтобы сохранить "
        "новое придуманное слово.\n\n"
        "Я записываю результаты всех игроков. Если интересно, смотри их "
        "в разделе 'Статистика' или командой /stat",

        parse_mode="HTML",
        reply_markup=keyboard_main
    )


bot.polling(none_stop=True)
