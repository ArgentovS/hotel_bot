from telebot.types import Message
from database import db_maintenance
from loader import bot


@bot.message_handler(commands=['history'])
def bot_history(message: Message):
    history = db_maintenance.user_history(message.from_user.id)
    if history:
        bot.reply_to(message,
                     f'История твоих запросов, <b>{message.from_user.first_name}</b>:\n'
                     , parse_mode='html')
        for request in history:
            bot.send_message(message.from_user.id,
                             f'Дата {request[0][0:19]}\n'
                             f'Команда: {request[1]}\n'
                             f'Отели: {request[2]}')
    else:
        bot.reply_to(message,
                     f'<b>{message.from_user.first_name}</b>, у тебя пока нет истории запросов!',
                     parse_mode='html')
