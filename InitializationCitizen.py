import datetime, os
from CONSTANTS import GENDER, HEALTH, PHYSICAL, SOCIAL, NAMES
from random import randint, choice
from  City import City

class InitializationCitizen:
    "Класс проводит инициализацию гражданина"

    def __init__(self, _id=-1, _happy_birthday=datetime.date(2000, 1, 1), _name='TERRA', _gender='woman', _alive=True,
                 _day=datetime.date(2999, 1, 1),
                 _health='astronaut', _mood_status='happy',
                 _social_status='aristocratic', _money=2 ** 100, _happiness=100, _work_status=False,
                 _work_pass=0, _work_experience=0, _commentary="I'LL KILL YOU ALL", _data_citizen= [],
                 _randomize=True):

        """конструктор класса либо при _randomize задает рандомный возраст, пол, имя, здоровье, сытость, счастье, социальный статус и id гражданина
        либо инциирует класс с заданными вручную параметрами"""

        # задаем id жителя
        if _randomize:
            self.id = InitializationCitizen.max_id() + 1
            # вводим параметры персонажа
            self.day = datetime.date(2022, 1, 1)
            self.gender = choice(GENDER)
            self.name = InitializationCitizen.random_name(self.gender)
            # вводим его статы
            self.happy_birthday = InitializationCitizen.random_date_birth()
            self.age = (self.day - self.happy_birthday).days // 365
            # узнаем здоровье после рандомизации др
            self.health = InitializationCitizen.age_health(self.age)
            self.happiness = 50
            self.social_status = InitializationCitizen.social_status_fun()
            self.money = InitializationCitizen.social_status_money(self.social_status)
            self.alive = True
            self.mood_status = self.mood(self.happiness)
            self.work_status = choice([True, False])
            self.work_pass = 0
            # если есть работа, то генерируем трудовой стаж
            if self.work_status:
                self.work_experience = randint(1, (self.day - self.happy_birthday).days)
            else:
                self.work_experience = -1
            self.commentary = "Hi, my name is {}! I'm {} years old {}. My health is {}. I feel myself {}. My social status is {}. My id is {}. I have {} rubles. ".format(
                self.name,
                self.age,
                self.gender,
                self.health,
                self.mood_status,
                self.social_status, self.id,
                self.money)
        else:
            self.id = _id
            # вводим параметры персонажа
            self.happy_birthday = _happy_birthday
            self.gender = _gender
            self.name = _name
            # вводим его статы
            self.health = _health
            self.happiness = _happiness
            self.social_status = _social_status
            self.money = _money
            self.alive = _alive
            self.mood_status = self.mood(self.happiness)
            self.work_status = _work_status
            self.work_pass = _work_pass
            self.work_experience = _work_experience
            self.day = _day
            # Года вычисляются вычитанием текущего дня и др
            self.age = (self.day - self.happy_birthday).days // 365
            self.commentary = _commentary
        # после заполнения величин создается список из списков статов гражданина
        self.data_citizen = _data_citizen

    def __str__(self):
        return "Today is {} Hi, my name is {}! I'm {} years old {} with birthbay in {}.  My health is {}. I feel myself {} with happiness {}. My social status is {}. My id is {}. I have {} rubles. My work status is {} with {} days experience and {} passes".format(
            self.day, self.name,
            self.age,
            self.gender,
            self.happy_birthday,
            self.health,
            self.mood_status,
            self.happiness,
            self.social_status, self.id,
            self.money, self.work_status, self.work_experience, self.work_pass)

    def random_date_birth():
        """Функция рандомизирует день рождения. Пока что не учтены високосные года и ДР 29 февраля"""
        _year = randint(1962, 2003)
        _month = randint(1, 12)
        _next_month = datetime.date(2022, _month, 1).replace(day=28) + datetime.timedelta(days=4)
        _next_month = _next_month - datetime.timedelta(days=_next_month.day)
        _day = randint(1, _next_month.day)
        if _month == 2 and _day == 29:
            _day = 28
        return datetime.date(_year, _month, _day)

    def age_health(age_int: int):
        """рандомизируем статус здоровья в зависимости от возраста"""
        if age_int < 26:
            rnd = randint(0, 100) - 60
        elif age_int > 25 and age_int < 36:
            rnd = randint(0, 100) - 20
        elif age_int > 35 and age_int < 61:
            rnd = randint(0, 100) + 10
        elif age_int > 60:
            rnd = randint(0, 100) + 30
        if rnd < 11:
            return HEALTH[1]
        elif rnd < 21:
            return HEALTH[0]
        elif rnd < 41:
            return HEALTH[2]
        elif rnd < 71:
            return HEALTH[3]
        else:
            return HEALTH[4]

    def social_status_fun():
        """определяем деньги и социальный статус гражданина"""
        _rnd = randint(0, 1000)
        if _rnd == 1:
            return SOCIAL[6]
        elif _rnd < 30:
            return SOCIAL[5]
        elif _rnd < 55:
            return SOCIAL[4]
        elif _rnd < 260:
            return SOCIAL[3]
        elif _rnd < 600:
            return SOCIAL[2]
        elif _rnd < 950:
            return SOCIAL[1]
        else:
            return SOCIAL[0]

    def social_status_money(str):
        """деньги соответствующие социальному статусу"""
        SS_MONEY = [100, 10000, 50000, 100000, 1000000, 1000000000, 1000000000000]
        return SS_MONEY[SOCIAL.index(str)]

    def random_name(gender):
        """задать рандомное имя"""
        return choice(NAMES[gender])

    #
    def mood(self, mood):
        """переводит настроение в психический статус"""
        if mood < 0:
            self.happiness = 0
        if mood > 100:
            self.happiness = 100
        if mood < 20:
            return PHYSICAL[0]
        elif 20 <= mood < 40:
            return PHYSICAL[1]
        elif 40 <= mood < 60:
            return PHYSICAL[2]
        elif 60 <= mood < 80:
            return PHYSICAL[3]
        elif 80 <= mood :
            return PHYSICAL[4]

    def stable_list(self):
        return [str(self.id), str(self.happy_birthday), str(self.name), str(self.gender), str(self.alive)]

    def add_str(self):
        return [self.day, self.health, self.mood_status, self.social_status, self.money, self.happiness,
                self.work_status, self.work_pass, self.work_experience, self.commentary]

    def max_id(max_id_answer = []):
        for i in os.listdir(os.getcwd() + '\citizens'):
            max_id_answer.append(City.extract_id_hb_name_gender(i, only_id=True))
        if max_id_answer == []:
            return  -1
        return int(max(max_id_answer))

