#Created by Kiko with ♥ for fucking slaves


#██╗░░██╗██╗██╗░░██╗░█████╗░
#██║░██╔╝██║██║░██╔╝██╔══██╗
#█████═╝░██║█████═╝░██║░░██║
#██╔═██╗░██║██╔═██╗░██║░░██║
#██║░╚██╗██║██║░╚██╗╚█████╔╝
#╚═╝░░╚═╝╚═╝╚═╝░░╚═╝░╚════╝░


import pandas as pd

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

createRegions()
createCountries()
createCities()