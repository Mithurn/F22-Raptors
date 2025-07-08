import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import telebot
from dotenv import load_dotenv
from telebot.types import Message
from backend.image_classification import detect_crop_disease
from backend.gemini_chat import ask_crop_doctor

# Load token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Store language of user
user_languages = {}  

# Start 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,  welcome_msg = """
🌾 *Hello Dear Farmer!* 🌾

I’m here to help protect your crops *and* your well-being. Here’s how I can help you today:

1. *Send a crop photo* → I’ll diagnose diseases/nutrient deficiencies.  
2. *Type your problem* (e.g. "crops failed") →

💬 *Just send a message – I understand simple words!*  


_One message could save your farm…_ 🌻  
""")

# Language selection 
@bot.message_handler(commands=['language'])
def set_language(message):
    lang_keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    lang_keyboard.add("English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা")
    bot.send_message(message.chat.id, "🌐 Choose your language:", reply_markup=lang_keyboard)

# Save language 
@bot.message_handler(func=lambda msg: msg.text in ["English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা"])
def save_language(message):
    lang_map = {
        "English": "en", "हिन्दी": "hi", "தமிழ்": "ta", "తెలుగు": "te", "বাংলা": "bn"
    }
    user_languages[message.chat.id] = lang_map[message.text]
    bot.send_message(message.chat.id, f"✅ Language set to {message.text}")

# Handle photos
@bot.message_handler(content_types=['photo'])
def handle_photo(message: Message):
    print(f"📷 Photo received from {message.from_user.username}")

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("temp.jpg", 'wb') as f:
        f.write(downloaded_file)

    lang = user_languages.get(message.chat.id, "en")  
    result = detect_crop_disease("temp.jpg", lang)
    bot.reply_to(message, result)

# Handle general questions 
@bot.message_handler(func=lambda msg: True)
def chat_with_crop_doctor(message):
    user_id = message.chat.id
    language = user_languages.get(user_id, "en")  
    print(f"🗣️ Question from {user_id} in {language}: {message.text}")
    
    reply = ask_crop_doctor(message.text, language)
    bot.send_message(message.chat.id, reply)

# Start polling
if __name__ == "__main__":
    print("🤖 Bot is polling...")
    bot.infinity_polling()
