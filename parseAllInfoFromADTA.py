#Created by Kiko with ♥ for fucking slaves


#██╗░░██╗██╗██╗░░██╗░█████╗░
#██║░██╔╝██║██║░██╔╝██╔══██╗
#█████═╝░██║█████═╝░██║░░██║
#██╔═██╗░██║██╔═██╗░██║░░██║
#██║░╚██╗██║██║░╚██╗╚█████╔╝
#╚═╝░░╚═╝╚═╝╚═╝░░╚═╝░╚════╝░

import requests
from bs4 import BeautifulSoup
import csv
import re

link = "https://academic.udayton.edu/kissock/http/Weather/citylistWorld.htm"


def find_dataset(text):
    pattern = r'\b\w+\.txt\b'
    matches = re.findall(pattern, text)
    return matches


online = requests.get(link)
soup = BeautifulSoup(online.content, "html.parser")
find = soup.findAll("li", {"class": "MsoNormal"})
i = 0

cities = []
regions = []
realRegions = []

city_list = soup.findAll("li", {"class": "MsoNormal"})
for item in city_list:
    city = item.text.partition('(')[0].strip()
    cities.append(city)

    region = item.find_previous("p").text.strip()
    if region:
        regions.append(region)

    region_span = item.find_previous("span", style="mso-bidi-font-size:10.0pt;font-family:Arial")
    region = region_span.text if region_span else ""
    realRegions.append(region)

data = []

for item in find:
    result = find_dataset(item.text)
    osn = ''.join(result)
    dataset = osn[:len(osn) - 4]

    countries = regions[i]

    region_span = item.find("span", style="mso-bidi-font-size:10.0pt;font-family:Arial")
    region = realRegions[i]
    country_spans = item.findAll("span", style=re.compile(r".*color:maroon.*"))
    for span in country_spans:
        country = re.sub(r'[\[\]\r\n]', '', span.text).strip()
        if country:
            countries += ", " + country

    if region or countries or cities[i] or dataset:
        data.append([region, countries, cities[i], dataset])

    i += 1


# Запись данных в файл CSV
filename = "data.csv"

with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Regions", "Countries", "Cities", "Dataset"])
    writer.writerows(data)

print("Данные успешно сохранены в файл:", filename)
