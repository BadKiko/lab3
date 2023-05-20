import psycopg2
import csv

# Параметры подключения к базе данных
hostname = '192.168.122.243'
username = 'postgres'
password = 'kiko123'
database = 'mainkiko'

# Путь к CSV файлу
csv_file = 'data/data.csv'

# Создание таблицы
def create_table():
    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    cur = conn.cursor()

    # Замените 'your_table_name' на имя таблицы, которую вы хотите создать
    cur.execute("""
        CREATE TABLE your_table_name (
            column1 datatype1,
            column2 datatype2,
            column3 datatype3,
            ...
        )
    """)

    conn.commit()
    conn.close()

# Загрузка данных из CSV файла
def load_data():
    conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
    cur = conn.cursor()

    # Замените 'your_table_name' и 'your_csv_file' на соответствующие значения
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Пропустить заголовок CSV файла
        for row in reader:
            cur.execute("""
                INSERT INTO your_table_name (column1, column2, column3, ...)
                VALUES (%s, %s, %s, ...)
            """, row)

    conn.commit()
    conn.close()

# Создание таблицы
create_table()

# Загрузка данных из CSV файла
load_data()
