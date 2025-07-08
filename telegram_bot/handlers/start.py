from telebot.types import Message
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def register(bot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message: Message):
        msg = (
            "🌾 *Hello Dear Farmer!* 🌾\n\n"
            "1. *Send a crop photo* → I’ll diagnose it.\n"
            "2. *Type your problem* → I’ll give advice.\n\n"
            "💬 Just message me — I understand simple words!"
        )
        bot.reply_to(message, msg, parse_mode="Markdown")

    @bot.message_handler(commands=['help'])
    def send_help(message: Message):
        help_msg = (
            "*How to use this bot:*\n\n"
            "1️⃣ *Send a crop photo* — I’ll detect diseases and suggest remedies.\n"
            "2️⃣ *Type your question* — I’ll answer with expert advice (in your language).\n"
            "3️⃣ */language* — Change your preferred language.\n"
            "4️⃣ *Say hi/hello* \n\n"
            "_I support English, Hindi, Tamil, Telugu, and Bengali.\n"
            "If you need help, just type /help anytime!_"
        )
        bot.reply_to(message, help_msg, parse_mode="Markdown")
