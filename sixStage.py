#Created by Kiko(Zhukov Kirill) with ♥

#██╗░░██╗██╗██╗░░██╗░█████╗░
#██║░██╔╝██║██║░██╔╝██╔══██╗
#█████═╝░██║█████═╝░██║░░██║
#██╔═██╗░██║██╔═██╗░██║░░██║
#██║░╚██╗██║██║░╚██╗╚█████╔╝
#╚═╝░░╚═╝╚═╝╚═╝░░╚═╝░╚════╝░


import pandas as pd
import os

def createRegions():
    # Чтение исходного файла data/data.csv
    df = pd.read_csv('data/data.csv')

    # Отбор уникальных регионов
    unique_regions = df['Regions'].unique()

    # Создание нового DataFrame с уникальными регионами
    regions_df = pd.DataFrame({'identifier': range(1, len(unique_regions) + 1),
                           'description': unique_regions})

    # Запись DataFrame в CSV-файл
    regions_df.to_csv('data/regions.csv', index=False)
    print("Создан файл регионов data/regions.csv")

def createCountries():
    # Чтение исходного файла data.csv
    df = pd.read_csv('data/data.csv')

    # Чтение файла с регионами
    regions_df = pd.read_csv('data/regions.csv')

    # Отбор уникальных стран и их регионов
    unique_countries = df.iloc[:, 0].unique()  # 1-й столбец в data.csv
    countries_regions = df.iloc[:, [0, 1]]  # 1-й и 2-й столбцы в data.csv

    # Создание нового DataFrame с уникальными странами и их регионами
    countries_df = pd.DataFrame({'identifier': range(1, len(unique_countries) + 1),
                                 'country': unique_countries})

    # Объединение данных с регионами для получения идентификаторов регионов
    countries_df = countries_df.merge(countries_regions, how='left', left_on='country', right_on=df.columns[0])
    countries_df = countries_df.merge(regions_df, how='left', left_on=df.columns[1], right_on='description')

    # Удаление ненужных столбцов и переименование столбцов
    countries_df = countries_df[['identifier_y', 'identifier_x', df.columns[1]]]
    countries_df.columns = ['identifier', 'region', 'description']
    countries_df['identifier'] = range(1, len(countries_df) + 1)

    
    # Запись DataFrame в CSV-файл
    countries_df.to_csv('data/countries.csv', index=False)
    print("Создан файл стран data/countries.csv")


def createCities():
    # Чтение исходного файла data.csv
    df = pd.read_csv('data/data.csv')

    # Чтение файла с странами
    countries_df = pd.read_csv('data/countries.csv')

    # Чтение файла с координатами стран
    coordinates_df = pd.read_csv('countries/output_convert/ne_10m_populated_places.csv')

    # Отбор уникальных городов и их стран
    unique_cities = df['Cities'].unique()
    cities_countries = df[['Cities', 'Regions', 'Dataset']]  # Столбцы "City", "Region" и "Dataset" в data.csv

    # Создание нового DataFrame с уникальными городами, странами и датасетами
    cities_df = pd.DataFrame({'identifier': range(1, len(unique_cities) + 1),
                              'country': unique_cities})

    # Объединение данных со странами и датасетами для получения идентификаторов стран
    cities_df = cities_df.merge(cities_countries.drop_duplicates(), how='left', left_on='country', right_on='Cities')
    cities_df = cities_df.merge(countries_df.drop_duplicates(), how='left', left_on='Regions', right_on='description')

    # Объединение данных с координатами стран
    cities_df = cities_df.merge(coordinates_df.drop_duplicates(subset=['NAME']), how='left', left_on='country', right_on='NAME')

    # Удаление ненужных столбцов и переименование столбцов
    cities_df = cities_df[['identifier_x', 'identifier_y', 'country', 'latitude', 'longitude', 'Dataset']]
    cities_df.columns = ['identifier', 'country', 'description', 'latitude', 'longitude', 'dataset']

    # Присвоение последовательных значений в столбце 'identifier'
    cities_df['identifier'] = range(1, len(cities_df) + 1)
    cities_df['country'] = range(1, len(cities_df) + 1)
    cities_df[['latitude', 'longitude']] = cities_df[['latitude', 'longitude']].fillna('0')

    # Запись DataFrame в CSV-файл
    cities_df.to_csv('data/cities.csv', index=False)
    print("Создан файл городов data/cities.csv")


def createMeasurement():
    # Чтение файла cities.csv
    cities_df = pd.read_csv('data/cities.csv')

    # Создание папки "measurement" или удаление существующей папки и создание новой
    measurement_dir = 'data/measurement/'
    if os.path.exists(measurement_dir):
        # Удаление существующей папки и ее содержимого
        for file_name in os.listdir(measurement_dir):
            file_path = os.path.join(measurement_dir, file_name)
            os.remove(file_path)
        os.rmdir(measurement_dir)
    os.mkdir(measurement_dir)

    # Проход по каждой записи в cities_df
    for index, row in cities_df.iterrows():
        city_id = row['identifier']
        dataset = row['dataset']

        # Путь к файлу с данными
        file_path = os.path.join('dataset/output_csv', f'{dataset}.csv')
        if os.path.exists(file_path):
            # Чтение данных из файла и запись в CSV-файл
            with open(file_path, 'r') as data_file:
                next(data_file)  # Пропуск заголовка файла

                # Создание CSV-файла для текущего набора данных
                output_file_path = os.path.join(measurement_dir, f'{dataset}.csv')
                with open(output_file_path, 'w') as output_file:
                    output_file.write('city,timestamp,temperature\n')  # Запись заголовка

                    for line in data_file:
                        parts = line.strip().split(',')
                        if int(parts[0]) >= 10:
                            mounths = parts[0]
                        else:
                            mounths = "0"+parts[0]

                        if int(parts[1]) >= 10:
                            days = parts[1]
                        else:
                            days = "0"+parts[1]

                        if mounths != "00" and days != "00":
                            timestamp = parts[2]+"-"+mounths+"-"+days+ " 00:00:00"
                            temperature = parts[3]

                            # Запись строки в CSV-файл текущего набора данных
                            output_file.write(f'{city_id},{timestamp},{temperature}\n')

    print("Созданы файлы с измерениями в папке data/measurement/")

    

def addCoastline():
    # Путь к исходному файлу coastline
    source_file = "coastline/output_convert/ne_10m_coastline.csv"
    
    # Путь к целевому файлу coastline
    target_file = "data/coastline.csv"

    # Считываем исходный файл с использованием pandas
    df = pd.read_csv(source_file, delimiter=',')

    # Создаем столбец и добавляем его в DataFrame
    df['shape'] = range(1, len(df) + 1)
    df['segment'] = range(1, len(df) + 1)

    # Оставляем только столбцы "shape segment", "latitude" и "longitude"
    df = df[['shape', 'segment', 'latitude', 'longitude']]

    # Сохраняем обновленный DataFrame в целевой файл
    df.to_csv(target_file, index=False)

    print("Файл coastline/output_convert/ne_10m_coastline.csv перемещен и дополнен.")


createRegions()
createCountries()
createCities()
createMeasurement()
addCoastline()