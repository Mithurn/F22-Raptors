
from telebot.types import Message
from telebot import types
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.lang_utils import get_lang_from_text, set_user_lang


def register(bot, user_languages, user_data=None):
    @bot.message_handler(commands=['language'])
    def set_language(message: Message):
        kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        kb.add("English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা")
        bot.send_message(message.chat.id, "🌐 Choose your language:", reply_markup=kb)

    @bot.message_handler(func=lambda msg: msg.text in ["English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা"])
    def save_language(message: Message):
        lang_code = get_lang_from_text(message.text)
        set_user_lang(message.chat.id, lang_code, user_languages)
        if user_data is not None:
            user_data[message.chat.id] = user_data.get(message.chat.id, {})
            user_data[message.chat.id]["language"] = lang_code
        bot.send_message(message.chat.id, f"✅ Language set to {message.text}")
