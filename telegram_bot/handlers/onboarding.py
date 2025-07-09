from telebot.types import Message
import telebot.types as types
from services.lang_utils import get_lang_from_text
from fuzzywuzzy import process
import pandas as pd
import logging
import os
import threading
from telegram_bot.handlers.alerts import send_region_alert

WELCOME_MSGS = {
    "en": "👋 Hello! Welcome to KRISHI-RAKSHAK!\nPlease select your language to continue.",
    "hi": "👋 नमस्ते! KRISHI-RAKSHAK में आपका स्वागत है!\nकृपया जारी रखने के लिए अपनी भाषा चुनें।",
    "ta": "👋 வணக்கம்! KRISHI-RAKSHAK-க்கு வரவேற்கிறோம்!\nதயவுசெய்து தொடர உங்கள் மொழியைத் தேர்ந்தெடுக்கவும்.",
    "te": "👋 హలో! KRISHI-RAKSHAK కు స్వాగతం!\nదయచేసి కొనసాగించడానికి మీ భాషను ఎంచుకోండి.",
    "bn": "👋 হ্যালো! KRISHI-RAKSHAK-এ স্বাগতম!\nচালিয়ে যেতে আপনার ভাষা নির্বাচন করুন।"
}
LOCATION_PROMPTS = {
    "en": "🌾 Great! Now, please type your farm location so we can provide you with local advice and alerts. (Don’t worry, you can change this anytime later.)",
    "hi": "🌾 बढ़िया! अब कृपया अपना खेत स्थान टाइप करें ताकि हम आपको स्थानीय सलाह और अलर्ट दे सकें। (चिंता न करें, आप इसे बाद में कभी भी बदल सकते हैं।)",
    "ta": "🌾 அருமை! இப்போது உங்கள் பண்ணை இடத்தைத் தட்டச்சு செய்யவும், நாங்கள் உங்களுக்கு உள்ளூர் ஆலோசனையும் எச்சரிக்கைகளையும் வழங்குவோம். (கவலைப்பட வேண்டாம், இதை நீங்கள் பிறகு எப்போது வேண்டுமானாலும் மாற்றலாம்.)",
    "te": "🌾 గొప్పది! ఇప్పుడు దయచేసి మీ వ్యవసాయ స్థలాన్ని టైప్ చేయండి, మేము మీకు స్థానిక సలహాలు మరియు హెచ్చరికలు ఇస్తాము. (ఎటువంటి ఆందోళన అవసరం లేదు, మీరు దీన్ని ఎప్పుడైనా మార్చవచ్చు.)",
    "bn": "🌾 দারুন! এখন, দয়া করে আপনার খামারের অবস্থান টাইপ করুন যাতে আমরা আপনাকে স্থানীয় পরামর্শ এবং সতর্কতা দিতে পারি। (চিন্তা করবেন না, আপনি এটি পরে যেকোনো সময় পরিবর্তন করতে পারেন।)"
}
LOCATION_CONFIRMED_MSGS = {
    "en": "📍 Location confirmed!\nYou’ve set your location as {location}.\nWe will now send you region-specific farming alerts and advice.\n🌾 You can change this anytime using /location.",
    "hi": "📍 स्थान की पुष्टि हो गई!\nआपने अपना स्थान {location} सेट किया है।\nअब हम आपको क्षेत्र-विशिष्ट कृषि अलर्ट और सलाह भेजेंगे।\n🌾 आप इसे कभी भी /change_location से बदल सकते हैं।",
    "ta": "📍 இடம் உறுதிப்படுத்தப்பட்டது!\nநீங்கள் உங்கள் இடத்தை {location} என அமைத்துள்ளீர்கள்.\nஇப்போது உங்கள் பகுதியில் விவசாய எச்சரிக்கைகள் மற்றும் ஆலோசனைகள் அனுப்பப்படும்.\n🌾 /change_location மூலம் எப்போது வேண்டுமானாலும் மாற்றலாம்.",
    "te": "📍 స్థలం నిర్ధారించబడింది!\nమీరు మీ స్థలాన్ని {location} గా సెట్ చేసుకున్నారు.\nఇప్పుడు మీ ప్రాంతానికి సంబంధించిన వ్యవసాయ హెచ్చరికలు మరియు సలహాలు పంపబడతాయి.\n🌾 మీరు దీన్ని ఎప్పుడైనా /change_location ద్వారా మార్చవచ్చు.",
    "bn": "📍 অবস্থান নিশ্চিত হয়েছে!\nআপনি আপনার অবস্থান {location} হিসাবে সেট করেছেন।\nএখন আমরা আপনাকে অঞ্চল-নির্দিষ্ট কৃষি সতর্কতা এবং পরামর্শ পাঠাব।\n🌾 আপনি এটি /change_location দিয়ে যেকোনো সময় পরিবর্তন করতে পারেন।"
}

LANGUAGE_OPTIONS = ["English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা"]

ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

# Helper to check onboarding
def is_onboarded(user_data, user_id):
    info = user_data.get(user_id, {})
    return info.get("language") and info.get("location") and info.get("onboarded")

def confirm_and_set_location(user_id: str, canonical_region: str, user_data, save_user_data, bot):
    user_data[user_id]["location"] = canonical_region
    user_data[user_id]["alerts"] = True
    user_data[user_id]["onboarded"] = True
    user_data[user_id]["waiting_for_location"] = False
    save_user_data(user_data)
    # Confirmation message
    bot.reply_to(
        bot._get_last_message(user_id),
        f"✅ Your location has been set to {canonical_region}. You will now start receiving region alerts."
    )
    # Start region alert timer
    def send_alert():
        info = user_data.get(user_id, {})
        if info.get("alerts", True):
            send_region_alert(bot, user_id, info, ADMIN_USER_ID)
        threading.Timer(30.0, send_alert).start()
    threading.Timer(30.0, send_alert).start()

def start_region_alert_timer(user_id, user_data, bot, admin_id, interval=30):
    import threading
    from telegram_bot.handlers.alerts import send_region_alert
    def send_alert():
        info = user_data.get(user_id, {})
        if not info.get("alerts", True):
            print(f"[DEBUG] Alerts stopped for user {user_id}, timer will not send.")
            return  # Do not send if alerts are off
        send_region_alert(bot, user_id, info, admin_id)
    threading.Timer(interval, send_alert).start()

def register_onboarding_handlers(bot, user_data, save_user_data):
    @bot.message_handler(commands=['start'])
    def send_welcome(message: Message):
        user_id = str(message.chat.id)
        info = user_data.get(user_id, {})
        lang = info.get("language", "en")
        if is_onboarded(user_data, user_id):
            bot.send_message(message.chat.id, "✅ You are already onboarded! Use /help to see available commands.")
            return
        # Always force language selection if not set
        if not info.get("language"):
            kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            kb.add(*LANGUAGE_OPTIONS)
            msg = WELCOME_MSGS.get(lang, WELCOME_MSGS["en"])
            bot.send_message(message.chat.id, msg, reply_markup=kb)
            return
        # Always force location selection if not set
        if not info.get("location"):
            prompt = LOCATION_PROMPTS.get(lang, LOCATION_PROMPTS["en"])
            bot.send_message(message.chat.id, prompt)
            return
        # If both are set but onboarding is not, set it now
            user_data[user_id]["onboarded"] = True
            save_user_data(user_data)
        # No onboarding complete message here; confirmation is sent after location

    @bot.message_handler(func=lambda msg: msg.text in LANGUAGE_OPTIONS)
    def save_language(message: Message):
        user_id = str(message.chat.id)
        lang_code = get_lang_from_text(message.text)
        user_data[user_id] = user_data.get(user_id, {})
        user_data[user_id]["language"] = lang_code
        user_data[user_id]["onboarded"] = False
        user_data[user_id]["location"] = None
        user_data[user_id]["waiting_for_location"] = True
        save_user_data(user_data)
        print(f"[DEBUG] [onboarding] After language set: {user_data[user_id]}")
        bot.send_message(message.chat.id, f"✅ Language set to {message.text}")
        prompt = LOCATION_PROMPTS.get(lang_code, LOCATION_PROMPTS["en"])
        bot.send_message(message.chat.id, prompt)

    # Remove duplicate location handlers and use only one clean handler for location input
    @bot.message_handler(func=lambda msg: user_data.get(str(msg.chat.id), {}).get("waiting_for_location", False) and msg.text and not msg.text.startswith("/"))
    def save_location(message: Message):
        user_id = str(message.chat.id)
        lang = user_data[user_id].get("language", "en")
        location = message.text.strip()
        csv_path = f"backend/DATASETS/risk_data_{lang}.csv"
        try:
            import pandas as pd
            from fuzzywuzzy import process
            df = pd.read_csv(csv_path)
            regions = df["Region"].astype(str).tolist()
            regions_norm = [r.strip().lower() for r in regions]
            match, score = process.extractOne(location.lower(), regions_norm)
            if score >= 70:
                idx = regions_norm.index(match)
                canonical_region = regions[idx]
                user_data[user_id]["location"] = canonical_region
                user_data[user_id]["onboarded"] = True
                user_data[user_id]["waiting_for_location"] = False  # ✅ set and save immediately
                user_data[user_id]["alerts"] = True  # Always enable alerts after onboarding
                save_user_data(user_data)
                print(f"[DEBUG] waiting_for_location: {user_data[user_id]['waiting_for_location']}")
                bot.reply_to(message, f"✅ Your location has been set to {canonical_region}. You will now start receiving region alerts.")
                # Start alerts after confirming
                ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
                start_region_alert_timer(user_id, user_data, bot, ADMIN_USER_ID)
            else:
                idx = regions_norm.index(match)
                suggestion = regions[idx]
                bot.reply_to(message, f"❌ Location not found. Did you mean: {suggestion}? Available regions include: {', '.join(regions[:5])} ...")
        except Exception as e:
            bot.reply_to(message, "❌ Could not load region data. Please try again later.")
            import logging
            logging.error(f"CSV load error: {e}")

    @bot.message_handler(commands=['location'])
    def ask_location(message: Message):
        user_id = str(message.chat.id)
        user_data[user_id] = user_data.get(user_id, {})
        user_data[user_id]["waiting_for_location"] = True
        save_user_data(user_data)
        print(f"[DEBUG] [onboarding] Waiting for location for {user_id}")
        bot.reply_to(message, "📍 Please type your farm location (district or region):")

    @bot.message_handler(commands=['myalerts'])
    def start_alerts(message: Message):
        user_id = str(message.chat.id)
        user_data[user_id] = user_data.get(user_id, {})
        user_data[user_id]["alerts"] = True
        save_user_data(user_data)
        bot.reply_to(message, "✅ You will now receive region alerts as per your preferences.")
        ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
        start_region_alert_timer(user_id, user_data, bot, ADMIN_USER_ID)

    @bot.message_handler(commands=['stopalerts'])
    def stop_alerts(message: Message):
        user_id = str(message.chat.id)
        user_data[user_id] = user_data.get(user_id, {})
        user_data[user_id]["alerts"] = False
        save_user_data(user_data)
        bot.reply_to(message, "🔕 You will no longer receive alerts. You can enable them anytime with /myalerts.")

    # Block all other actions until onboarding is complete, but allow commands
    @bot.message_handler(func=lambda msg: not is_onboarded(user_data, str(msg.chat.id)) and not (getattr(msg, 'text', None) and msg.text.startswith('/')))
    def block_until_onboarded(message: Message):
        user_id = str(message.chat.id)
        info = user_data.get(user_id, {})
        if not info.get("language"):
            kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            kb.add(*LANGUAGE_OPTIONS)
            bot.send_message(message.chat.id, "🌐 Please select your language:", reply_markup=kb)
        elif not info.get("location"):
            bot.send_message(message.chat.id, "📍 Please tell me your farm location (district or region) in the format: Location: <your location>") 

    # Block all commands except onboarding-related ones until onboarding is complete
    @bot.message_handler(func=lambda msg: not is_onboarded(user_data, str(msg.chat.id)) and getattr(msg, 'text', None) and msg.text.startswith('/') and msg.text.split()[0] not in ['/start', '/help', '/language', '/location'])
    def block_commands_until_onboarded(message: Message):
        bot.reply_to(message, "🚫 Please complete onboarding (set language and location) before using this command.") 