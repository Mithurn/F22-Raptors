from backend.image_classification import detect_crop_disease
from services.lang_utils import get_user_lang
from services.file_utils import save_photo_temp
from telebot.types import Message
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.lang_utils import get_lang_from_text, set_user_lang


def handle_photo(bot, message, user_languages):
    lang = get_user_lang(message.chat.id, user_languages)
    path = save_photo_temp(bot, message)
    result = detect_crop_disease(path, lang)
    bot.reply_to(message, result)


def register(bot, user_languages):
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message: Message):
        lang = get_user_lang(message.chat.id, user_languages)
        path = save_photo_temp(bot, message)
        result = detect_crop_disease(path, lang)
        # Try to extract disease and advice from result string
        if result.startswith('🧪 Detected:'):
            # Parse the result for disease and remedy
            lines = result.split('\n')
            disease_line = next((l for l in lines if l.startswith('- ')), None)
            advice_line = next((l for l in lines if l.startswith('💊 Remedy:')), None)
            disease = disease_line[2:] if disease_line else 'Unknown disease'
            advice = advice_line[10:] if advice_line else 'No advice available.'
            reply = (
                f"🖼️ Thanks for sending your crop photo!\n"
                f"🤖 Our system detected: {disease}.\n"
                f"💡 Suggested action: {advice}.\n"
                f"For more help, you can ask a question or contact your local agri officer."
            )
        else:
            reply = f"🖼️ Thanks for sending your crop photo!\n{result}\nFor more help, you can ask a question or contact your local agri officer."
        bot.reply_to(message, reply)
