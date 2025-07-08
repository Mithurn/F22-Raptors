from telegram_bot.handlers import start, language, photo, chat
from telebot import TeleBot
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()
bot = TeleBot(os.getenv("BOT_TOKEN"))
user_languages = {}

# Register handlers
start.register(bot)
language.register(bot, user_languages)
photo.register(bot, user_languages)
chat.register(bot, user_languages)

if __name__ == "__main__":
    print("🤖 Bot is polling...")
    bot.infinity_polling()
