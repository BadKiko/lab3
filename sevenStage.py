#Created by Kiko(Zhukov Kirill) with ♥

#██╗░░██╗██╗██╗░░██╗░█████╗░
#██║░██╔╝██║██║░██╔╝██╔══██╗
#█████═╝░██║█████═╝░██║░░██║
#██╔═██╗░██║██╔═██╗░██║░░██║
#██║░╚██╗██║██║░╚██╗╚█████╔╝
#╚═╝░░╚═╝╚═╝╚═╝░░╚═╝░╚════╝░


import psycopg2
import csv
import os

# Параметры подключения к базе данных
hostname = '192.168.122.243'
username = 'postgres'
password = 'kiko123'
database = 'testdb'

conn = None

# Функция для создания таблицы в PostgreSQL
def create_table(table_name, columns):
    cursor = conn.cursor()
    drop_query = "DROP TABLE IF EXISTS {} CASCADE;".format(table_name)
    cursor.execute(drop_query)
    conn.commit()
    # Формирование строки CREATE TABLE
    create_query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
    
    # Создание таблицы
    cursor.execute(create_query)
    
    conn.commit()
    cursor.close()

# Функция для импорта данных из CSV в таблицу PostgreSQL
def import_csv_to_table(csv_file, table_name):
    cursor = conn.cursor()
    
    with open(csv_file, 'r') as file:
        # Чтение CSV файла с помощью модуля csv
        csv_data = csv.reader(file)
        next(csv_data)  # Пропуск заголовка файла
        
        # Генерация строки INSERT для каждой записи
        insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(next(csv_data)))})"
        
        # Вставка данных в таблицу
        file.seek(0)  # Возвращение к началу файла
        next(csv_data)  # Пропуск заголовка файла
        cursor.copy_from(file, table_name, sep=',', null='')
        
    conn.commit()
    cursor.close()

# Получение списка файлов CSV в папке "data/measurement/"
def get_csv_files():
    csv_files = []
    measurement_dir = 'data/measurement/'
    for file_name in os.listdir(measurement_dir):
        if file_name.endswith('.csv'):
            csv_files.append(os.path.join(measurement_dir, file_name))
    return csv_files

def get_connection():
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
# verify_database_info()

# Установка подключения
get_connection()

if conn is not None:
    print("Создаем таблицу регионов")
    # Создание таблицы "regions"
    create_table('regions', ['identifier SERIAL PRIMARY KEY', 'description TEXT'])

    print("Создаем таблицу стран")
    # Создание таблицы "countries"
    create_table('countries', ['identifier SERIAL PRIMARY KEY', 'region_id INTEGER REFERENCES regions(identifier)', 'description TEXT'])
    
    print("Создаем таблицу городов")
    # Создание таблицы "cities"
    create_table('cities', ['identifier SERIAL PRIMARY KEY', 'country_id INTEGER REFERENCES countries(identifier)', 'description TEXT', 'latitude DOUBLE PRECISION', 'longitude DOUBLE PRECISION', 'dataset TEXT'])
    
    print("Создаем таблицу измерений в городах")
    # Создание таблицы "measurement"
    create_table('measurement', ['city INTEGER REFERENCES cities(identifier)', 'mark TEXT', 'temperature TEXT'])
    
    print("Создаем таблицу береговых линий")
    # Создание таблицы "regions"
    create_table('coastline', ['shape INTEGER', 'segment INTEGER', 'latitude DOUBLE PRECISION', 'longtitude DOUBLE PRECISION'])


    print("Импорт данных в таблицу регионов из data/regions.csv")
    # Импорт данных в таблицу "regions"
    import_csv_to_table('data/regions.csv', 'regions')
    
    print("Импорт данных в таблицу стран из data/countries.csv")
    # Импорт данных в таблицу "countries"
    import_csv_to_table('data/countries.csv', 'countries')
    
    print("Импорт данных в таблицу городов из data/cities.csv")
    # Импорт данных в таблицу "cities"
    import_csv_to_table('data/cities.csv', 'cities')
    
    print("Импорт данных в таблицу измерений городов из data/measurement.csv")
    # Импорт данных в таблицу "measurement"
    import_csv_to_table('data/measurement.csv', 'measurement')

    print("Импорт данных в таблицу береговых линий из data/coastline.csv")
    # Импорт данных в таблицу "measurement"
    import_csv_to_table('data/coastline.csv', 'coastline')

    conn.close()
else:
    print("Ошибка подключения! Убедитесь что вы правильно выбрали IP адрес")