import os
import requests
import json
from datetime import datetime

vk_access_token = ' '
user_id = ' '
yd_access_token = ' '


class VK:

    def __init__(self, access_token, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def vk_photo(self, user_id):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': user_id, 'album_id': 'profile', 'extended': '1', 'rev': '1', 'count': '5'}
        response = requests.get(url, params={**self.params, **params})
        return response.json()


class YD:

    def __init__(self, access_token):
        self.token = access_token

    def put_folder(self, user_id):
        files_url = f'https://cloud-api.yandex.net/v1/disk/resources?path={user_id}'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        response = requests.put(files_url, headers=headers)
        return response.json()

    def upload_file_link(self, user_id, filename):
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {"path": f"{user_id}/{filename}", "overwrite": "true"}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        response = requests.get(files_url, headers=headers, params=params)
        return response.json()

    def load_file(self, user_id, filename):
        result = self.upload_file_link(user_id=user_id, filename=filename)
        href = result['href']
        with open(filename, 'rb') as f:
            response = requests.put(href, files={'file': f})
            response.raise_for_status()
            if response.status_code == 201:
                print('Загрузка завершена')

    def load_file_link(self, user_id, filename, url):
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {"path": f"{user_id}/{filename}", "url": url, "overwrite": "true"}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                   'Authorization': f'OAuth {self.token}'}
        response = requests.post(files_url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 202:
            print('Загрузка фото завершена')


vk = VK(vk_access_token)
yd = YD(yd_access_token)

with open("table.json", "w", encoding="utf-8") as file:
    json_list = []
    items_photo = vk.vk_photo(user_id)['response']['items']
    print(f'Начинаем резервное копирование. \nПолучено для загрузки {len(items_photo)} фото.')
    yd.put_folder(user_id)
    i = 0
    for item in items_photo:
        data_vk = str(datetime.fromtimestamp(item['date']).strftime("%d.%m.%Y"))
        name_photo = str(item['likes']['count']) + '.jpg'
        sizes = item['sizes'][-1]['type']
        name_photo_data = str(name_photo[:-4] + "_" + data_vk + '.jpg')
        photo_url = item['sizes'][-1]['url']
        for dic in json_list:
            if name_photo == dic['file_name']:
                name_photo = name_photo_data

            else:
                name_photo = name_photo

        json_list.append({'file_name': name_photo, 'size': sizes})
        i += 1
        print(f'Начата загрузка {i} из {len(items_photo)} фото.')
        yd.load_file_link(user_id, name_photo, photo_url)
    json.dump(json_list, file, indent=4)
print('Начинаем загрузку json, каталога.')
yd.load_file(user_id, "table.json")
os.remove("table.json")
print('Резервное копирование завершено! ')
