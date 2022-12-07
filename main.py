from loader import bot
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands
import handlers
import loguru
from datetime import date


loguru.logger.add('logfile.log', level='DEBUG', format='{time}  |  {level}  |  {message}',
                  rotation='1000KB', compression="zip", backtrace=True, diagnose=True)


# Стартовая процедура
if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    bot.infinity_polling()

    loguru.logger.info(f'Остановили бота: {date.today()}')
