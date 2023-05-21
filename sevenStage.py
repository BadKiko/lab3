import psycopg2
import csv

# Параметры подключения к базе данных
hostname = '192.168.122.243'
username = 'postgres'
password = 'kiko123'
database = 'testdb'


# Функция для создания таблицы в PostgreSQL
def create_table(table_name, columns):
    conn = psycopg2.connect(
        host=hostname,
        database=database,
        user=username,
        password=password
    )
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
    conn.close()

# Функция для импорта данных из CSV в таблицу PostgreSQL
def import_csv_to_table(csv_file, table_name):
    conn = psycopg2.connect(
        host=hostname,
        database=database,
        user=username,
        password=password
    )
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
    conn.close()

# Создание таблицы "regions"
create_table('regions', ['identifier SERIAL PRIMARY KEY', 'description TEXT'])

# Создание таблицы "countries"
create_table('countries', ['identifier SERIAL PRIMARY KEY', 'region_id INTEGER REFERENCES regions(identifier)', 'description TEXT'])

# Создание таблицы "cities"
create_table('cities', ['identifier SERIAL PRIMARY KEY', 'country_id INTEGER REFERENCES countries(identifier)', 'description TEXT', 'latitude TEXT', 'longitude TEXT', 'dataset TEXT'])

# Импорт данных в таблицу "regions"
import_csv_to_table('data/regions.csv', 'regions')

# Импорт данных в таблицу "countries"
import_csv_to_table('data/countries.csv', 'countries')

# Импорт данных в таблицу "cities"
import_csv_to_table('data/cities.csv', 'cities')
