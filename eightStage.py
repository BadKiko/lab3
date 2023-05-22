import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# Параметры подключения к базе данных
hostname = '192.168.122.243'
username = 'postgres'
password = 'kiko123'
database = 'mainkiko'

conn = None

def drawMap():
    # Создание курсора для выполнения SQL-запросов
    cursor = conn.cursor()

    # Выполнение SQL-запроса для получения данных
    query = "SELECT longitude, latitude FROM data.coastline"
    cursor.execute(query)

    # Получение результатов запроса
    results = cursor.fetchall()

    # Закрытие курсора и соединения
    cursor.close()
    conn.close()

    # Создание DataFrame из результатов запроса
    data = pd.DataFrame(results, columns=['longitude', 'latitude'])

    # Создание графика
    plt.figure(figsize=(10, 6))
    plt.scatter(data['longitude'], data['latitude'], s=0.5, alpha=0.5)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Map')

    # Ограничение пределов осей
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)

    # Отображение графика
    plt.show()

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

verify_database_info()
get_connection()
drawMap()