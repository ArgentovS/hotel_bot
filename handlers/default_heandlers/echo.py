from telebot.types import Message

from loader import bot


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message):
    bot.reply_to(message, f"Неизвестная команда {message.text}\n"
                          f"Для работы с ботом введите одну из команд, "
                          f"которые можно посмотреть в меню или в /help")
