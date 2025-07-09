from telegram_bot.handlers import start, language, photo, chat
from telebot import TeleBot
import os
from dotenv import load_dotenv
import sys
import threading
import time
import pandas as pd
import json
from telegram_bot.user_persistence import save_user_data, user_data_path
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()
user_data = {}

last_alert_time = {}

# Define ADMIN_USER_ID at the top so it is available everywhere
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))

# Load user_data from file if it exists
if os.path.exists(user_data_path):
    with open(user_data_path, 'r') as f:
        user_data = json.load(f)
    print(f"[DEBUG] Loaded user_data at startup: {user_data}")
    # Migration: ensure last_alert_time is set for all users with alerts and location
    import time
    for user_id, info in user_data.items():
        if info.get("alerts", False) and info.get("location") and last_alert_time.get(user_id) is None:
            last_alert_time[user_id] = time.time() + 30
            print(f"[DEBUG] Migrated last_alert_time for user {user_id} at startup: {last_alert_time[user_id]} (30s in future)")
else:
    user_data = {}

bot = TeleBot(os.getenv("BOT_TOKEN"))
user_languages = {}


def register_all_handlers():
    start.register(bot, user_languages, user_data)
    language.register(bot, user_languages, user_data)
    photo.register(bot, user_languages)  # Only 2 args
    chat.register(bot, user_languages, user_data)

register_all_handlers()


def alert_sender():
    while True:
        # Always reload user_data from disk to get the latest state
        global user_data
        try:
            with open(user_data_path, 'r') as f:
                user_data = json.load(f)
        except Exception as e:
            logging.error(f"Failed to reload user_data: {e}")
        now = time.time()
        for user_id, info in user_data.items():
            # SKIP admin for region alerts
            if str(user_id) == str(ADMIN_USER_ID):
                continue
            # Only send if alerts are enabled for this user
            if not info.get("alerts", True):
                continue
            lang = info.get("language", "en")
            location = info.get("location")
            if not location:
                continue
            # Default alert frequency is 10 seconds
            frequency = info.get("alert_frequency", 10)
            # Ensure last_alert_time is set 30 seconds after onboarding
            last_time = last_alert_time.get(user_id)
            if last_time is None:
                # Set last_alert_time to now + 30 seconds after onboarding
                last_alert_time[user_id] = now + 30
                continue
            if now - last_time < frequency:
                continue
            csv_path = f"backend/DATASETS/risk_data_{lang}.csv"
            try:
                df = pd.read_csv(csv_path)
                user_loc_norm = location.strip().lower()
                df["Region_norm"] = df["Region"].astype(str).str.strip().str.lower()
                row = df[df["Region_norm"] == user_loc_norm]
                if not row.empty:
                    soil = row.iloc[0]["Soil_Health"]
                    water = row.iloc[0]["Groundwater_Status"]
                    risk = row.iloc[0]["Overall_Risk"]
                    suggestion = row.iloc[0]["Suggestion"]
                    region = row.iloc[0]["Region"]
                    precautions = [s.strip() for s in suggestion.replace(';', ',').split(',') if s.strip()]
                    precautions_text = '\n'.join([f"- {p}" for p in precautions]) if precautions else "- No specific precautions listed."
                    alert_message = f"{risk} detected for your region."
                    msg = (
                        f"⚠️ *Region Alert for {region}:*\n\n"
                        f"{alert_message}\n\n"
                        f"🌱 *Precautions:*\n{precautions_text}\n\n"
                        f"Please take these steps to protect your crops. For more advice, use /help or ask a question anytime!"
                    )
                    # Send alert to farmer
                    bot.send_message(user_id, msg, parse_mode="Markdown")
                    # Send same alert to admin
                    try:
                        bot.send_message(ADMIN_USER_ID, f"[Farmer {user_id}]\n" + msg, parse_mode="Markdown")
                    except Exception as e:
                        logging.error(f"Admin notification error: {e}")
                    last_alert_time[user_id] = now
            except Exception as e:
                logging.error(f"Alert error for user {user_id}: {e}")
        time.sleep(1)

# Start alert sender in background
if __name__ == "__main__":
    t = threading.Thread(target=alert_sender, daemon=True)
    t.start()
    print("🤖 Bot is polling...")
    bot.infinity_polling()

# Handler to stop alerts for a user
@bot.message_handler(commands=['stopalerts'])
def stop_alerts(message):
    user_data[message.chat.id] = user_data.get(message.chat.id, {})
    user_data[message.chat.id]["alerts"] = False
    save_user_data(user_data)
    bot.reply_to(message, "🔕 You will no longer receive alerts. You can enable them anytime with /myalerts.")

# Handler to start alerts for a user
@bot.message_handler(commands=['myalerts'])
def start_alerts(message):
    user_data[message.chat.id] = user_data.get(message.chat.id, {})
    user_data[message.chat.id]["alerts"] = True
    save_user_data(user_data)
    bot.reply_to(message, "✅ You will now receive region alerts as per your preferences.")

# Handler to set alert frequency 
@bot.message_handler(commands=['alertfrequency'])
def set_alert_frequency(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError
        freq = int(parts[1])
        if freq < 5:
            bot.reply_to(message, "❌ Please set a frequency of at least 5 seconds.")
            return
        user_data[message.chat.id] = user_data.get(message.chat.id, {})
        user_data[message.chat.id]["alert_frequency"] = freq
        save_user_data(user_data)
        bot.reply_to(message, f"✅ Alert frequency set to {freq} seconds.")
    except Exception:
        bot.reply_to(message, "⚠️ Sorry, something went wrong. Please try again or type /help.")


@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_USER_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    parts = message.text.split(' ', 1)
    if len(parts) != 2 or not parts[1].strip():
        bot.reply_to(message, "❌ Usage: /broadcast <message>")
        return
    broadcast_msg = parts[1].strip()
    count = 0
    for user_id in user_data.keys():
        try:
            bot.send_message(user_id, f"📢 Broadcast: {broadcast_msg}")
            count += 1
        except Exception as e:
            print(f"Broadcast error for user {user_id}: {e}")
    bot.reply_to(message, f"✅ Broadcast sent to {count} users.")
