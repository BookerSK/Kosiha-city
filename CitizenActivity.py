from InitializationCitizen import InitializationCitizen
import datetime, os
from CONSTANTS import MORTY, HEALTH, PHYSICAL, SOCIAL, ACTION_COMMENTARY
from random import randint
import pandas as pd

class CitizenActivity(InitializationCitizen):
    """Класс определяет что гражданин каждый день делает"""

    def dayend(self):
        """К концу дня человек тратит деньги на ежедневные нужды. Распечатывается его статы. А ещё он может умереть"""
        if self.alive:
            self.spend_money()
            self.day_activity()
            if self.day == datetime.date(self.day.year, self.happy_birthday.month, self.happy_birthday.day):
                self.getting_old(self.age)
            # print(
            #     "Day {}! My health is {}. My social status is {}. I feel myself {}. I have {} rubles.".format(
            #         self.day,
            #         self.health,
            #         self.social_status,
            #         self.mood_status,
            #         int(self.money)))
            a = self.micromort(HEALTH.index(self.health), SOCIAL.index(self.social_status),
                               PHYSICAL.index(self.mood_status))
            _rnd = randint(1, 1000000)
            if _rnd < self.micromort(HEALTH.index(self.health), SOCIAL.index(self.social_status),
                                     PHYSICAL.index(self.mood_status)):
                self.alive = False
                self.commentary = "I died in age " + str(
                    self.age + (self.day - datetime.date(2022, 1, 1)).days // 365) + ' with micromort ' + str(a)
                _name = '_'.join(InitializationCitizen.stable_list(self))
                #ниже проверяется, является ли челик игроком. Если да, то записывается уведомление о гибели
                #а также в БД отмечается, что челик отъехал. При следующем входе на любую команду система уведомит
                #что челик умер и нужно создать нового персонажа
                if os.path.exists('real_players\\real_players_ids.csv'):
                    df_check_real_pl = pd.read_csv('real_players\\real_players_ids.csv', index_col='Index', sep=';')
                    if len(df_check_real_pl[df_check_real_pl['id'] == self.id]) > 0:
                        df_save = df_check_real_pl[df_check_real_pl['id'] == self.id].copy()
                        df_save['alive'] = False
                        tg_id = int(df_save['tg_id'].values[0])
                        df_check_real_pl = df_check_real_pl.drop(df_check_real_pl[df_check_real_pl['id'] == self.id].index)
                        df_check_real_pl = pd.concat([df_check_real_pl,df_save])
                        df_check_real_pl.to_csv('real_players\\real_players_ids.csv', index_label="Index", sep=';')
                        notification_new = pd.DataFrame({'tg_id': [tg_id], 'type': ['death']})
                        if os.path.exists('real_players\\notification.csv'):
                            notification_old = pd.read_csv('real_players\\notification.csv', index_col='Index', sep=';')
                            notification_new = pd.concat([notification_old,notification_new])
                        notification_new.to_csv('real_players\\notification.csv', index_label="Index", sep=';')



                if os.path.exists('citizens\{}.csv'.format(_name.replace("False", 'True'))):
                    os.remove('citizens\{}.csv'.format(_name.replace("False", 'True')))
            # в конце дня к списку состояний персонажа добавляется новый список состояний, обнуляется ежедневный комментарий
            self.data_citizen.append(self.add_str())
            # наступает следующий день
            self.day += datetime.timedelta(days=1)
        # print(self.commentary)
        self.commentary = ''

    def spend_money(self):
        """Если не аристократ, то каждый день тратит 1/30 на жизнь и откладывает 10%, если ниже бедного. Если средний класс,
        то откладывает 20% зп. Если богатый и выше, тратит от 5 000 до 20 000
        Если к концу дня у персонажа долги, то он становится банкротом и его социальный статус снижается и возвращается количество денег положенное статусу
        Если к концу дня у персонажа в три раза больше денег, чем положено по статусу (т.е. на статус выше), то его статус повышается.
        Также в этой функции прописана зарплата"""
        if self.social_status != 'aristocratic':
            if SOCIAL.index(self.social_status) < 3:
                self.money -= InitializationCitizen.social_status_money(self.social_status) * 0.9 / 30
            elif self.social_status == 'modest':
                self.money -= InitializationCitizen.social_status_money(self.social_status) * 0.8 / 30
            else:
                self.money -= randint(5000, 20000)
            if (self.work_status) and (self.work_pass < 3):
                if self.day.day == 15:
                    self.money += InitializationCitizen.social_status_money(self.social_status) * 0.4
                    self.commentary += 'Today I got my advance.'
                if self.day.day == 1:
                    self.money += InitializationCitizen.social_status_money(self.social_status) * 0.6 + InitializationCitizen.social_status_money(
                        self.social_status) * 0.1 * (self.work_experience // 365)
                    self.commentary += 'Today I got my salary.'
            else:
                self.commentary += ' '
                self.go_to_work()
            # если к концу дня у персонажа долги, то он становится банкротом и его социальный статус снижается и возвращается количество денег положенное статусу
            if self.money < 0:
                if self.social_status != 'wretched':
                    self.money = InitializationCitizen.social_status_money(self.social_status)
                    self.social_status = SOCIAL[SOCIAL.index(self.social_status) - 1]
                    self.commentary += "Oh, no, I'm bankrupt. My social status is {} now.".format(self.social_status)
                    # человек лишается работы, если становится бомжом
                    if self.social_status == 'wretched':
                        self.work_status = False
            # если к концу дня у персонажа в три раза больше денег, чем положено по статусу (т.е. на статус выше), то его статус повышается.
            if self.money > InitializationCitizen.social_status_money(SOCIAL[SOCIAL.index(self.social_status) + 1]) * 3:
                if self.social_status != 'aristocratic':
                    self.social_status = SOCIAL[SOCIAL.index(self.social_status) + 1]
                    self.commentary += "I feel myself more prestigious. My social status is {} now.".format(
                        self.social_status)
        else:
            self.money = InitializationCitizen.social_status_money(self.social_status)

    def getting_old(self, _age):
        '''функция пересчитывает года в соответствии с днем рождения и может рандомно подкинуть болезнь'''
        _a = InitializationCitizen.age_health(_age + 10 * (6 - SOCIAL.index(self.social_status)))
        self.age = (self.day - self.happy_birthday).days // 365
        self.commentary += " Today is my Happy Birthday! I'm {} years old.".format(self.age)
        if (HEALTH.index(_a) > HEALTH.index(self.health)) and (self.health != 'disabled'):
            self.health = HEALTH[HEALTH.index(self.health) + 1]
            self.commentary += " My health is getting worse. It's {} now.".format(self.health)

    def micromort(self, _health, _social_status, _happienes):
        """ рассчет вероятности умереть на миллион при текущем здоровье и социальном статусе
        Константа MORTY определяет глобальные вероятности умереть"""
        return (MORTY * 1 / 4 * 2 ** _health * 16 / 2 ** _social_status * 4 / 2 ** _happienes) * (
                1000 ** ((self.age + (self.day - datetime.date(2022, 1, 1)).days // 365) // 100))

    def day_activity(self, _rnd_act=0, randomize=True):
        """Рандомизирует активности или навязывает их персонажу, если они ему необходимы"""
        if os.path.exists('activity\\activities.csv'):
            force_action = pd.read_csv('activity\\activities.csv', parse_dates=['Date'], dayfirst=False,
                            index_col='Index', sep=';')
            day = pd.Timestamp(self.day)
            date_id_checking = force_action[force_action['id'] == self.id]
            #уязвимость. может плохо работать с прошлым
            #date_id_checking = date_id_checking[date_id_checking['Date'] >= day]
            if len(date_id_checking) > 0:
                randomize = False
                _rnd_act = int(date_id_checking['to_do'].tolist()[0])
        if randomize:
            _rnd_act = randint(0, 4)
            if (self.work_status and self.day.weekday() < 5) or (_rnd_act == 0):
                self.go_to_work()
            elif self.have_money(3500) and self.social_status != 'wretched' and (
                    (self.mood_status == 'depressed') or (_rnd_act == 4)):
                self.go_to_spa()
            elif self.have_money(1000) and (
                    (self.mood_status == 'depressed') or (_rnd_act == 2)):
                self.drink()
            elif _rnd_act == 3:
                self.see_doctor()
            else:
            #relax соответствует рандому 1
                self.relax()
        else:
            if (self.work_status and self.day.weekday() < 5) and (_rnd_act > 0):
                self.work_pass += 1
            if _rnd_act == 0:
                self.go_to_work()
            elif _rnd_act == 4:
                self.go_to_spa()
            elif _rnd_act == 2:
                self.drink()
            elif _rnd_act == 3:
                self.see_doctor()
            else:
                self.relax()

    def have_money(self, _spend):
        """Эта функция определяет, обанкротится ли чувак, если потратит сегодня столько-то денег"""
        if self.day.month < 12:
            return self.money - InitializationCitizen.social_status_money(self.social_status) * (
                    datetime.date(self.day.year, self.day.month + 1, 1) - self.day).days / (
                           datetime.date(self.day.year, self.day.month + 1, 1) - datetime.date(self.day.year,
                                                                                               self.day.month,
                                                                                               1)).days - _spend > 0
        else:
            return self.money - InitializationCitizen.social_status_money(self.social_status) * (
                    datetime.date(self.day.year, 1, 1) - self.day).days / (
                           datetime.date(self.day.year, 1, 1) - datetime.date(self.day.year, self.day.month,
                                                                              1)).days - _spend > 0

    def go_to_work(self):
        '''Если ты бомж, то можешь взять подработку и заработать 500 до 1500 р.
        Если ты работаешь, то при плохом настроении есть вероятность, что ты на работу не выйдешь
        Если у тебя нет работы и ты не бомж, то ты её ищешь'''
        if self.work_pass < 3:
            if self.social_status == 'wretched':
                _a = randint(1, 3) * 500
                self.money += _a
                self.commentary += 'I found a side job and earned {}.'.format(str(_a))
            elif not self.work_status:
                _findjob = randint(0, 100) + 10 * SOCIAL.index(self.social_status)
                if _findjob > 50:
                    self.commentary += "Finally I've found a job!"
                    self.work_status = True
                    self.work_pass = 0
                else:
                    self.commentary += "I was looking for a job, but nobody appreciated me."
                    self.happiness -= 10
            elif self.day.weekday() < 5:
                if self.mood_status == 'depressed':
                    _fkjob = randint(0, 100)
                else:
                    _fkjob = 0
                if _fkjob > 90:
                    self.commentary += 'Fuck this job! I need a rest!'
                    self.happiness = 60
                    self.mood_status = self.mood(self.happiness)
                    self.work_pass += 1
                else:
                    self.happiness -= 5
                    self.mood_status = self.mood(self.happiness)
                    self.commentary += ACTION_COMMENTARY['work']
                    if self.work_experience == -1:
                        self.work_experience = 1
                    else:
                        self.work_experience += 1
            else:
                self.happiness -= 20
                self.money += InitializationCitizen.social_status_money(self.social_status) * 0.005
                self.mood_status = self.mood(self.happiness)
                self.commentary += ACTION_COMMENTARY['work_overtime']
        else:
            self.commentary += "I didn't go to work for 3 times, so I was failed."
            self.work_status = False
            self.work_pass = 0
            self.work_experience = -1

    def relax(self):
        """Виды отдыха определяются социальным слоем.
    Человек не может пойти развлекаться, если есть вероятность его банкротства к концу месяца"""
        if self.social_status != 'wretched':
            _rnd = randint(0, 1)
        else:
            _rnd = 0
        if _rnd == 0:
            self.happiness += 10
            self.mood_status = self.mood(self.happiness)
            self.commentary += 'I was relaxing all day.'
        elif _rnd == 1:
            self.happiness += 15
            self.mood_status = self.mood(self.happiness)
            self.commentary += 'I was playing videogames all day.'

    def drink(self):
        '''Доступное всем развлечение - выпивка'''
        self.happiness += 30
        self.money -= 1000
        self.mood_status = self.mood(self.happiness)
        self.commentary += "I got drunk, I'll be happy until tomorrow."

    def see_doctor(self):
        '''С некоторой вероятностью ты можешь поднять здоровье, если ты не здоров как космонавт, либо ты не инвалид'''
        if self.health == 'disabled':
            self.commentary += "I visited a doctor. I'm disabled, so only mirracle can help me."
        elif self.health == 'astronaut':
            self.commentary += "I visited a doctor. I'm healthy as an astronaut. I'm going to the Korolev. Joke!"
        else:
            _rnd = randint(0, 100)
            if self.health == HEALTH[1] and _rnd == 0:
                self.health = HEALTH[0]
                self.commentary += "I visited a doctor. I fixed all my diseases - now I'm healthy as an astronaut."
            elif self.health == HEALTH[2] and _rnd < 10:
                self.health = HEALTH[1]
                self.commentary += "I visited a doctor. I heal some of my diseases - now I'm healthy as a bull."
            elif self.health == HEALTH[3] and _rnd == 0:
                self.health = HEALTH[2]
                self.commentary += "I visited a doctor. It was hard but all my chronic diseases went into recession  - now I'm healthy as an usual."
            else:
                self.commentary += "I visited a doctor. Doctors couldn't help me."

    def go_to_spa(self):
        '''Развлечение, недоступное бомжам'''
        self.happiness += 50
        self.money -= 3500
        self.mood_status = self.mood(self.happiness)
        self.commentary += "I visited SPA, I feel myself so relaxed."

    def save_story(self):
        if not os.path.exists('citizens'):
            os.mkdir("citizens")
            print("The folder 'citizens' doesn't exist, so I created it")
        _name = '_'.join(InitializationCitizen.stable_list(self))
        data_citizen = pd.DataFrame(self.data_citizen,
                                    columns=["Date", "Health", "Mood_Status", "Social_Status", "Money",
                                             "Happienes", "Work_Status", "Work_Pass", "Work_experience",
                                             "Commentary"])
        data_citizen.to_csv(os.getcwd() + '\citizens\{}.csv'.format(_name), index_label="Index", sep=';')
