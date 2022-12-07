from rapid_requests import rapid, sort_hotel
from database import db_maintenance
from datetime import datetime, timedelta


def city_exist(city):
        return rapid.locations_v2_search(city)


def hotels_result(user, command, city_code, data_start, data_finish, number_hotels, price_range_low, price_range_high, distance):
    request_hotels = rapid.properties_list(city_code, data_start, data_finish)
    if request_hotels:
        number_day = (data_finish - data_start).days
        if command in ['/lowprice', '/highprice']:
            result = sort_hotel.get_price_hotel(request_hotels, number_day, number_hotels, command)
        else:
            result = sort_hotel.get_best_hotel(request_hotels, number_day, number_hotels,
                                               price_range_low, price_range_high, distance)
        db_maintenance.record_request((user, command, [(hotel[1][0], hotel[0]) for hotel in result]))
        return result
    else:
        return False


def photos(id_hotel, number_photos):
    return rapid.properties_get_hotel_photos(id_hotel, number_photos)