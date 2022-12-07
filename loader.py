from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
import loguru
from datetime import date

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
