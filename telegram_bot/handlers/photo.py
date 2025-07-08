from backend.image_classification import detect_crop_disease
from services.lang_utils import get_user_lang
from services.file_utils import save_photo_temp
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.lang_utils import get_lang_from_text, set_user_lang


def handle_photo(bot, message, user_languages):
    lang = get_user_lang(message.chat.id, user_languages)
    path = save_photo_temp(bot, message)
    result = detect_crop_disease(path, lang)
    bot.reply_to(message, result)
from backend.image_classification import detect_crop_disease
from services.lang_utils import get_user_lang
from services.file_utils import save_photo_temp
from telebot.types import Message

def register(bot, user_languages):
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message: Message):
        lang = get_user_lang(message.chat.id, user_languages)
        path = save_photo_temp(bot, message)
        result = detect_crop_disease(path, lang)
        bot.reply_to(message, result)
