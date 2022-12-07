from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def keyboard_photo_status() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_yes = KeyboardButton(text="ДА")
    button_no = KeyboardButton(text="НЕТ")
    keyboard.add(button_yes, button_no)
    return keyboard

def keyboard_number() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = KeyboardButton(text="1")
    button_2 = KeyboardButton(text="2")
    button_3 = KeyboardButton(text="3")
    button_4 = KeyboardButton(text="4")
    button_5 = KeyboardButton(text="5")
    keyboard.add(button_1, button_2, button_3, button_4, button_5)
    return keyboard

