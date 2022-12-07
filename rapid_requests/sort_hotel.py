import typing


def get_hotel(request: list, numder_day: int) -> list:
    hotels = {}
    for hotel in request:
        if 'ratePlan' in hotel and 'price' in hotel['ratePlan'] \
                and 'distance' in hotel['landmarks'][0] \
                and 'address' in hotel and 'streetAddress' in hotel['address']:
            hotels[hotel['name']] = (hotel['id'], hotel['address']['streetAddress'],
                                     round(float(hotel['landmarks'][0]['distance'].split()[0]), 2),
                                     round(float(hotel['ratePlan']['price']['exactCurrent']), 2),
                                     round(hotel['ratePlan']['price']['exactCurrent'] * numder_day, 2))
    return list(sorted(hotels.items(), key=lambda x: int(x[1][3])))


def get_price_hotel(request: list, numder_day: int, number_hotel: int, command: str) -> list:

    hotels = get_hotel(request, numder_day)
    if number_hotel > len(hotels): number_hotel = len(hotels)

    if command == '/lowprice':
        return hotels[0:number_hotel]
    else:
        return hotels[-number_hotel:]


def get_best_hotel(request: list, numder_day: int, number_hotel: int, price_range_low: float, price_range_high: float, distance: float) -> list:
    hotels = get_hotel(request, numder_day)
    return [hotel for hotel in \
            [hotel for hotel in hotels if price_range_low <= hotel[1][3] <= price_range_high] \
            if hotel[1][2] <= distance][0:number_hotel]
