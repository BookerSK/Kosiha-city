from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import timedelta, date
from Commander import game_create, ld_citizen
from CONSTANTS import USER_ACTION
from translator import translate as tr
from City import City

from random import randint

import pandas as pd
import re
import datetime
import os



storage = MemoryStorage()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)


class FSM_Creature_Char(StatesGroup):
    '''Машина состояний при создании персонажа'''
    name = State()
    happy_birthday = State()
    gender = State()


class FSM_Action(StatesGroup):
    '''Машина состояний для действия'''
    action = State()


class FSM_City_Stat(StatesGroup):
    '''Машина состояний для выбора статистики'''
    choice_stat = State()


def start_button1():
    '''Кнопка создать персонажа при первом заходе'''
    b_text = KeyboardButton('/Создать_персонажа')
    kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    return kb_start.add(b_text)


def start_button2():
    '''Кпонки старта после создания персонажа'''
    b1 = KeyboardButton('/Задать_действия')
    b2 = KeyboardButton('/Узнать_статус_персонажа')
    b3 = KeyboardButton('/Вчерашние_действия')
    b4 = KeyboardButton('/Посмотреть_статистики_города')
    kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    return kb_start.row(b1, b2, b3, b4)


def action_button(work_status=False, drink=False, spa=False, ii=True):
    buttons = []
    buttons.append(KeyboardButton('/Отдыхать'))
    buttons.append(KeyboardButton('/Сходить_к_доктору'))
    buttons.append(KeyboardButton('/Назад'))
    if work_status:
        buttons.append(KeyboardButton('/Идти_работать'))
    else:
        buttons.append(KeyboardButton('/Искать_работу'))
    if drink:
        buttons.append(KeyboardButton('/Напиться'))
    if spa:
        buttons.append(KeyboardButton('/Сходить_в_СПА'))
    if not ii:
        buttons.append(KeyboardButton('/Вернуть_контроль_ИИ'))
    kb_action = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in buttons:
        kb_action.insert(i)
    return kb_action


def city_stat_button():
    b1 = KeyboardButton('/Население')
    b2 = KeyboardButton('/Назад')
    kb_city_stat = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    return kb_city_stat.row(b1, b2)


def export_citizen_from_dir(id):
    for i in os.listdir(os.getcwd() + '\citizens'):
        if City.extract_id_hb_name_gender(i, only_id=True) == id:
            return ld_citizen(str(i))


def db_create():
    '''Создание папок и базы данных, если они не существуют'''
    if not os.path.exists('real_players'):
        os.mkdir("real_players")
        print("The folder 'real_players' doesn't exist, so I created it")
    if not os.path.exists('real_players\\real_players_ids.csv'):
        empty_df = pd.DataFrame(columns=['id', 'tg_id'])
        empty_df.to_csv('real_players\\real_players_ids.csv', index_label="Index", sep=';')
        print("The file 'real_players_ids.csv' doesn't exist, so I created it")
    if not os.path.exists('real_players\\notification.csv'):
        empty_df = pd.DataFrame(columns=['tg_id', 'type'])
        empty_df.to_csv('real_players\\notification.csv', index_label="Index", sep=';')
        print("The file 'notification.csv' doesn't exist, so I created it")
    if not os.path.exists('activity\\activities.csv'):
        empty_df = pd.DataFrame(columns=['id', 'to_do', 'Date'])
        empty_df.to_csv('activity\\activities.csv', index_label="Index", sep=';')
        print("The file 'activities.csv' doesn't exist, so I created it")


async def on_startup(_):
    '''Функция выводит, что бот вышел в онлайн'''
    print('Бот вышел в онлайн')


def exist_check_yes(message):
    exist_alive = pd.read_csv('real_players\\real_players_ids.csv', index_col='Index', sep=';')
    exist_alive = exist_alive[exist_alive['tg_id'] == int(message.from_user.id)]
    return len(exist_alive) > 0 and any(exist_alive['alive'].values)

def exist_check_no(message):
    exist_alive = pd.read_csv('real_players\\real_players_ids.csv', index_col='Index', sep=';')
    exist_alive = exist_alive[exist_alive['tg_id'] == int(message.from_user.id)]
    return len(exist_alive) == 0 or not any(exist_alive['alive'].values)


@dp.message_handler(lambda message: int(message.from_user.id) in
                                    pd.read_csv('real_players\\notification.csv', index_col='Index', sep=';')[
                                        'tg_id'].values)
async def notification_death(message: types.Message, state: FSMContext):
    text_notification = '''
К сожалению, ваш персонаж скончался. 
В данной игре, как и в жизни, ничто 
не убережет вашего персонажа от печального 
конца. Каждый день есть вероятность его 
смерти, которая зависит от здоровья, 
счастья, социального статуса и других 
характеристик.
Создайте нового персонажа, чтобы
продолжить игру'''
    delete_notification = pd.read_csv('real_players\\notification.csv', index_col='Index', sep=';')
    delete_notification = delete_notification.drop(
        delete_notification[delete_notification['tg_id'] == int(message.from_user.id)].index)
    delete_notification.to_csv('real_players\\notification.csv', index_label="Index", sep=';')
    await bot.send_message(message.from_user.id, text_notification, reply_markup=start_button1())
    await state.finish()


@dp.message_handler(exist_check_no, commands=['start'])
async def command_start(message: types.Message):
    '''1 вариант функции старта, если человек ещё не создал персонажа.
    Здесь происходит проверка, есть ли message.from_user.id в файле
    'real_players\\real_players_ids.csv' в колонке tg_id. Если нет,
    то выводится команда создать персонажа'''
    introduction1 = """
Добро пожаловать в игру 'Город Косиха'!
В данной игре вы можете создать персонажа,
задать/изменить его ежедневные действия,
либо отдать управление ИИ. Персонаж будет
жить в городе, жители которого также
весело проводят время.
Вы сможете посмотреть различные 
статистические данные по городу. Например,
население, уровень безработицы, смертность,
благосостояние и тому подобное. При желании
вы сможете узнать, что делал персонаж в
определенную дату.
Жанр игры можно определить как 
Zero Player Game - т.е. игра, которая по
большей части играет саму в себя. Игроку лишь
предстоит наблюдать сверху за развитием города
и (при желании) своего персонажа.     
"""
    introduction2 = '''
Для начала впишем вас в историю города,
давайте создадим персонажа!'''
    await bot.send_message(message.from_user.id, introduction1)
    await bot.send_message(message.from_user.id, introduction2, reply_markup=start_button1())
    actual_button = start_button1()


@dp.message_handler(exist_check_yes, commands=['start'])
async def command_start(message: types.Message):
    '''2 вариант функции старта, если человек ещё не создал персонажа.
    Здесь происходит проверка, есть ли message.from_user.id в файле
    'real_players\\real_players_ids.csv' в колонке tg_id. Если да,
    то выводится команда задать действия персонажа или перейти к статистике
    города'''
    introduction1 = """
Добро пожаловать в игру 'Город Косиха'!
В данной игре вы можете создать персонажа,
задать/изменить его ежедневные действия,
либо отдать управление ИИ. Персонаж будет
жить в городе, жители которого также
весело проводят время.
Вы сможете посмотреть различные 
статистические данные по городу. Например,
население, уровень безработицы, смертность,
благосостояние и тому подобное. При желании
вы сможете узнать, что делал персонаж в
определенную дату.
Жанр игры можно определить как 
Zero Player Game - т.е. игра, которая по
большей части играет саму в себя. Игроку лишь
предстоит наблюдать сверху за развитием города
и (при желании) своего персонажа.     
"""
    introduction2 = '''
    Задайте действия для вашего персонажа, узнайте его статус или перейдите к статистикам города'''
    await bot.send_message(message.from_user.id, introduction1)
    await bot.send_message(message.from_user.id, introduction2, reply_markup=start_button2())


@dp.message_handler(commands=['about'])
async def command_start(message: types.Message):
    introduction = """
Проект создан, как упражнение по Python
в использовании библиотек Pandas, Numpy,
aiogram, а также понимания принципов ООП.
Проект публикуется на Github по ссылке:
---
Текущая версия 0.1
Если вы заметите баги или ошибки, то пришлите
сообщение в ТГ https://t.me/rmyskin
или на почту rymyskin1992@gmail.com   
Автор идеи: Мыскин Роман Юрьевич
Лицензия:
Creative Commons Zero v1.0 
Universal 
"""
    await bot.send_message(message.from_user.id, introduction)


@dp.message_handler(exist_check_no, commands=['Создать_персонажа'], state=None)
async def command_start(message: types.Message):
    await FSM_Creature_Char.name.set()
    await bot.send_message(message.from_user.id,
                           'Введите имя персонажа. До 16 символов, только латинские/только русские буквы без пробелов или спецсимволов. Первая буква заглавная')


@dp.message_handler(lambda message: not (len(str(message.text)) < 17 and (
        bool(re.fullmatch('[A-Z][a-z]*', str(message.text))) or bool(re.fullmatch('[А-ЯЁ][а-яё]*', str(message.text))))),
                    state=FSM_Creature_Char.name)
async def check_name(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Некорректно. До 16 символов, только латинские/только русские буквы без пробелов или спецсимволов. Первая буква заглавная. Например, "Иван"')


@dp.message_handler(state=FSM_Creature_Char.name)
async def enter_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSM_Creature_Char.next()
    await bot.send_message(message.from_user.id,
                           'Введите день рождения персонажа в формате ДД.ММ.ГГГГ. Доступные дни рождения между {} и {}. Например, {}'.format(
                               (datetime.datetime.today() - datetime.timedelta(days=365 * 60)).strftime('%d.%m.%Y'),
                               (datetime.datetime.today() - datetime.timedelta(days=365 * 18)).strftime('%d.%m.%Y'),
                               (datetime.datetime.today() - datetime.timedelta(days=365 * 25)).strftime('%d.%m.%Y')))


@dp.message_handler(lambda message: not bool(re.fullmatch('\d\d.\d\d.\d{4}', str(message.text))) or not
datetime.datetime.today() - datetime.timedelta(days=365 * 60 + 1) <=
datetime.datetime.strptime(str(message.text), '%d.%m.%Y') <=
datetime.datetime.today() - datetime.timedelta(days=365 * 18 - 1),
                    state=FSM_Creature_Char.happy_birthday)
async def check_hb(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Некорректно. Введите дату в формате ДД.ММ.ГГГГ. Доступные дни рождения между {} и {}. Например, {}'.format(
                               (datetime.datetime.today() - datetime.timedelta(days=365 * 60)).strftime('%d.%m.%Y'),
                               (datetime.datetime.today() - datetime.timedelta(days=365 * 18)).strftime('%d.%m.%Y'),
                               (datetime.datetime.today() - datetime.timedelta(days=365 * randint(18, 60))).strftime(
                                   '%d.%m.%Y')))


@dp.message_handler(state=FSM_Creature_Char.happy_birthday)
async def enter_hb(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['happy_birthday'] = message.text
    await FSM_Creature_Char.next()
    await bot.send_message(message.from_user.id,
                           'Введите пол персонажа: м - мужской, ж - женский')


@dp.message_handler(lambda message: not message.text in ['м', 'ж', 'мужской', 'женский', 'm', 'w'],
                    state=FSM_Creature_Char.gender)
async def check_gender(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Некорректно. Либо букву м/ж, либо пол "мужской", "женский".')


@dp.message_handler(state=FSM_Creature_Char.gender)
async def enter_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text
    async with state.proxy() as data:
        id_save = game_create(name=data['name'], happy_birthday=data['happy_birthday'], gender=data['gender'], tg=True,
                              lang='rus')
        df_tg_id = pd.DataFrame({'id': [id_save], 'tg_id': [message.from_user.id], 'alive': ['True']})
        df_old_tg_id = pd.read_csv('real_players\\real_players_ids.csv', index_col='Index', sep=';')
        df_tg_id = pd.concat([df_old_tg_id, df_tg_id], ignore_index=True)
        df_tg_id.to_csv('real_players\\real_players_ids.csv', index_label="Index", sep=';')
    await state.finish()
    introduction2 = '''
Поздравляем! Ваш персонаж переехал в город "Косиха".
Задайте действия для вашего персонажа, узнайте его статус или перейдите к статистикам города.
Сегодня ваш персонаж был занят переездом, поэтому первое действие он совершит завтра.'''
    await bot.send_message(message.from_user.id, introduction2, reply_markup=start_button2())


@dp.message_handler(exist_check_yes, commands=['Узнать_статус_персонажа'])
async def command_stat_char(message: types.Message):
    read_csv = pd.read_csv('real_players\\real_players_ids.csv', index_col='Index', sep=';')
    id = read_csv[read_csv['tg_id'] == message.from_user.id]
    id = int(id['id'].values[-1])
    load_citizen = export_citizen_from_dir(id=id)
    if load_citizen.work_status:
        wk_st = 'есть работа'
    else:
        wk_st = 'нет работы'
    status = '''Меня зовут {}. Я {}, мне {} лет. Моё настроение - {}. Я в социальном слое {}. Моё здоровье - {}. У меня {} рублей. У меня {}'''.format(
        load_citizen.name, tr(load_citizen.gender), load_citizen.age, tr(load_citizen.mood_status),
        tr(load_citizen.social_status), tr(load_citizen.health), round(load_citizen.money), wk_st)
    await bot.send_message(message.from_user.id, status)
    await bot.send_message(message.from_user.id,
                           'Задайте действия для вашего персонажа, узнайте его статус или перейдите к статистикам города',
                           reply_markup=start_button2())


@dp.message_handler(exist_check_yes, commands=['Вчерашние_действия'])
async def command_stat_yesterday(message: types.Message):
    read_csv = pd.read_csv('real_players\\real_players_ids.csv', index_col='Index', sep=';')
    id = read_csv[read_csv['tg_id'] == message.from_user.id]
    id = int(id['id'].values[-1])
    for i in os.listdir(os.getcwd() + '\citizens'):
        if City.extract_id_hb_name_gender(i, only_id=True) == id:
            read_csv = pd.read_csv(os.getcwd() + '\citizens\\' + i, parse_dates=['Date'], dayfirst=False,
                                   index_col='Index', sep=';')
            answer = read_csv[read_csv['Date'] == pd.Timestamp(date.today() - timedelta(days=1))]
            if len(answer) > 0:
                answer = answer['Commentary'].values[0]
            else:
                answer = 'Ваш персонаж ещё не переехал в "Косиху"!'
            await bot.send_message(message.from_user.id, answer)
            await bot.send_message(message.from_user.id,
                                   'Задайте действия для вашего персонажа, узнайте его статус или перейдите к статистикам города',
                                   reply_markup=start_button2())
            break


@dp.message_handler(exist_check_yes, commands=['Посмотреть_статистики_города'])
async def command_city_stat(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Выберите интересующую статистику',
                           reply_markup=city_stat_button())
    await FSM_City_Stat.choice_stat.set()


@dp.message_handler(commands=['Население'], state=FSM_City_Stat.choice_stat)
async def command_city_population(message: types.Message, state: FSMContext):
    for i in os.listdir(os.getcwd() + '\city_statistic'):
        if i[:2] == 'id':
            df_id_card = pd.read_csv(os.getcwd() + '\city_statistic\\' + i, index_col='Index', sep=';')
            break
    answer = 'Всего было жителей в городе "Косиха": {}\nСейчас население {}\nВсего погибло жителей {}'.format(
        df_id_card['alive'].count(), df_id_card['alive'][df_id_card['alive'] == True].count(),
        df_id_card['alive'][df_id_card['alive'] == False].count())
    await bot.send_message(message.from_user.id,
                           answer)
    await bot.send_message(message.from_user.id,
                           'Задайте действия для вашего персонажа, узнайте его статус или перейдите к статистикам города',
                           reply_markup=start_button2())
    await state.finish()


@dp.message_handler(commands=['Назад'], state=FSM_City_Stat.choice_stat)
async def command_city_population(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
                           'Задайте действия для вашего персонажа, узнайте его статус или перейдите к статистикам города',
                           reply_markup=start_button2())
    await state.finish()


@dp.message_handler(state=FSM_City_Stat.choice_stat)
async def command_nothing_happend(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
                           'Ничего не произошло')
    await bot.send_message(message.from_user.id,
                           'Выберите интересующую статистику',
                           reply_markup=city_stat_button())



@dp.message_handler(exist_check_yes, commands=['Задать_действия'])
async def command_action(message: types.Message):
    read_csv = pd.read_csv('real_players\\real_players_ids.csv', index_col='Index', sep=';')
    id = read_csv[read_csv['tg_id'] == message.from_user.id]
    id = int(id['id'].values[-1])
    load_citizen = export_citizen_from_dir(id=id)
    action_text = ''
    ii_bool = not id in pd.read_csv('activity\\activities.csv', index_col='Index', sep=';')['id'].values
    if not ii_bool:
        action_text = '''Сейчас ваш персонаж планирует:\n'''
        to_do = pd.read_csv('activity\\activities.csv', index_col='Index', sep=';')
        to_do = to_do[to_do['id'] == id]
        to_do = to_do['to_do'].values[-1]
        action_text += str(to_do)
    action_text += '''Ваш персонаж может:'''
    await FSM_Action.action.set()
    await bot.send_message(message.from_user.id, action_text,
                           reply_markup=action_button(work_status=load_citizen.work_status,
                                                      drink=load_citizen.money > 1000,
                                                      spa=load_citizen.money > 3500,
                                                      ii=ii_bool))


@dp.message_handler(commands=['Назад'], state=FSM_Action.action)
async def command_action_return(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
                           'Задайте действия для вашего персонажа, узнайте его статус или перейдите к статистикам города',
                           reply_markup=start_button2())
    await state.finish()


@dp.message_handler(
    commands=['Отдыхать', 'Сходить_к_доктору', 'Идти_работать', 'Искать_работу', 'Напиться', 'Сходить_в_СПА',
              'Вернуть_контроль_ИИ'], state=FSM_Action.action)
async def command_action_save(message: types.Message, state: FSMContext):
    read_csv = pd.read_csv('real_players\\real_players_ids.csv', index_col='Index', sep=';')
    id = read_csv[read_csv['tg_id'] == message.from_user.id]
    id = int(id['id'].values[-1])
    load_citizen = export_citizen_from_dir(id=id)
    ii_bool = not id in pd.read_csv('activity\\activities.csv', index_col='Index', sep=';')['id'].values
    if message.text == '/Идти_работать' and not load_citizen.work_status:
        await bot.send_message(message.from_user.id,
                               'Вы безработный! Если нужна работа, введите команду "Искать_работу"',
                               reply_markup=action_button(work_status=load_citizen.work_status,
                                                          drink=load_citizen.money >= 1000,
                                                          spa=load_citizen.money >= 3500,
                                                          ii=ii_bool))
    elif message.text == '/Искать_работу' and load_citizen.work_status:
        await bot.send_message(message.from_user.id,
                               'Вы уже трудоустроены',
                               reply_markup=action_button(work_status=load_citizen.work_status,
                                                          drink=load_citizen.money >= 1000,
                                                          spa=load_citizen.money >= 3500,
                                                          ii=ii_bool))
    elif message.text == '/Напиться' and load_citizen.money < 1000:
        await bot.send_message(message.from_user.id,
                               'У вас нет денег, чтобы напиться',
                               reply_markup=action_button(work_status=load_citizen.work_status,
                                                          drink=load_citizen.money >= 1000,
                                                          spa=load_citizen.money >= 3500,
                                                          ii=ii_bool))
    elif message.text == '/Сходить_в_СПА' and load_citizen.money < 3500:
        await bot.send_message(message.from_user.id,
                               'У вас нет денег, чтобы сходить в СПА',
                               reply_markup=action_button(work_status=load_citizen.work_status,
                                                          drink=load_citizen.money >= 1000,
                                                          spa=load_citizen.money >= 3500,
                                                          ii=ii_bool))
    else:
        await bot.send_message(message.from_user.id,
                               'Отлично! О результатах сегодняшней деятельности персонажа вы узнаете завтра, введя команду "Вчерашние_действия". Учтите, что персонаж будет повторять действие каждый день до тех пор, пока вы не зададите другое действие, либо передадите контроль ИИ.')
        await bot.send_message(message.from_user.id,
                               'Задайте действия для вашего персонажа, узнайте его статус или перейдите к статистикам города',
                               reply_markup=start_button2())
        if message.text != "/Вернуть_контроль_ИИ":
            activity = USER_ACTION[message.text]
        else:
            activity = None
        df_activity = pd.DataFrame({'id': [id], 'to_do': [activity], 'Date': [datetime.date.today()]})
        if os.path.exists('activity\\activities.csv'):
            df_old_activity = pd.read_csv('activity\\activities.csv', parse_dates=['Date'], dayfirst=False,
                                          index_col='Index', sep=';')
            if id in df_old_activity['id'].values:
                df_old_activity = df_old_activity.drop(df_old_activity[df_old_activity['id'] == id].index)
            if message.text != "/Вернуть_контроль_ИИ":
                df_activity = pd.concat([df_old_activity, df_activity], ignore_index=True)
            else:
                df_activity = df_old_activity
        df_activity.to_csv('activity\\activities.csv', index_label="Index", sep=';')
        await state.finish()


@dp.message_handler(state=FSM_Action.action)
async def command_action_nothing_happend(message: types.Message, state: FSMContext):
    read_csv = pd.read_csv('real_players\\real_players_ids.csv', index_col='Index', sep=';')
    id = read_csv[read_csv['tg_id'] == message.from_user.id]
    id = int(id['id'].values[-1])
    load_citizen = export_citizen_from_dir(id=id)
    ii_bool = not id in pd.read_csv('activity\\activities.csv', index_col='Index', sep=';')['id'].values
    await bot.send_message(message.from_user.id, 'Ничего не произошло!')
    await bot.send_message(message.from_user.id, 'Введите одну из команд в подсказке',
                           reply_markup=action_button(work_status=load_citizen.work_status,
                                                      drink=load_citizen.money > 1000,
                                                      spa=load_citizen.money > 3500,
                                                      ii=ii_bool))


@dp.message_handler(exist_check_yes, state="*")
async def nothing_happend(message: types.Message):
    await bot.send_message(message.from_user.id, 'Ничего не произошло!')
    await bot.send_message(message.from_user.id, 'Введите одну из команд в подсказке', reply_markup=start_button2())


@dp.message_handler(exist_check_no, state="*")
async def nothing_happend(message: types.Message):
    await bot.send_message(message.from_user.id, 'Ничего не произошло!')
    await bot.send_message(message.from_user.id, 'Введите одну из команд в подсказке', reply_markup=start_button1())


db_create()
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
