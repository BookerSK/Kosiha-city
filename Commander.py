import datetime
import pandas as pd
import os
from CitizenActivity import CitizenActivity as RussiaCitizen
from City import City


def wide_pandas():
    """
    Меняет параметры отображения ДФ Пандаса для корректной работы с таблицей
    """
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('max_colwidth', None)
    pd.options.display.max_rows = 9999
    pd.set_option('max_colwidth', 80)


def ld_citizen(file_name: str):
    '''
    Входный параметр - это название файла в папке citizens в формате
    id_happybirthday_name_gender_alive.csv
    Затем проходит инициализация Class гражданина с двумя последовательно наследуемыми классами:
    инициализации и ежедневной активности
    с присвоением всех состояний последней записи
    '''
    read_file = pd.read_csv(os.getcwd() + '\citizens\\' + str(file_name), parse_dates=['Date'], dayfirst=False,
                            index_col='Index', sep=';')
    # столбец с датами переводится в формат datetime для корректной работы с жителем
    read_file['Date'] = pd.to_datetime(read_file['Date']).dt.date
    last_condition = read_file.iloc[len(read_file) - 1]
    _id, _happy_birthday, _name, _gender, _alive = City.extract_id_hb_name_gender(file_name)
    _day = last_condition[0] + datetime.timedelta(days=1)
    _health = last_condition[1]
    _mood_status = last_condition[2]
    _social_status = last_condition[3]
    _money = last_condition[4]
    _happiness = last_condition[5]
    _work_status = last_condition[6]
    _work_pass = last_condition[7]
    _work_experience = last_condition[8]
    _commentary = ""
    _dt_citizen = []
    for j in range(len(read_file)):
        _dt_citizen.append(list(read_file.iloc[j]))
    load_citizen = RussiaCitizen(_id, _happy_birthday, _name, _gender, _alive, _day, _health, _mood_status,
                                 _social_status, _money, _happiness, _work_status, _work_pass, _work_experience,
                                 _commentary, _dt_citizen, _randomize=False)
    return load_citizen


def create_activity_folder():
    if not os.path.exists('activity'):
        os.mkdir("activity")
        print("The folder 'activity' doesn't exist, so I created it")


def generate():
    """
    Функция запрашивает, сколько инициализировать человек, затем генерит логи запрошенное число раз каждый раз до тех
    пор пока челик не умрет, либо не наступит вчера
    """
    population = int(input('How many people do you want to generate: '))
    for k in range(1, population + 1):
        generate_citizen = RussiaCitizen(_data_citizen=[])
        while generate_citizen.alive and generate_citizen.day < datetime.date.today():
            generate_citizen.dayend()
        generate_citizen.save_story()


def refresh():
    """
    обновить список жителей. последовательно открывается каждый лог жителя. из имени файла извлекаются id, др, имя, пол, жив ли.
    по последней строчке определяется последнее состояние жителя. прибавляется день. конец дня повторяется до тех пор пока челик жив
    """
    for i in os.listdir(os.getcwd() + '\citizens'):
        load_citizen = ld_citizen(str(i))
        ADD_DAYS = 2
        while load_citizen.alive and load_citizen.day < datetime.date.today() + datetime.timedelta(days=ADD_DAYS):
            load_citizen.dayend()
        load_citizen.save_story()
    print('Refresh completed')


def game():
    print('Welcome to active mod in "Kosiha city"')
    print('Create - to make a new civilian')
    print('Сont - to continue')
    _string = input('Input: ')
    if _string.lower() == 'create':
        game_create()
    elif _string.lower() == 'cont':
        game_cont()
    else:
        print('Nothing happend')


def game_create(name=None, happy_birthday=None, gender=None, tg=False, lang='eng'):
    id = RussiaCitizen.max_id() + 1
    day = datetime.date.today()
    if not tg:
        name = input('Enter name of your character: ')
        happy_birthday = input("Enter your character's birthday in format DD.MM.YYYY (Example: 01.01.2022): ")
        gender = input('Enter your gender (m - man, w - woman):').lower()
    if lang == 'rus':
        if gender == 'м' or gender == 'мужской':
            gender = 'man'
        elif gender == 'ж' or gender == 'женский':
            gender = 'woman'
    if gender == 'm':
        gender = 'man'
    elif gender == 'w':
        gender = 'woman'
    happy_birthday = datetime.datetime.strptime(happy_birthday, '%d.%m.%Y').date()
    age = (day - happy_birthday).days // 365
    health = RussiaCitizen.age_health(age)
    happiness = 50
    social_status = RussiaCitizen.social_status_fun()
    money = RussiaCitizen.social_status_money(social_status)
    commentary = "Today was my first day in Kosiha. I settled in a new place"
    generate_citizen = RussiaCitizen(_id=id, _happy_birthday=happy_birthday, _name=name, _gender=gender,
                                     _day=datetime.date.today(), _health=health, _social_status=social_status,
                                     _money=money, _happiness=happiness, _randomize=False, _commentary=commentary,
                                     _data_citizen=[])
    generate_citizen.data_citizen.append(generate_citizen.add_str())
    generate_citizen.save_story()
    if not tg:
        print(generate_citizen)
        print(generate_citizen.commentary)
    if tg:
        return id


def game_cont():
    id = int(input('Enter id your character: '))
    for i in os.listdir(os.getcwd() + '\citizens'):
        if City.extract_id_hb_name_gender(i, only_id=True) == id:
            load_citizen = ld_citizen(str(i))
            print('What is you character going to do tomorrow?')
            if load_citizen.work_status:
                print('0 - Go to work')
            else:
                print('0 - Find job')
            print('1 - Relax')
            if load_citizen.money > 1000:
                print('2 - Drink')
            print('3 - Seeing a doctor')
            if load_citizen.money > 3500:
                print('4 - Go to SPA')
            print('I - return control to II')
            activity = input('Input: ')
            df_activity = pd.DataFrame({'id': [id], 'to_do': [activity], 'Date': [datetime.date.today()]})
            if os.path.exists('activity\\activities.csv'):
                df_old_activity = pd.read_csv('activity\\activities.csv', parse_dates=['Date'], dayfirst=False,
                                              index_col='Index', sep=';')
                if len(df_old_activity['id'] == id) > 0:
                    df_old_activity = df_old_activity.drop(df_old_activity[df_old_activity['id'] == id].index)
                if str(activity).lower() != "i":
                    df_activity = pd.concat([df_old_activity, df_activity], ignore_index=True)
                else:
                    df_activity = df_old_activity
            df_activity.to_csv('activity\\activities.csv', index_label="Index", sep=';')
            break


def cmd_city():
    """
    Функция инициализирует класс City и предлагает получить пользователю одну из функций
    """
    startcity = City()
    print('Welcome to the "Kosiha city" "Global statistic" panel')
    print('Enter command')
    print('Health - Show health statistic')
    print('Social - Show social statistic')
    print('Population - Show dead/alive statistic')
    print('Census - look global census')
    startcity.ministry(end=datetime.date(2000, 1, 1).today(), departament=input('Input: '))


def command(_string):
    if _string.lower() == 'generate':
        generate()
    elif _string.lower() == 'refresh':
        refresh()
    elif _string.lower() == 'city':
        cmd_city()
    elif _string.lower() == 'game':
        game()
    else:
        print('Nothing happend')


def admin():
    wide_pandas()
    print('Welcome to the "Kosiha city" panel')
    print('Enter command')
    print('Generate - generate new citizen')
    print('Refresh - refresh citizens status until today')
    print('City - look global statictic')
    print('Game - create user or continie')
    command(input('Input: '))
    # input('Process finished')
