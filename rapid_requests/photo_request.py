import requests
from rapid_requests.rapid import headers
import json


def properties_get_hotel_photos(id_hotel, headers=headers):
    url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
    querystring = {"id":id_hotel}
    response = requests.request("GET", url, headers=headers, params=querystring)
    with open('properties_get_hotel_photos.txt', 'w') as file:
        file.write(response.text)


#properties_get_hotel_photos('1178275040')
with open('properties_get_hotel_photos.txt', 'r') as file:
    a = json.loads(file.read())
    print(a)

for elem in a['hotelImages']:
    print(elem)
