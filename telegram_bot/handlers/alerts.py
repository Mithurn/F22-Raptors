import threading
import time
import pandas as pd
import logging
from telebot.types import Message

def is_onboarded(user_data, user_id):
    info = user_data.get(user_id, {})
    return info.get("language") and info.get("location") and info.get("onboarded")

def send_region_alert(bot, user_id, info, admin_id):
    lang = info.get("language", "en")
    location = info.get("location")
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
            bot.send_message(int(user_id), msg, parse_mode="Markdown")
            # Get user name for admin alert
            try:
                chat = bot.get_chat(int(user_id))
                user_name = chat.first_name or str(user_id)
            except Exception:
                user_name = str(user_id)
            admin_msg = f"⚠️ Alert for user {user_name} ({region}): {alert_message}\n{precautions_text}"
            bot.send_message(admin_id, admin_msg)
            logging.info(f"[ALERT] Sent region alert to user {user_id} and admin {admin_id}")
    except Exception as e:
        logging.error(f"[ALERT] Error sending region alert for user {user_id}: {e}")

def alert_thread_fn(bot, user_data, last_alert_time, admin_id):
    while True:
        now = time.time()
        for user_id, info in list(user_data.items()):
            if not is_onboarded(user_data, user_id):
                continue
            if not info.get("alerts", True):
                continue
            location = info.get("location")
            if not location:
                continue
            frequency = info.get("alert_frequency", 10)
            last_time = last_alert_time.get(user_id)
            if last_time is None:
                last_alert_time[user_id] = now + 30
                logging.info(f"[ALERT] Set last_alert_time for user {user_id} to {last_alert_time[user_id]} (30s after onboarding)")
                continue
            if now - last_time < frequency:
                continue
            send_region_alert(bot, user_id, info, admin_id)
            last_alert_time[user_id] = now
        time.sleep(1)

def start_alert_thread(bot, user_data, last_alert_time, admin_id):
    t = threading.Thread(target=alert_thread_fn, args=(bot, user_data, last_alert_time, admin_id), daemon=True)
    t.start()

def register_alert_handlers(bot, user_data, save_user_data, last_alert_time, admin_id):
    @bot.message_handler(commands=['stopalerts'])
    def stop_alerts(message: Message):
        user_id = str(message.chat.id)
        user_data[user_id] = user_data.get(user_id, {})
        user_data[user_id]["alerts"] = False
        save_user_data(user_data)
        print(f"[DEBUG] [alerts] Alerts stopped for {user_id}")
        bot.reply_to(message, "🔕 You will no longer receive alerts. You can enable them anytime with /myalerts.")
        logging.info(f"[ALERT] User {user_id} stopped alerts.")

    @bot.message_handler(commands=['myalerts'])
    def start_alerts(message: Message):
        user_id = str(message.chat.id)
        user_data[user_id] = user_data.get(user_id, {})
        user_data[user_id]["alerts"] = True
        save_user_data(user_data)
        print(f"[DEBUG] [alerts] Alerts started for {user_id}")
        bot.reply_to(message, "✅ You will now receive region alerts as per your preferences.")
        logging.info(f"[ALERT] User {user_id} started alerts.")
        # Immediately schedule alert if not already scheduled
        if user_id not in last_alert_time:
            import time
            last_alert_time[user_id] = time.time() - 100  # Force immediate alert

    @bot.message_handler(commands=['alertfrequency'])
    def set_alert_frequency(message: Message):
        user_id = str(message.chat.id)
        try:
            parts = message.text.split()
            if len(parts) != 2:
                raise ValueError
            freq = int(parts[1])
            if freq < 5:
                bot.reply_to(message, "❌ Please set a frequency of at least 5 seconds.")
                return
            user_data[user_id] = user_data.get(user_id, {})
            user_data[user_id]["alert_frequency"] = freq
            save_user_data(user_data)
            print(f"[DEBUG] [alerts] Alert frequency set for {user_id}: {freq}s")
            bot.reply_to(message, f"✅ Alert frequency set to {freq} seconds.")
            logging.info(f"[ALERT] User {user_id} set alert frequency to {freq}s.")
        except Exception:
            bot.reply_to(message, "⚠️ Sorry, something went wrong. Please try again or type /help.") 