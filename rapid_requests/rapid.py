import requests
from requests import get
import json
from config_data import config


class SiteError(Exception):
    def __init__(self, text):
        self.txt = text



headers = {
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }


def request_to_api(url, headers, querystring):
    try:
        response = get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            print('Всё -ОК!')
            return response
    except:
        'Ошибка! Сервер не доступен или неверно сформирован запрос!'


def locations_v2_search(city, *arg, headers=headers):
    url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
    querystring = {"query": city, "locale":"ru", "currency":"RUB"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    try:
        return json.loads(response.text)['suggestions'][0]['entities'][1]['destinationId']
    except SiteError:
        print('На сайте отсутствует необходимая детализация по отелю')
        return False


def properties_list(city_code, date_start, date_finish, *args, headers=headers):

    try:
        url = 'https://hotels4.p.rapidapi.com/properties/list'
        querystring = {"destinationId": city_code, "pageNumber": "1", "pageSize": "25", "checkIn": date_start,
                       "checkOut": date_finish, "adults1": "1", "sortOrder": "PRICE",
                       "locale": "ru", "currency": "RUB"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        return json.loads(response.text)['data']['body']['searchResults']['results']
    except Exception:
        print('Нет полной информации об отеле')
        return False

def properties_get_hotel_photos(id_hotel, number_photos, *args, headers=headers):
    if number_photos > 0:
        url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
        querystring = {"id": id_hotel}
        response = requests.request("GET", url, headers=headers, params=querystring)
        with open('properties_get_hotel_photos.txt', 'w') as file:
            file.write(response.text)
        try:
            photos = []
            for elem in json.loads(response.text)['hotelImages'][:number_photos]:
                try:
                    url_photo = str(elem['baseUrl'][:-10]) + str(elem['sizes'][0]['suffix']) + str('.jpg')
                    photos.append(url_photo)
                    print('Элемент словаря:', photos[len(photos)-1])
                except SiteError:
                    print('Ошибка запроса к фотографии')
            print('Словарь:', photos)
            return photos
        except Exception:
            print('На сайте отсутствуют фотографии по отелю')
            return False
