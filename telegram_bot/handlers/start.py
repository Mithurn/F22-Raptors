from telebot.types import Message
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import pandas as pd
from telegram_bot.user_persistence import save_user_data
import telebot.types as types
from services.lang_utils import get_lang_from_text, set_user_lang

def register(bot, user_data=None):
    @bot.message_handler(commands=['start'])
    def send_welcome(message: Message):
        info = user_data.get(message.chat.id, {}) if user_data else {}
        if not info.get("language"):
            kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            kb.add("English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা")
            bot.send_message(message.chat.id, "🌐 Please select your language:", reply_markup=kb)
        elif not info.get("location"):
            bot.send_message(message.chat.id, "📍 Please tell me your farm location (district or region) in the format: Location: <your location>")
        else:
            send_help(message)

    @bot.message_handler(func=lambda msg: msg.text in ["English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা"])
    def save_language(message):
        lang_code = get_lang_from_text(message.text)
        set_user_lang(message.chat.id, lang_code, user_languages)
        if user_data is not None:
            user_data[message.chat.id] = user_data.get(message.chat.id, {})
            user_data[message.chat.id]["language"] = lang_code
            save_user_data(user_data)
        bot.send_message(message.chat.id, f"✅ Language set to {message.text}")
        # Prompt for location after language
        bot.send_message(message.chat.id, "📍 Please tell me your farm location (district or region) in the format: Location: <your location>")

    # Accept any text as location if language is set but location is not
    @bot.message_handler(func=lambda msg: user_data and user_data.get(msg.chat.id, {}).get("language") and not user_data.get(msg.chat.id, {}).get("location") and msg.text and not msg.text.startswith("/"))
    def save_location_onboarding(message: Message):
        location = message.text.strip()
        lang = user_data[message.chat.id]["language"]
        csv_path = f"backend/DATASETS/risk_data_{lang}.csv"
        try:
            df = pd.read_csv(csv_path)
            regions = df["Region"].astype(str).str.lower().tolist()
        except Exception as e:
            bot.reply_to(message, "❌ Could not load region data. Please try again later.")
            print(f"CSV load error: {e}")
            return
        if location.lower() not in regions:
            sample = ', '.join(df["Region"].astype(str).tolist()[:5])
            bot.reply_to(message, f"❌ Location not found. Available regions include: {sample} ...")
            return
        if user_data is not None:
            user_data[message.chat.id] = user_data.get(message.chat.id, {})
            user_data[message.chat.id]["location"] = location
            user_data[message.chat.id]["alerts"] = True  # Enable alerts only after location is set
            save_user_data(user_data)
        bot.reply_to(message, f"✅ Location saved as: {location}")
        # Show help after both language and location are set
        help_msg = """
*How to use this bot:*

1️⃣ /start — Begin and set up your profile
2️⃣ /language — Change your preferred language
3️⃣ /location — Set or update your farm location
4️⃣ /myalerts — Enable automatic alerts
5️⃣ /stopalerts — Disable automatic alerts
6️⃣ /status — View your current settings
7️⃣ /about — About this bot
8️⃣ *Send a crop photo* — I’ll detect diseases and suggest remedies
9️⃣ *Type your question* — I’ll answer with expert advice (in your language)
🔔 Alerts are sent every 10 seconds for demo purposes.
_I support English, Hindi, Tamil, Telugu, and Bengali._
If you need help, just type /help anytime!
"""
        sent = bot.send_message(message.chat.id, help_msg, parse_mode="Markdown")
        try:
            bot.pin_chat_message(message.chat.id, sent.message_id)
        except Exception as e:
            print(f"Could not pin help message: {e}")

    # Accept any text as location after /location command
    @bot.message_handler(func=lambda msg: user_data and user_data.get(msg.chat.id, {}).get("language") and msg.text and user_data.get(msg.chat.id, {}).get("location") and not msg.text.startswith("/"))
    def update_location(message: Message):
        location = message.text.strip()
        lang = user_data[message.chat.id]["language"]
        csv_path = f"backend/DATASETS/risk_data_{lang}.csv"
        try:
            df = pd.read_csv(csv_path)
            regions = df["Region"].astype(str).str.lower().tolist()
        except Exception as e:
            bot.reply_to(message, "❌ Could not load region data. Please try again later.")
            print(f"CSV load error: {e}")
            return
        if location.lower() not in regions:
            sample = ', '.join(df["Region"].astype(str).tolist()[:5])
            bot.reply_to(message, f"❌ Location not found. Available regions include: {sample} ...")
            return
        if user_data is not None:
            user_data[message.chat.id]["location"] = location
            save_user_data(user_data)
        bot.reply_to(message, f"✅ Location updated to: {location}")

    # Block all other actions until setup is complete
    @bot.message_handler(func=lambda msg: not (user_data and user_data.get(msg.chat.id, {}).get("language") and user_data.get(msg.chat.id, {}).get("location")))
    def block_until_setup(message: Message):
        info = user_data.get(message.chat.id, {}) if user_data else {}
        if not info.get("language"):
            kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            kb.add("English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা")
            bot.send_message(message.chat.id, "🌐 Please select your language:", reply_markup=kb)
        elif not info.get("location"):
            bot.send_message(message.chat.id, "📍 Please tell me your farm location (district or region) in the format: Location: <your location>")

    @bot.message_handler(commands=['location'])
    def ask_location(message: Message):
        bot.reply_to(message, "📍 Please type your farm location (district or region):")

    @bot.message_handler(commands=['status'])
    def status(message: Message):
        info = user_data.get(message.chat.id, {}) if user_data else {}
        lang_map = {"en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali"}
        lang = lang_map.get(info.get("language", "en"), "English")
        location = info.get("location", "Not set")
        alerts = info.get("alerts", True)
        alerts_str = "ON" if alerts else "OFF"
        msg = f"🌐 Language: {lang}\n📍 Location: {location}\n🔔 Alerts: {alerts_str}"
        bot.reply_to(message, msg)

    @bot.message_handler(commands=['about'])
    def about(message: Message):
        msg = (
            "🤖 *KRISHI-RAKSHAK*\n"
            "AI-powered, multilingual Telegram bot for farmers.\n"
            "- Diagnose crop diseases from photos\n"
            "- Get remedies and advice in 5 languages\n"
            "- Receive personalized farm alerts\n"
            "Built by Mithurn and team."
        )
        bot.reply_to(message, msg, parse_mode="Markdown")

    @bot.message_handler(commands=['help'])
    def send_help(message: Message):
        help_msg = """
*How to use this bot:*

1️⃣ /start — Begin and set up your profile
2️⃣ /language — Change your preferred language
3️⃣ /location — Set or update your farm location
4️⃣ /myalerts — Enable automatic alerts
5️⃣ /stopalerts — Disable automatic alerts
6️⃣ /status — View your current settings
7️⃣ /about — About this bot
8️⃣ *Send a crop photo* — I’ll detect diseases and suggest remedies
9️⃣ *Type your question* — I’ll answer with expert advice (in your language)
🔔 Alerts are sent every 10 seconds for demo purposes.
_I support English, Hindi, Tamil, Telugu, and Bengali._
If you need help, just type /help anytime!
"""
        sent = bot.reply_to(message, help_msg, parse_mode="Markdown")
        try:
            bot.pin_chat_message(message.chat.id, sent.message_id)
        except Exception as e:
            print(f"Could not pin help message: {e}")

    @bot.message_handler(commands=['alert'])
    def send_alerts(message: Message):
        if user_data is None:
            bot.reply_to(message, "User data not available.")
            return
        count = 0
        for user_id, info in user_data.items():
            lang = info.get("language", "en")
            location = info.get("location")
            if not location:
                continue
            csv_path = f"backend/DATASETS/risk_data_{lang}.csv"
            try:
                df = pd.read_csv(csv_path)
                row = df[df["Region"] == location]
                if not row.empty:
                    risk = row.iloc[0]["Overall_Risk"]
                    suggestion = row.iloc[0]["Suggestion"]
                    msg = f"⚠️ Alert for {location}:\nRisk: {risk}\nAdvice: {suggestion}"
                    bot.send_message(user_id, msg)
                    count += 1
            except Exception as e:
                print(f"Alert error for user {user_id}: {e}")
        bot.reply_to(message, f"✅ Sent alerts to {count} users.")

    # Catch-all handler for unknown commands or messages
    @bot.message_handler(func=lambda msg: msg.text and not msg.text.startswith('/'))
    def unknown_command(message: Message):
        bot.reply_to(message, "❓ Sorry, I didn’t understand that. Type /help for a list of commands.")
