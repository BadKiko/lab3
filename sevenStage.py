#Created by Kiko(Zhukov Kirill) with ♥

#██╗░░██╗██╗██╗░░██╗░█████╗░
#██║░██╔╝██║██║░██╔╝██╔══██╗
#█████═╝░██║█████═╝░██║░░██║
#██╔═██╗░██║██╔═██╗░██║░░██║
#██║░╚██╗██║██║░╚██╗╚█████╔╝
#╚═╝░░╚═╝╚═╝╚═╝░░╚═╝░╚════╝░

import paramiko
import psycopg2
import csv
import numpy as np
import os
import time
from datetime import datetime
import fiona

# Параметры подключения к базе данных
hostname = '192.168.122.243'
username = 'postgres'
password = 'kiko123'
database = 'mainkiko'

# Параметры подключения к SFTP-серверу
hostname_sftp = '192.168.122.40'
username_sftp = 'postgres'
password_sftp = 'kiko123'


conn = None

# Пути к исходной и целевой директориям
source_dir = 'data/measurement'
target_dir = '/home/postgres/data/data/measurement'


def create_sftp_directory(sftp, directory_path):
    """
    Создает папку на сервере SFTP, если она не существует.
    """
    try:
        sftp.chdir(directory_path)
    except IOError:
        sftp.mkdir(directory_path)
        sftp.chdir(directory_path)

def clear_sftp_directory(sftp, directory_path):
    """
    Очищает содержимое папки на сервере SFTP.
    """
    sftp.chdir(directory_path)
    files = sftp.listdir()
    for file_name in files:
        file_path = directory_path + '/' + file_name
        sftp.remove(file_path)


def transfer_files_to_database():
    print("Передача файлов через SFTP")
    transport = paramiko.Transport((hostname_sftp, 22))
    transport.connect(username=username_sftp, password=password_sftp)
    sftp = paramiko.SFTPClient.from_transport(transport)
    # Создание папки, если она не существует
    create_sftp_directory(sftp, target_dir)

    # Очистка содержимого папки
    clear_sftp_directory(sftp, target_dir)

    # Создание клиента SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Установка соединения с сервером SFTP
        ssh.connect(hostname_sftp, username=username_sftp, password=password_sftp)

        # Открытие сессии SFTP
        sftp = ssh.open_sftp()

        # Переход в целевую директорию
        sftp.chdir(target_dir)

        # Получение списка файлов в исходной директории
        files = os.listdir(source_dir)

        # Итерация по файлам в исходной директории
        for filename in files:
            # Формирование путей к исходному и целевому файлам
            source_path = os.path.join(source_dir, filename)
            target_path = os.path.join(target_dir, filename)

            # Проверка, является ли текущий элемент файлом
            if os.path.isfile(source_path):
                # Передача файла на сервер SFTP
                sftp.put(source_path, target_path)

                # Опционально: удаление исходного файла после передачи
                os.remove(source_path)

        # Закрытие сессии SFTP
        sftp.close()

    finally:
        # Закрытие соединения SSH
        ssh.close()








def verify_database_info():
    global hostname, username, password, database, hostname_sftp, username_sftp, password_sftp
    
    print("Текущая информация о базе данных:")
    print(f"Хост: {hostname}")
    print(f"Пользователь: {username}")
    print(f"Пароль: {password}")
    print(f"База данных: {database}")
    
    choice = input("Это правильная информация для подключения к базе данных? (1 - Да, 2 - Нет): ")
    
    if choice == "2":
        hostname = input("Введите хост: ")
        username = input("Введите пользователя: ")
        password = input("Введите пароль: ")
        database = input("Введите имя базы данных: ")

    print("\nВведите информацию о SFTP")
    hostname_sftp = input("Введите хост:")
    username_sftp = input("Введите пользователя:")
    password_sftp = input("Введите пароль:")

def create_scheme(scheme_name):
    create_schema_query = f"CREATE SCHEMA IF NOT EXISTS {scheme_name};"
    cursor = conn.cursor()
    cursor.execute(create_schema_query)
    conn.commit()
    cursor.close()

def install_file_fdw(schema):
    cursor = conn.cursor()
    cursor.execute(f"CREATE EXTENSION IF NOT EXISTS file_fdw WITH SCHEMA {schema};")
    conn.commit()
    cursor.close()

def create_file_server(schema):
    cursor = conn.cursor()

    drop_server_query = "DROP SERVER IF EXISTS file_server CASCADE"
    cursor.execute(drop_server_query)
    conn.commit()

    create_server_query = f"""
        CREATE SERVER file_server
        FOREIGN DATA WRAPPER file_fdw;
    """
    cursor.execute(create_server_query)
    conn.commit()
    cursor.close()


def create_foreign_table(table_name, csv_file):
    cursor = conn.cursor()
    create_scheme('external')
    cursor.execute(f"DROP FOREIGN TABLE IF EXISTS external.{table_name}")
    create_table_query = f"""
        CREATE FOREIGN TABLE external.{table_name} (
            city INTEGER,
            mark TIMESTAMP WITHOUT TIME ZONE,
            temperature DOUBLE PRECISION
        )
        SERVER file_server
        OPTIONS (
            filename '{csv_file}',
            format 'csv',
            header 'true'
        );
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()


def create_measurement_foreign_tables():
    measurements_dir = 'data/measurement'  # Путь к директории с файлами измерений

    # Получение списка файлов измерений в директории
    measurement_files = [f for f in os.listdir(measurements_dir) if f.endswith('.csv')]

    for file_name in measurement_files:
        # Извлечение датасета из имени файла
        dataset = file_name.replace('.csv', '')

        # Формирование имени таблицы
        table_name = f"measurement_{dataset}"

        # Полный путь к файлу CSV
        csv_file = os.path.join(measurements_dir, file_name)

        # Создание внешней таблицы для текущего файла измерений
        create_foreign_table(table_name, csv_file)

    print("Созданы внешние таблицы для файлов измерений")


# Функция для создания таблицы в PostgreSQL
def create_table(scheme ,table_name, columns):
    cursor = conn.cursor()
    drop_query = f"DROP TABLE IF EXISTS {scheme}.{table_name.format()} CASCADE;"
    cursor.execute(drop_query)
    conn.commit()
    # Формирование строки CREATE TABLE
    create_query = f"CREATE TABLE {scheme}.{table_name} ({', '.join(columns)})"
    
    # Создание таблицы
    cursor.execute(create_query)
    
    conn.commit()
    cursor.close()

# Функция для импорта данных из CSV в таблицу PostgreSQL
def import_csv_to_table(schema, csv_file, table_name):
    cursor = conn.cursor()
    
    with open(csv_file, 'r') as file:
        # Чтение CSV файла с помощью модуля csv
        csv_data = csv.reader(file)
        columns = next(csv_data)  # Получение списка столбцов
        
        # Генерация строки INSERT для каждой записи
        insert_query = f"INSERT INTO {schema}.{table_name} VALUES ({', '.join(['%s'] * len(columns))})"
        
        # Установка схемы
        cursor.execute(f"SET search_path TO {schema}")
        
        # Вставка данных в таблицу
        file.seek(0)  # Возвращение к началу файла
        next(csv_data)  # Пропуск заголовка файла
        cursor.copy_from(file, table_name, sep=',', null='', columns=columns)
        
    conn.commit()
    cursor.close()


def create_coastline():
    shp = fiona.open("coastline/ne_10m_coastline.shp")
    i = 0
    sql = 'INSERT INTO data.coastline (shape, segment, latitude, longitude) VALUES'
    for feature in shp:
     arr = feature['geometry']['coordinates']
     x,y = np.array(arr).T
    
     for j in range (len(x)):
      sql += f'({i}, {j}, {x[j]}, {y[j]}),'
     i = i + 1
    sql = sql[:-1] + ';'
    cur = conn.cursor()
    cur.execute(sql)
    cur.close()
    conn.commit()


def merge_all_scheme(schema, table_name):
    cur = conn.cursor()

    # Получение списка внешних таблиц из схемы "external"
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='external';")
    external_tables = cur.fetchall()

    # Объединение внешних таблиц и вставка данных в таблицу "data.mesurement"
    for table in external_tables:
        cur.execute(f"INSERT INTO {schema}.{table_name} SELECT * FROM external.{table[0]};")

    # Завершение транзакции и закрытие соединения
    conn.commit()
    cur.close()
    conn.close()



# Получение списка файлов CSV в папке "data/measurement/"
def get_csv_files():
    csv_files = []
    measurement_dir = 'data/measurement/'
    for file_name in os.listdir(measurement_dir):
        if file_name.endswith('.csv'):
            csv_files.append(os.path.join(measurement_dir, file_name))
    return csv_files

def get_connection():
    print("Начинаем соединение с БД")
    global conn
    attempts = 0
    max_attempts = 5
    delay = 2  # Задержка между попытками подключения (в секундах)
    
    while attempts < max_attempts:
        try:
            conn = psycopg2.connect(
                host=hostname,
                database=database,
                user=username,
                password=password
            )
            print("Успешное подключение к базе данных")
            break
        except psycopg2.Error as e:
            print("Ошибка подключения к базе данных:", e)
            attempts += 1
            print(f"Повторная попытка подключения через {delay} сек...")
            time.sleep(delay)

# Проверка правильности информации о базе данных
#verify_database_info()

# Установка подключения
get_connection()

if conn is not None:
    print("Создаем схему data")
    create_scheme('data')

    install_file_fdw('data')
    create_file_server('data')

    print("Создаем таблицу регионов")
    # Создание таблицы "regions"
    create_table('data', 'regions', ['identifier SERIAL PRIMARY KEY', 'description TEXT'])

    print("Создаем таблицу стран")
    # Создание таблицы "countries"
    create_table('data', 'countries', ['identifier SERIAL PRIMARY KEY', 'region INTEGER REFERENCES data.regions(identifier)', 'description TEXT'])

    print("Создаем таблицу городов")
    # Создание таблицы "cities"
    create_table('data', 'cities', ['identifier SERIAL PRIMARY KEY', 'country INTEGER REFERENCES data.countries(identifier)', 'description TEXT', 'latitude DOUBLE PRECISION', 'longitude DOUBLE PRECISION', 'dataset TEXT'])

    print("Создаем таблицу измерений")
    # Создание таблицы "measurement"
    create_table('data','measurement', ['city INTEGER REFERENCES data.cities(identifier)', 'mark TIMESTAMP WITHOUT TIME ZONE', 'temperature TEXT'])

    print("Создаем таблицу береговых линий")
    # Создание таблицы "coastline"
    create_table('data', 'coastline', ['shape INTEGER', 'segment INTEGER', 'latitude DOUBLE PRECISION', 'longitude DOUBLE PRECISION'])

    create_coastline()

    #try:
    #    transfer_files_to_database()
    #except:
    #    print(f"Не удалось подключиться к SFTP")

    # Создание внешних таблиц измерений
    create_measurement_foreign_tables()

    print("Импорт данных в таблицу регионов из data/regions.csv")
    # Импорт данных в таблицу "regions"
    import_csv_to_table('data', 'data/regions.csv', 'regions')

    print("Импорт данных в таблицу стран из data/countries.csv")
    # Импорт данных в таблицу "countries"
    import_csv_to_table('data', 'data/countries.csv', 'countries')

    print("Импорт данных в таблицу городов из data/cities.csv")
    # Импорт данных в таблицу "cities"
    import_csv_to_table('data', 'data/cities.csv', 'cities')

    print("Соединение всех внешних таблиц из external в measurement")
    merge_all_scheme('data', 'measurement')

    conn.close()
else:
    print("Ошибка подключения! Убедитесь, что вы правильно выбрали IP-адрес")
