import loguru
import os
from rapid_requests import dispatcher, rapid
from loader import bot
from states.states_group import UserParameterState
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import timedelta, date, datetime
from keyboards.reply.photo_status import keyboard_number, keyboard_photo_status


loguru.logger.info(f'Запустили бота на отслеживание команд: {os.uname()}')
date.today()

def print_info(bot, message, info):
    bot.send_message(message.from_user.id,
                     f'<b><i>{message.from_user.first_name}</i></b>, твой запрос:\n'
                     f'Дата заезда - {info["date_start"]}\n'
                     f'Дата выезда - {info["date_finish"]}\n'
                     f'В городе - {info["city"]}\n'
                     f'Минимальная цена - {info["price_range_low"]}\n'
                     f'Максимальная цена - {info["price_range_high"]}\n'
                     f'Удаление от центра города - {info["distance"]}\n'
                     f'Найти отели в количестве - {info["number_hotels"]}\n'
                     f'Вывести фотографии - {info["photo"]}\n'
                     f'Количество фотографий - {info["number_photos"]}',
                     parse_mode='html')
    bot.send_message(message.from_user.id, '\n... ищу информацию ...\n')
    loguru.logger.info(f'Бот начал поиск отелей по запросу: {info}')

    hotels = dispatcher.hotels_result(info["user"], info["command"], info["city_code"],
                                      info["date_start"], info["date_finish"],
                                      info["number_hotels"],
                                      info["price_range_low"], info["price_range_high"], info["distance"])
    if hotels:
        n = 0
        for hotel in hotels:
            bot.send_message(message.from_user.id,
                             f'\n<i><b>Вариант №{n +1}:</b></i>\n'
                             f'Отель: {hotel[0]},\n'
                             f'адрес: {hotel[1][1]},\n'
                             f'от центра: {round(hotel[1][2] * 1.609344, 1)} км,\n'
                             f'цена: {int(round(hotel[1][3], 0))} руб./сутки\n'
                             f'сайт отеля: {str("https://www.hotels.com/ho") + str(hotel[1][0])}\n'
                             f'стоимость проживания: {int(round(hotel[1][3] * int(info["length_stay"]), 0))} руб.',
                             parse_mode='html')
            if info['number_photos'] > 0:
                photos = dispatcher.photos(hotel[1][0], info['number_photos'])
                bot.send_media_group(message.chat.id, [InputMediaPhoto(photo) for photo in photos])
            n += 1
        bot.send_message(message.from_user.id, 'Закончили поиск отелей. Можешь вводить новый запрос!')
    else:
        bot.send_message(message.from_user.id,
                         f'\nОтелей по заданным характеристикам нет. Попробуй изменить данные\n', parse_mode='html')
    loguru.logger.info(f'Бот вывел результаты запроса: {hotels}')


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def get_command(message: Message) -> None:
    loguru.logger.info(f'Шаг 0: Начальный статус состояния бота: {bot.get_state(message.from_user.id)}')
    bot.send_message(message.from_user.id, f'Начнём поиск отелей, <b>{message.from_user.first_name}</b>!\n'
                                           f'Введи город для поиска отелей', parse_mode='html')
    bot.set_state(message.from_user.id, UserParameterState.city, message.chat.id)
    loguru.logger.info(f'Шаг 0.1: Статус состояния бота {bot.get_state(message.from_user.id)}')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
        info['command'] = message.text
        info['user'] = (message.from_user.id, message.from_user.username)
    loguru.logger.info(f'Шаг 0.2: Записали поданную боту команду: {info}')


@bot.message_handler(state=UserParameterState.city)
def get_city(message: Message) -> None:
    loguru.logger.info(f'Шаг 1: Статус состояния бота {bot.get_state(message.from_user.id)}')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
        info['city'] = message.text
        loguru.logger.info(f'Пополнили запрос наименованием города: {info}')
        try:
            info['city_code'] = dispatcher.city_exist(info['city'])
        except Exception:
            print('Ошибка! Город не существует')
            info['city_code'] = False
            bot.send_message(message.from_user.id,
                             f'<i><b>По отелям города "{info["city"]}" на сайте нет информации</b></i>\n'
                             f'...попробуй другой город...',
                             parse_mode='html')
    if message.text.replace(' ', '').replace('-', '').isalpha():
        loguru.logger.info(f'Шаг 2.0: Статус состояния бота {bot.get_state(message.from_user.id)}  | info: {info}')
        if info['city_code']:
            bot.set_state(message.from_user.id, UserParameterState.date_start)
            loguru.logger.info(f'Шаг 2.1: Статус состояния бота {bot.get_state(message.from_user.id)}  | info: {info}')
            get_date(message)
    else:
        loguru.logger.info(f'Шаг 2.2: В названии города не только буквы. Статус состояния бота {bot.get_state(message.from_user.id)}  | info: {info}')
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>!\n'
                         f'в наименовании города могут быть только буквы\n'
                         f'попробуй ещё раз', parse_mode='html')


@bot.message_handler(state=UserParameterState.date_start)
def get_date(message):
    loguru.logger.info(f'Шаг 3: Статус состояния бота: {bot.get_state(message.from_user.id)}')
    calendar, step = DetailedTelegramCalendar(min_date=date.today()).build()
    bot.send_message(message.chat.id, f"Для начала выбери {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar(min_date=date.today()).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Теперь выбери {LSTEP[step]}",
                              c.message.chat.id, c.message.message_id, reply_markup=key)
    elif result:
        bot.edit_message_text(f"Заезд {result}", c.message.chat.id, c.message.message_id)
        with bot.retrieve_data(c.from_user.id, c.message.chat.id) as info:
            info['date_start'] = result
        bot.set_state(c.from_user.id, UserParameterState.length_stay)
        loguru.logger.info(f'Шаг 4: Статус состояния бота: {bot.get_state(c.message.from_user.id)} | info: {info}')
        bot.send_message(c.from_user.id, f'<b>{c.message.from_user.first_name}</b>!\n'
                                         f'Введи продолжительность проживания (дни)', parse_mode='html')


@bot.message_handler(state=UserParameterState.length_stay)
def get_length_stay(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
            info['length_stay'] = int(message.text)
            info['date_finish'] = info["date_start"] + timedelta(days=info["length_stay"])

        if info['command'] == '/bestdeal':
            bot.send_message(message.from_user.id,
                             f'<b>{message.from_user.first_name}</b>!\n'
                             f'введи минимальную стоимость (руб/сутки)\n', parse_mode='html')
            bot.set_state(message.from_user.id, UserParameterState.price_range_low)
            loguru.logger.info(f'Шаг 5: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')
        else:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
                info['price_range_low'] = 'не задана'
                info['price_range_high'] = 'не задана'
                info['distance'] = 'не задано'
            bot.send_message(message.from_user.id,
                             f'<b>{message.from_user.first_name}</b>!\n'
                             f'какое количество отелей вывести (не более 5)\n',
                             parse_mode='html', reply_markup=keyboard_number())
            bot.set_state(message.from_user.id, UserParameterState.number_hotels)
            loguru.logger.info(f'Шаг 5.1: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')

    else:
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>!\n'
                         f'продолжительность должна быть указана числом\n', parse_mode='html')
        loguru.logger.info(f'Шаг 5.2: Статус состояния бота: {bot.get_state(message.from_user.id)}')


@bot.message_handler(state=UserParameterState.price_range_low)
def get_price_range_low(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
            info['price_range_low'] = int(message.text)
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>,\n'
                         f'введи максимальную стоимость отеля (руб/сутки)\n', parse_mode='html')
        bot.set_state(message.from_user.id, UserParameterState.price_range_high, message.chat.id)
        loguru.logger.info(f'Шаг 6: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')
    else:
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>!\n'
                         f'цена должна быть указана числом\n', parse_mode='html')


@bot.message_handler(state=UserParameterState.price_range_high)
def get_price_range_high(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
            info['price_range_high'] = int(message.text)
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>,\n'
                         f'введи удаление отеля от центра города (км)\n',
                         parse_mode='html')
        bot.set_state(message.from_user.id, UserParameterState.distance, message.chat.id)
        loguru.logger.info(f'Шаг 7: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')
    else:
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>!\n'
                         f'цена должна быть указана числом\n', parse_mode='html')


@bot.message_handler(state=UserParameterState.distance)
def get_distance(message: Message) -> None:
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
            info['distance'] = int(message.text)
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>,\n'
                         f'введи количество отелей, поиском которых необходимо ограничиться (но не более 5)',
                         parse_mode='html', reply_markup=keyboard_number())
        bot.set_state(message.from_user.id, UserParameterState.number_hotels, message.chat.id)
        loguru.logger.info(f'Шаг 8: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')
    else:
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>!\n'
                         f'расстояние должно быть указано числом\n',
                         parse_mode='html')


@bot.message_handler(content_types=['text'], state=UserParameterState.number_hotels)
def get_number_hotels(message: Message) -> None:
    if message.text.isdigit() and (1 <= int(message.text) <= 5):
        with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
            info['number_hotels'] = int(message.text)
        loguru.logger.info(f'Шаг 9: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>,\n'
                         f'необходимо ли выводить фото отеля?\n'
                         f'\nвведи да - если необходимо выводить фото\n',
                         parse_mode='html', reply_markup=keyboard_photo_status())
        bot.set_state(message.from_user.id, UserParameterState.photo, message.chat.id)
        loguru.logger.info(f'Шаг 10: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')
    else:
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>!\n'
                         f'цифра должна быть целым числом (от 1 до 5)\n'
                         f'попробуй ещё раз', parse_mode='html')


@bot.message_handler(content_types=['text'], state=UserParameterState.photo)
def get_photo(message: Message) -> None:
    if message.text.lower() in ['д', 'да', 'y', 'yes']:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
            info['photo'] = 'да'
        bot.send_message(message.from_user.id,
                         f'<b>{message.from_user.first_name}</b>,\n'
                         f'введи количество фото (но не более 5)\n',
                         parse_mode='html', reply_markup=keyboard_number())
        bot.set_state(message.from_user.id, UserParameterState.number_photos, message.chat.id)
        loguru.logger.info(f'Шаг 11: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')
    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
            info['photo'] = 'нет'
            info['number_photos'] = 0
        bot.send_message(message.from_user.id, 'Запись закончена!\n', parse_mode='html')
        bot.delete_state(message.from_user.id,message.chat.id)
        loguru.logger.info(f'Шаг 12: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')
        print_info(bot, message, info)


@bot.message_handler(content_types=['text'], state=UserParameterState.number_photos)
def get_number_photos(message: Message) -> None:
        if message.text.isdigit() and (1 <= int(message.text) <= 5):
            with bot.retrieve_data(message.from_user.id, message.chat.id) as info:
                info['number_photos'] = int(message.text)
            bot.send_message(message.from_user.id, f'Запись закончена!\n', parse_mode='html')
            bot.set_state(message.from_user.id, UserParameterState.date_start, message.chat.id)
            print_info(bot, message, info)
            bot.delete_state(message.from_user.id, message.chat.id)
            loguru.logger.info(f'Шаг 14: Статус состояния бота: {bot.get_state(message.from_user.id)} | info: {info}')
        else:
            bot.send_message(message.from_user.id,
                             f'<b>{message.from_user.first_name}</b>\n'
                             f'цифра должна быть целым числом (от 1 до 5)\n'
                             f'попробуй ещё раз', parse_mode='html')
