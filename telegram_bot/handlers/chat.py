from backend.gemini_chat import ask_crop_doctor
from services.lang_utils import get_user_lang
from telebot.types import Message
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def register(bot, user_languages):
    @bot.message_handler(func=lambda msg: True)
    def chat_with_crop_doctor(message: Message):
        lang = get_user_lang(message.chat.id, user_languages)
        reply = ask_crop_doctor(message.text, lang)
        bot.send_message(message.chat.id, reply)
