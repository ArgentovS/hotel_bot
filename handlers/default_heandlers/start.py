from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message,
                 f'Привет, <b>{message.from_user.first_name}</b>!', parse_mode='html')

