import datetime, os
import pandas as pd

# население города
class City:
    def __init__(self):
        """При инициализации создается 2 датафрейма - 1 с id, именами, полом, возрастом, жив ли, 2 из логов всех жителей
        При создании 2 датафрейма столбец с датами переводится в формат datetime, добавляется столбец с id жителя
        добавляется столбец с номером месяца"""
        # создаем папку с сохраненной статистикой, чтобы не создавать каждый раз дата фрейм по новой из логов
        if not os.path.exists('city_statistic'):
            os.mkdir("city_statistic")
            print("The folder 'city_statistic' doesn't exist, so I created it")
        # создаем массив. в него будем читать логи из папки с жителями и искать максимальное значение
        population_check = []
        # перебираем файлы жителей
        for i in os.listdir(os.getcwd() + '\citizens'):
            j = City.extract_id_hb_name_gender(i, only_id=True)
            population_check.append(j)
        # получаем максимальный индекс
        population_check = max(population_check)
        # данный буль будет для понимания, надо ли обновлять файлы
        # проверяет, все ли файлы в папке с нужной датой и соответствует ли количество жителей
        if len(os.listdir(os.getcwd() + '\city_statistic')) == 0:
            check_bool = False
        else:
            check_bool = True
        for i in os.listdir(os.getcwd() + '\city_statistic'):
            idd, ddate = City.extract_id_hb_name_gender(i, actual_check=True)
            if (ddate != datetime.date(2000, 1, 1).today()) or (idd != population_check):
                for delete_stat in os.listdir(os.getcwd() + '\city_statistic'):
                    os.remove(os.getcwd() + '\city_statistic\\' + delete_stat)
                check_bool = False
                break
        if not check_bool:
            df_id_card = []
            summary_citizen_bool = False
            # цель этого цикла сформировать из логов жителей ДФ.
            for i in os.listdir(os.getcwd() + '\citizens'):
                read_file = pd.read_csv(os.getcwd() + '\citizens\\' + str(i), parse_dates=['Date'], dayfirst=False,
                                        index_col='Index', sep=';')
                df_id_card.append(City.extract_id_hb_name_gender(i))
                id_citizen = City.extract_id_hb_name_gender(i, only_id=True)
                # добавляем колонку АЙ ДИ жителей
                read_file['Citizen_id'] = id_citizen
                # приписываем месяц
                read_file['Month'] = read_file['Date'].dt.month
                if not summary_citizen_bool:
                    self.summary_citizen = pd.DataFrame(read_file,
                                                        columns=["Date", "Health", "Mood_Status", "Social_Status",
                                                                 "Money",
                                                                 "Happienes", "Work_Status", "Work_Pass",
                                                                 "Work_experience",
                                                                 "Commentary", "Citizen_id", "Month"])
                    summary_citizen_bool = True
                else:
                    self.summary_citizen = pd.concat([self.summary_citizen, read_file], ignore_index=True)
            self.df_id_card = pd.DataFrame(df_id_card, columns=['id', 'date_of_birth', 'name', 'gender', 'alive'])
            self.df_id_card.to_csv(
                os.getcwd() + '\city_statistic\id_{}_{}.csv'.format(str(datetime.date(2000, 1, 1).today()),
                                                                    str(self.df_id_card['id'].max())),
                index_label="Index", sep=';')
            self.summary_citizen.to_csv(
                os.getcwd() + '\city_statistic\summary_{}_{}.csv'.format(str(datetime.date(2000, 1, 1).today()),
                                                                         str(self.df_id_card['id'].max())),
                index_label="Index", sep=';')
        else:
            self.df_id_card = pd.read_csv(
                os.getcwd() + '\city_statistic\id_{}_{}.csv'.format(str(datetime.date(2000, 1, 1).today()),
                                                                    str(population_check)),
                index_col='Index', sep=';')
            self.summary_citizen = pd.read_csv(
                os.getcwd() + '\city_statistic\summary_{}_{}.csv'.format(str(datetime.date(2000, 1, 1).today()),
                                                                         str(population_check)),
                parse_dates=['Date'], dayfirst=False,
                index_col='Index', sep=';')

    def extract_id_hb_name_gender(_filename, only_id=False, actual_check=False):
        """3 опции:
        по умолчанию извлекает id, happy_birthday, name, gender, alive
        из файла формата id_happybirthday_name_gender_alive
        если only_id=True
        то извлекает только id
        если actual_check=True
        то извлекает id, date"""
        _filename = _filename.replace('.csv', '')
        _filename = _filename.split('_')
        if (not only_id) and (not actual_check):
            _id = int(_filename[0])
            _happy_birthday = datetime.date(int(_filename[1][:4]), int(_filename[1][5:7]), int(_filename[1][8:10]))
            _name = str(_filename[2])
            _gender = str(_filename[3])
            if _filename[4] == 'True':
                _alive = True
            else:
                _alive = False
            return _id, _happy_birthday, _name, _gender, _alive
        elif only_id:
            _id = int(_filename[0])
            return _id
        elif actual_check:
            _id = int(_filename[2])
            _date = datetime.date(int(_filename[1][:4]), int(_filename[1][5:7]), int(_filename[1][8:10]))
            return _id, _date


    def ministry(self, start=datetime.date(2022, 1, 1), end=datetime.date(2022, 12, 1), departament=None):
        """функция позволяет посмотреть статистики города
        если информация нужна в разрезе месяца(это кстати надо доделать)
        (вообще нужно доделать, чтобы были разные функции за месяц и год)
        то создаются серии состояний на конец месяца. """
        i = start
        end = end.replace(day=1) - datetime.timedelta(days=1)
        #df передает, создался ли ДФ
        df_bool = False
        while i < end:
            # эти операции передают конец месяца
            # для пересчета статистики по годам или неделям нужно будет модифицировать эти строки кода
            end_of_month = i.replace(day=28) + datetime.timedelta(days=4)
            end_of_month = end_of_month - datetime.timedelta(days=end_of_month.day)
            # создаем серию состояний на конец месяца
            end_of_month_series = self.summary_citizen[self.summary_citizen['Date'] == pd.Timestamp(end_of_month)]
            i = end_of_month + datetime.timedelta(days=1)
            if departament.lower() == 'health':
                # создаем пустой лист из которого будем собирать ДФ
                list_health = []
                # создаем словарь значений соответствующих статусам. также добавляем месяц (его конец) в начало
                health_count = {'month': 0, 'astronaut': 0, 'bull': 0, 'usual': 0, 'chronically': 0, 'disabled': 0}
                # пересчитываем значения в конце месяца для каждого поля словаря.
                for j in health_count:
                    health_count[j] = int(end_of_month_series[['Health']][end_of_month_series['Health'] == j].count())
                # присваиваем полю месяц значение конца месяца
                health_count['month'] = end_of_month
                # присваиваем листу значения словаря. вообще тут аппенд необязателен - я думал вначале делать список списков
                list_health.append(list(health_count.values()))
                if not df_bool:
                    df_final = pd.DataFrame(list_health,
                                            columns=['month', 'astronaut', 'bull', 'usual', 'chronically', 'disabled'])
                    df_bool = True
                else:
                    list_health = pd.DataFrame(list_health,
                                               columns=['month', 'astronaut', 'bull', 'usual', 'chronically',
                                                        'disabled'])
                    df_final = pd.concat([df_final, list_health], ignore_index=True)
            elif departament.lower() == 'social':
                list_social = []
                social_count = {'month': 0, 'wretched': 0, 'squalid': 0, 'poor': 0, 'modest': 0, 'comfortable': 0,
                                'wealthy': 0, 'aristocratic': 0}
                for j in social_count:
                    social_count[j] = int(
                        end_of_month_series[['Social_Status']][end_of_month_series['Social_Status'] == j].count())
                social_count['month'] = end_of_month
                list_social.append(list(social_count.values()))
                if not df_bool:
                    df_final = pd.DataFrame(list_social,
                                            columns=['month', 'wretched', 'squalid', 'poor', 'modest', 'comfortable',
                                                     'wealthy', 'aristocratic'])
                    df_bool = True
                else:
                    list_social = pd.DataFrame(list_social,
                                               columns=['month', 'wretched', 'squalid', 'poor', 'modest', 'comfortable',
                                                        'wealthy', 'aristocratic'])
                    df_final = pd.concat([df_final, list_social], ignore_index=True)
            elif departament.lower() == 'health_age':
                # ЕБЕМСЯ С ЭТИМ
                yesterday = pd.Timestamp(datetime.date(2000, 1, 1).today() - datetime.timedelta(days=1))
                df_yesterday = self.summary_citizen[self.summary_citizen['Date'] == yesterday]
                df_yesterday = df_yesterday[['Citizen_id', 'Health']]
                df_citizens = self.df_id_card
                df_citizens.set_index('id')
                df_yesterday.set_index('Citizen_id')
                df_citizens.update(df_yesterday)
                df_final = str(df_citizens.head())
                break

            elif departament.lower() == 'population':
                df_final = 'Alive citizens = ' + str(
                    self.df_id_card['alive'][self.df_id_card['alive'] == True].count()) + '\nDead citizens =' + str(
                    self.df_id_card['alive'][self.df_id_card['alive'] != True].count())
                break
            elif departament.lower() == 'census':
                for kk in os.listdir(os.getcwd() + '\citizens'):
                    print(City.extract_id_hb_name_gender(kk, only_id=True), )
                    df_final = None
            else:
                df_final = 'Nothing happens'
        print(df_final)

    def age_category(_age):
        if _age < 18:
            return 'young'
        if 25 > _age >= 18:
            return '18-24'
        elif 35 > _age >= 25:
            return '25-34'
        elif 45 > _age >= 35:
            return '35-44'
        elif 60 >= _age >= 45:
            return '45-60'
        else:
            return '60+'