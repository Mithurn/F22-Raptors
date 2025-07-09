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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()
user_data = {}

# Load user_data from file if it exists
if os.path.exists(user_data_path):
    with open(user_data_path, 'r') as f:
        user_data = json.load(f)
    # Disable alerts for all users on startup
    for user in user_data.values():
        user["alerts"] = False
    print(f"[DEBUG] Loaded user_data at startup: {user_data}")
else:
    user_data = {}

bot = TeleBot(os.getenv("BOT_TOKEN"))
user_languages = {}

# Register handlers with shared user_data
def register_all_handlers():
    start.register(bot, user_languages, user_data)
    language.register(bot, user_languages, user_data)
    photo.register(bot, user_languages)
    chat.register(bot, user_languages)

register_all_handlers()

# Track last alert time 
last_alert_time = {}

# Background alert 
def alert_sender():
    while True:
        now = time.time()
        for user_id, info in user_data.items():
            if not info.get("alerts", True):
                continue
            lang = info.get("language", "en")
            location = info.get("location")
            if not location:
                continue
            frequency = info.get("alert_frequency", 10)  #  10 seconds
            last_time = last_alert_time.get(user_id, 0)
            if now - last_time < frequency:
                continue
            csv_path = f"backend/DATASETS/risk_data_{lang}.csv"
            try:
                df = pd.read_csv(csv_path)
                # Normalize both user location and region names for comparison
                user_loc_norm = location.strip().lower()
                df["Region_norm"] = df["Region"].astype(str).str.strip().str.lower()
                row = df[df["Region_norm"] == user_loc_norm]
                if not row.empty:
                    risk = row.iloc[0]["Overall_Risk"]
                    suggestion = row.iloc[0]["Suggestion"]
                    msg = f"⚠️ Alert for {location}:\nRisk: {risk}\nAdvice: {suggestion}"
                    bot.send_message(user_id, msg)
                    last_alert_time[user_id] = now
                    # Flag farmer and notify admin if risk is present
                    if str(risk).lower() not in ["none", "low", "0", "no risk"]:
                        info["flagged"] = True
                        save_user_data(user_data)
                        try:
                            admin_msg = f"🚩 Farmer flagged!\nUser ID: {user_id}\nLocation: {location}\nRisk: {risk}\nAdvice: {suggestion}"
                            bot.send_message(ADMIN_USER_ID, admin_msg)
                        except Exception as e:
                            print(f"Admin notification error: {e}")
            except Exception as e:
                print(f"Alert error for user {user_id}: {e}")
        time.sleep(1)

# Start alert sender in background
t = threading.Thread(target=alert_sender, daemon=True)
t.start()

# Handler to stop alerts for a user
@bot.message_handler(commands=['stopalerts'])
def stop_alerts(message):
    user_data[message.chat.id] = user_data.get(message.chat.id, {})
    user_data[message.chat.id]["alerts"] = False
    save_user_data(user_data)
    bot.reply_to(message, "🚫 You will no longer receive automatic alerts.")

# Handler to start alerts for a user
@bot.message_handler(commands=['myalerts'])
def start_alerts(message):
    user_data[message.chat.id] = user_data.get(message.chat.id, {})
    user_data[message.chat.id]["alerts"] = True
    save_user_data(user_data)
    bot.reply_to(message, "✅ You will now receive automatic alerts for your farm location.")

# Handler to set alert frequency for a user
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
        bot.reply_to(message, "❌ Usage: /alertfrequency <seconds> (e.g., /alertfrequency 60)")

ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID'))

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

if __name__ == "__main__":
    print("🤖 Bot is polling...")
    bot.infinity_polling()
