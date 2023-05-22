#Created by Kiko(Zhukov Kirill) with ♥

#██╗░░██╗██╗██╗░░██╗░█████╗░
#██║░██╔╝██║██║░██╔╝██╔══██╗
#█████═╝░██║█████═╝░██║░░██║
#██╔═██╗░██║██╔═██╗░██║░░██║
#██║░╚██╗██║██║░╚██╗╚█████╔╝
#╚═╝░░╚═╝╚═╝╚═╝░░╚═╝░╚════╝░

import os
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

def download_files(url, extension):
    dataset_dir = 'dataset'

    # Создаем папку "dataset" (если она не существует)
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    else:
        # Очищаем папку "dataset"
        for file in os.listdir(dataset_dir):
            file_path = os.path.join(dataset_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    response = requests.get(url)
    content = response.text

    soup = BeautifulSoup(content, 'html.parser')
    txt_links = [link.get('href') for link in soup.find_all('a') if link.get('href').endswith(extension)]

    session = requests.Session()

    for link in tqdm(txt_links, desc='Загрузка файлов', unit='файл'):
        file_url = requests.compat.urljoin(url, link)
        file_name = os.path.join(dataset_dir, os.path.basename(link))

        # Загружаем файл
        response = session.get(file_url, stream=True)
        response.raise_for_status()
        
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

# Пример использования
url = 'https://academic.udayton.edu/kissock/http/Weather/citylistWorld.htm'
extension = '.txt'

download_files(url, extension)
