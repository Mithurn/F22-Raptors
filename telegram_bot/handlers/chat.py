from backend.gemini_chat import ask_crop_doctor
from services.lang_utils import get_user_lang
from telebot.types import Message
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import distress detection
from backend.distress_ai import is_distress_message
from dotenv import load_dotenv
load_dotenv()

ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0'))

# Optional: helpline info
HELPLINE_INFO = "If you need urgent help, please call the National Helpline: 1-800-123-4567."

LANGUAGE_OPTIONS = ["English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা"]

# Multilingual distress messages
DISTRESS_MSGS = {
    "en": "🚨 It looks like you might be facing some difficulties. If you need urgent help, please reach out to someone you trust or your local agricultural officer. Remember, you’re not alone — we’re here to support you!",
    "hi": "🚨 ऐसा लगता है कि आप कुछ कठिनाइयों का सामना कर रहे हैं। यदि आपको तत्काल सहायता की आवश्यकता है, तो कृपया अपने विश्वसनीय व्यक्ति या स्थानीय कृषि अधिकारी से संपर्क करें। याद रखें, आप अकेले नहीं हैं — हम आपकी मदद के लिए यहाँ हैं!",
    "ta": "🚨 நீங்கள் சில சிரமங்களை எதிர்கொள்கிறீர்கள் போல் தெரிகிறது. உடனடி உதவி தேவைப்பட்டால், நம்பகமான ஒருவரை அல்லது உங்கள் உள்ளூர் விவசாய அதிகாரியை அணுகவும். நீங்கள் தனியாக இல்லை — நாங்கள் உங்களை ஆதரிக்க இருக்கிறோம்!",
    "te": "🚨 మీరు కొన్ని కష్టాలను ఎదుర్కొంటున్నట్లు కనిపిస్తోంది. తక్షణ సహాయం అవసరమైతే, దయచేసి మీ నమ్మకమైన వ్యక్తిని లేదా స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి. మీరు ఒంటరిగా లేరు — మేము మీకు మద్దతుగా ఉన్నాము!",
    "bn": "🚨 মনে হচ্ছে আপনি কিছু সমস্যার সম্মুখীন হচ্ছেন। জরুরি সহায়তার প্রয়োজন হলে, দয়া করে আপনার বিশ্বস্ত কাউকে বা স্থানীয় কৃষি কর্মকর্তার সাথে যোগাযোগ করুন। মনে রাখবেন, আপনি একা নন — আমরা আপনাকে সহায়তা করতে এখানে আছি!"
}

def register(bot, user_languages, user_data=None):
    @bot.message_handler(func=lambda msg: msg.text.lower() in ["hi", "hello", "hey"])
    def greet(message: Message):
        bot.reply_to(message, "👋 Hello! How can I help you with your crops today?")

    @bot.message_handler(func=lambda msg: msg.text and not msg.text.startswith('/') and msg.text not in LANGUAGE_OPTIONS)
    def chat_with_crop_doctor(message: Message):
        print(f"[DEBUG] chat_with_crop_doctor called for user {message.chat.id}: {message.text}")
        # Only process chat if onboarding is complete
        info = user_data.get(message.chat.id, {}) if user_data else {}
        if not info.get("onboarded"):
            return  # Let onboarding/location handlers process
        print(f"[DEBUG] Checking for distress: {message.text}")
        # Distress detection
        is_distress, reason = is_distress_message(message.text)
        print(f"[DEBUG] is_distress={is_distress}, reason={reason}")
        if is_distress:
            # Alert admin
            try:
                print(f"[DEBUG] Sending distress alert to admin: ADMIN_USER_ID={ADMIN_USER_ID}, user_id={message.chat.id}")
                alert_msg = (
                    f"🚨 Distress Alert!\n"
                    f"Farmer {getattr(message.from_user, 'first_name', 'Unknown')} (@{getattr(message.from_user, 'username', 'N/A')}) in {info.get('location', 'Unknown')} may need urgent support.\n"
                    f"Message:\n\"{message.text}\""
                )
                bot.send_message(ADMIN_USER_ID, alert_msg)
            except Exception as e:
                print(f"[ERROR] Failed to alert admin: {e}")
            # Empathetic auto-reply to user (multilingual)
            lang = info.get("language", "en")
            reply = DISTRESS_MSGS.get(lang, DISTRESS_MSGS["en"])
            bot.send_message(message.chat.id, reply)
            return
        # Normal chat flow
        lang = get_user_lang(message.chat.id, user_languages)
        answer = ask_crop_doctor(message.text, lang)
        reply = (
            f"🤖 Here’s what I found:\n{answer}\nLet me know if you'd like more details!"
        )
        bot.send_message(message.chat.id, reply)
