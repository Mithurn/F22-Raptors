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
