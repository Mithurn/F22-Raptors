from telebot.types import Message
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import pandas as pd
from telegram_bot.user_persistence import save_user_data
import telebot.types as types
from services.lang_utils import get_lang_from_text, set_user_lang
from fuzzywuzzy import process
import time

# Translation dictionaries
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
    "te": "📍 స్థానం నిర్ధారించబడింది!\nమీరు మీ స్థానాన్ని {location} గా సెట్ చేసారు.\nమేము ఇప్పుడు మీ ప్రాంతానికి ప్రత్యేకమైన వ్యవసాయ హెచ్చరికలు మరియు సలహాలు పంపిస్తాము.\n🌾 మీరు దీన్ని ఎప్పుడైనా /change_location ద్వారా మార్చవచ్చు.",
    "bn": "📍 অবস্থান নিশ্চিত হয়েছে!\nআপনি আপনার অবস্থান {location} হিসেবে সেট করেছেন।\nএখন আমরা আপনাকে অঞ্চলভিত্তিক কৃষি সতর্কতা ও পরামর্শ পাঠাবো।\n🌾 আপনি এটি /change_location দিয়ে যেকোনো সময় পরিবর্তন করতে পারেন।"
}
LOCATION_NOT_FOUND_MSGS = {
    "en": "😅 Sorry, we couldn’t find that location. Did you mean one of these?\nPlease type the correct name or select from the suggestions below.",
    "hi": "😅 क्षमा करें, हम उस स्थान को नहीं ढूंढ सके। क्या आप इनमें से किसी एक को कहना चाह रहे थे?\nकृपया सही नाम टाइप करें या नीचे दिए गए सुझावों में से चुनें।",
    "ta": "😅 மன்னிக்கவும், அந்த இடத்தை கண்டுபிடிக்க முடியவில்லை. நீங்கள் இதை நினைத்தீர்களா?\nசரியான பெயரை உள்ளிடவும் அல்லது கீழே உள்ள பரிந்துரைகளில் ஒன்றைத் தேர்ந்தெடுக்கவும்.",
    "te": "😅 క్షమించండి, ఆ ప్రదేశాన్ని కనుగొనలేకపోయాం. మీరు వీటిలో ఏదైనా ఉద్దేశించారా?\nదయచేసి సరైన పేరును టైప్ చేయండి లేదా క్రింది సూచనల నుండి ఎంచుకోండి.",
    "bn": "😅 দুঃখিত, আমরা সেই অবস্থানটি খুঁজে পাইনি। আপনি কি এর মধ্যে কোনটি বোঝাতে চেয়েছিলেন?\nসঠিক নাম টাইপ করুন বা নিচের পরামর্শ থেকে নির্বাচন করুন."
}
HELP_MSGS = {
    "en": "*🛠 How to use this bot:*\n\n1️⃣ /start — Set up your profile and get started\n2️⃣ /language — Change your language anytime\n3️⃣ /location — Set or update your farm location\n4️⃣ /myalerts — Manage automatic region alerts\n5️⃣ /stopalerts — Stop receiving alerts\n6️⃣ /status — View your current settings\n7️⃣ /about — Learn about this bot\n8️⃣ 📷 *Send a crop photo* — I’ll detect diseases and suggest remedies\n9️⃣ 💬 *Type your farming question* — Get expert advice in your language\n\n🔔 *Alerts are currently sent every 10 seconds (for demo).*\n\n🌐 Supported languages: English, हिंदी, தமிழ், తెలుగు, বাংলা.\n\n💡 If you need help anytime, just type /help!",
    "hi": "*🛠 इस बोट का उपयोग कैसे करें:*\n\n1️⃣ /start — अपनी प्रोफ़ाइल सेट करें और शुरू करें\n2️⃣ /language — कभी भी अपनी भाषा बदलें\n3️⃣ /location — अपना खेत स्थान सेट या अपडेट करें\n4️⃣ /myalerts — क्षेत्रीय अलर्ट प्रबंधित करें\n5️⃣ /stopalerts — अलर्ट बंद करें\n6️⃣ /status — अपनी वर्तमान सेटिंग्स देखें\n7️⃣ /about — इस बोट के बारे में जानें\n8️⃣ 📷 *फसल की फोटो भेजें* — मैं रोग पहचानूंगा और सुझाव दूंगा\n9️⃣ 💬 *अपना कृषि प्रश्न टाइप करें* — अपनी भाषा में विशेषज्ञ सलाह पाएं\n\n🔔 *अलर्ट हर 10 सेकंड में भेजे जाते हैं (डेमो).*\n\n🌐 समर्थित भाषाएँ: English, हिंदी, தமிழ், తెలుగు, বাংলা.\n\n💡 कभी भी /help टाइप करें!",
    "ta": "*🛠 இந்த பாட்டை எப்படி பயன்படுத்துவது:*\n\n1️⃣ /start — உங்கள் சுயவிவரத்தை அமைக்கவும் தொடங்கவும்\n2️⃣ /language — உங்கள் மொழியை எப்போது வேண்டுமானாலும் மாற்றவும்\n3️⃣ /location — உங்கள் பண்ணை இடத்தை அமைக்கவும் அல்லது புதுப்பிக்கவும்\n4️⃣ /myalerts — பகுதி எச்சரிக்கைகளை நிர்வகிக்கவும்\n5️⃣ /stopalerts — எச்சரிக்கைகளை நிறுத்தவும்\n6️⃣ /status — உங்கள் தற்போதைய அமைப்புகளைப் பார்க்கவும்\n7️⃣ /about — இந்த பாட்டைப் பற்றி அறியவும்\n8️⃣ 📷 *பயிர் புகைப்படம் அனுப்பவும்* — நோய்களை கண்டறிந்து பரிந்துரைகளை வழங்குவேன்\n9️⃣ 💬 *உங்கள் விவசாயக் கேள்வியைத் தட்டச்சு செய்யவும்* — உங்கள் மொழியில் நிபுணர் ஆலோசனை பெறவும்\n\n🔔 *எச்சரிக்கைகள் தற்போது ஒவ்வொரு 10 வினாடிகளுக்கும் அனுப்பப்படுகின்றன (டெமோ).*\n\n🌐 ஆதரவு மொழிகள்: English, हिंदी, தமிழ், తెలుగు, বাংলা.\n\n💡 எப்போது வேண்டுமானாலும் /help எனத் தட்டச்சு செய்யவும்!",
    "te": "*🛠 ఈ బాట్‌ను ఎలా ఉపయోగించాలి:*\n\n1️⃣ /start — మీ ప్రొఫైల్‌ను సెటప్ చేయండి మరియు ప్రారంభించండి\n2️⃣ /language — మీ భాషను ఎప్పుడైనా మార్చండి\n3️⃣ /location — మీ వ్యవసాయ స్థలాన్ని సెటప్ చేయండి లేదా నవీకరించండి\n4️⃣ /myalerts — ప్రాంతీయ హెచ్చరికలను నిర్వహించండి\n5️⃣ /stopalerts — హెచ్చరికలను ఆపండి\n6️⃣ /status — మీ ప్రస్తుత సెట్టింగులను చూడండి\n7️⃣ /about — ఈ బాట్ గురించి తెలుసుకోండి\n8️⃣ 📷 *పంట ఫోటోను పంపండి* — నేను వ్యాధులను గుర్తించి సూచనలు ఇస్తాను\n9️⃣ 💬 *మీ వ్యవసాయ ప్రశ్నను టైప్ చేయండి* — మీ భాషలో నిపుణుల సలహా పొందండి\n\n🔔 *హెచ్చరికలు ప్రస్తుతం ప్రతి 10 సెకన్లకూ పంపబడతాయి (డెమో).*\n\n🌐 మద్దతు భాషలు: English, हिंदी, தமிழ், తెలుగు, বাংলা.\n\n💡 ఎప్పుడైనా /help టైప్ చేయండి!",
    "bn": "*🛠 ఏఇ బట్టి కీభాబు బ్యవహారం చేయండి:*\n\n1️⃣ /start — మీ ప్రోఫైల్ సెట్ చేయండి మరియు ప్రారంభించండి\n2️⃣ /language — యొక్క ఏ సమయంలో మీ భాషను మార్చండి\n3️⃣ /location — మీ వ్యవసాయ స్థలాన్ని సెట్ చేయండి లేదా నవీకరించండి\n4️⃣ /myalerts — ప్రాంతీయ హెచ్చరికలను నిర్వహించండి\n5️⃣ /stopalerts — హెచ్చరికలను ఆపండి\n6️⃣ /status — మీ ప్రస్తుత సెట్టింగులను చూడండి\n7️⃣ /about — ఈ బాట్ గురించి తెలుసుకోండి\n8️⃣ 📷 *పంట ఫోటోను పంపండి* — నేను వ్యాధులను గుర్తించి సూచనలు ఇస్తాను\n9️⃣ 💬 *మీ వ్యవసాయ ప్రశ్నను టైప్ చేయండి* — మీ భాషలో నిపుణుల సలహా పొందండి\n\n🔔 *హెచ్చరికలు ప్రస్తుతం ప్రతి 10 సెకన్లకూ పంపబడతాయి (డెమో).*\n\n🌐 మద్దతు భాషలు: English, हिंदी, தமிழ், తెలుగు, বাংলা.\n\n💡 ఎప్పుడైనా /help టైప్ చేయండి!"
}
STATUS_MSGS = {
    "en": "*✅ Your Current Settings:*\n\n🌐 *Language:* {language}\n📍 *Location:* {location}\n🔔 *Alerts:* {alerts_status}\n\nYou can update your language with /language or change your location with /location anytime.\n\nIf you'd like to manage alerts, use /myalerts or /stopalerts.\n\n💡 Type /help anytime to see all commands.",
    "hi": "*✅ आपकी वर्तमान सेटिंग्स:*\n\n🌐 *भाषा:* {language}\n📍 *स्थान:* {location}\n🔔 *अलर्ट्स:* {alerts_status}\n\nआप /language से भाषा या /location से स्थान कभी भी बदल सकते हैं।\n\nअलर्ट्स प्रबंधित करने के लिए /myalerts या /stopalerts का उपयोग करें।\n\n💡 सभी कमांड्स के लिए कभी भी /help टाइप करें।",
    "ta": "*✅ உங்கள் தற்போதைய அமைப்புகள்:*\n\n🌐 *மொழி:* {language}\n📍 *இடம்:* {location}\n🔔 *எச்சரிக்கைகள்:* {alerts_status}\n\n/language மூலம் மொழியை அல்லது /location மூலம் இடத்தை எப்போது வேண்டுமானாலும் மாற்றலாம்.\n\nஎச்சரிக்கைகளை நிர்வகிக்க /myalerts அல்லது /stopalerts பயன்படுத்தவும்.\n\n💡 அனைத்து கட்டளைகளையும் பார்க்க எப்போது வேண்டுமானாலும் /help எனத் தட்டச்சு செய்யவும்!",
    "te": "*✅ మీ ప్రస్తుత సెట్టింగులు:*\n\n🌐 *భాష:* {language}\n📍 *స్థానం:* {location}\n🔔 *హెచ్చరికలు:* {alerts_status}\n\nమీరు /language తో భాషను లేదా /location తో స్థానాన్ని ఎప్పుడైనా మార్చవచ్చు.\n\nహెచ్చరికలను నిర్వహించడానికి /myalerts లేదా /stopalerts ఉపయోగించండి.\n\n💡 అన్ని ఆదేశాలను చూడటానికి ఎప్పుడైనా /help టైప్ చేయండి!",
    "bn": "*✅ আপনার বর্তমান সেটিংস:*\n\n🌐 *ভাষা:* {language}\n📍 *অবস্থান:* {location}\n🔔 *সতর্কতা:* {alerts_status}\n\n/language দিয়ে ভাষা বা /location দিয়ে অবস্থান যেকোনো সময় পরিবর্তন করতে পারেন।\n\nসতর্কতা পরিচালনা করতে /myalerts বা /stopalerts ব্যবহার করুন।\n\n💡 সব কমান্ড দেখতে যেকোনো সময় /help টাইপ করুন!"
}
ABOUT_MSGS = {
    "en": "*ℹ️ About this bot:*\n\nThis is a *Smart Farming Assistant* designed to support farmers with region-specific alerts, crop disease diagnosis, and expert farming advice — all in your local language.\n\n✅ Features:\n- Region-aware risk and weather alerts\n- AI chat for personalized crop queries\n- Photo-based disease detection\n- Multilingual support (English, हिंदी, தமிழ், తెలుగు, বাংলা)\n\n👨‍🌾 Our mission: Help farmers stay informed, reduce losses, and improve yields using AI.\n\nIf you have any questions, just type /help anytime!",
    "hi": "*ℹ️ इस बोट के बारे में:*\n\nयह एक *स्मार्ट फार्मिंग असिस्टेंट* है जो किसानों को क्षेत्र-विशिष्ट अलर्ट, फसल रोग निदान और विशेषज्ञ कृषि सलाह उनके स्थानीय भाषा में प्रदान करता है।\n\n✅ विशेषताएँ:\n- क्षेत्र-आधारित जोखिम और मौसम अलर्ट\n- व्यक्तिगत फसल प्रश्नों के लिए एआई चैट\n- फोटो-आधारित रोग पहचान\n- बहुभाषी समर्थन (English, हिंदी, தமிழ், తెలుగు, বাংলা)\n\n👨‍🌾 हमारा मिशन: किसानों को सूचित रखना, नुकसान कम करना और उपज बढ़ाना।\n\nकोई भी सवाल हो तो कभी भी /help टाइप करें!",
    "ta": "*ℹ️ இந்த பாட்டைப் பற்றி:*\n\nஇது ஒரு *ஸ்மார்ட் விவசாய உதவியாளர்*, விவசாயிகளுக்கு பகுதி சார்ந்த எச்சரிக்கைகள், பயிர் நோய் கண்டறிதல் மற்றும் நிபுணர் விவசாய ஆலோசனைகள் அவர்களின் உள்ளூர் மொழியில் வழங்கப்படுகிறது.\n\n✅ அம்சங்கள்:\n- பகுதி சார்ந்த அபாயம் மற்றும் வானிலை எச்சரிக்கைகள்\n- தனிப்பயன் பயிர் கேள்விகளுக்கான ஏஐ உரையாடல்\n- புகைப்பட அடிப்படையிலான நோய் கண்டறிதல்\n- பன்மொழி ஆதரவு (English, हिंदी, தமிழ், తెలుగు, বাংলা)\n\n👨‍🌾 எங்கள் நோக்கம்: விவசாயிகளை தகவலறிந்தவர்களாக வைத்திருத்தல், இழப்புகளை குறைத்தல் மற்றும் விளைச்சலை மேம்படுத்துதல்.\n\nஎந்த கேள்வியும் இருந்தால் எப்போது வேண்டுமானாலும் /help எனத் தட்டச்சு செய்யவும்!",
    "te": "*ℹ️ ఈ బాట్ గురించి:*\n\nఇది ఒక *స్మార్ట్ ఫార్మింగ్ అసిస్టెంట్*, రైతులకు ప్రాంతీయ హెచ్చరికలు, పంట వ్యాధి నిర్ధారణ మరియు నిపుణుల వ్యవసాయ సలహా వారి స్థానిక భాషలో అందిస్తుంది.\n\n✅ లక్షణాలు:\n- ప్రాంతీయ ప్రమాదం మరియు వాతావరణ హెచ్చరికలు\n- వ్యక్తిగత పంట ప్రశ్నలకు AI చాట్\n- ఫోటో ఆధారిత వ్యాధి నిర్ధారణ\n- బహుభాషా మద్దతు (English, हिंदी, தமிழ், తెలుగు, বাংলা)\n\n👨‍🌾 మా లక్ష్యం: రైతులను సమాచారం కలిగినవారిగా ఉంచడం, నష్టాలను తగ్గించడం మరియు దిగుబడిని పెంచడం.\n\nఏవైనా ప్రశ్నలు ఉంటే ఎప్పుడైనా /help టైప్ చేయండి!",
    "bn": "*ℹ️ ఇది బట్ గురించి:*\n\nఇది ఒక *స్మార్ట్ ఫార్మింగ్ అసిస్టెంట్*, యాక్షికారులకు ప్రాంతీయ సతర్కతలు, పంట వ్యాధి నిర్ధారణ మరియు నిపుణుల వ్యవసాయ సలహా అవరుల స్థానిక భాషలో అందిస్తుంది.\n\n✅ లక్షణాలు:\n- ప్రాంతీయ ప్రమాదం మరియు వాతావరణ సతర్కతలు\n- బిందువులు ప్రశ్నలకు AI చాట్\n- ఫోటో ఆధారిత వ్యాధి నిర్ధారణ\n- బహుభాషా మద్దతు (English, हिंदी, தமிழ், తెలుగు, বাংলা)\n\n👨‍🌾 మా లక్ష్యం: రైతులను సమాచారం కలిగినవారిగా ఉంచడం, నష్టాలను తగ్గించడం మరియు దిగుబడిని పెంచడం.\n\nఏవైనా ప్రశ్నలు ఉంటే ఎప్పుడైనా /help టైప్ చేయండి!"
}

def register(bot, user_languages, user_data=None):
    @bot.message_handler(commands=['start'])
    def send_welcome(message: Message):
        info = user_data.get(message.chat.id, {}) if user_data else {}
        lang = info.get("language", "en")
        if info.get("onboarded"):
            send_help(message)
            return
        if not info.get("language"):
            kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            kb.add("English", "हिन्दी", "தமிழ்", "తెలుగు", "বাংলা")
            msg = WELCOME_MSGS.get(lang, WELCOME_MSGS["en"])
            bot.send_message(message.chat.id, msg, reply_markup=kb)
        elif not info.get("location"):
            prompt = LOCATION_PROMPTS.get(lang, LOCATION_PROMPTS["en"])
            bot.send_message(message.chat.id, prompt)
        else:
            # If both are set but onboarded is not, set it now
            user_data[message.chat.id]["onboarded"] = True
            save_user_data(user_data)
            from telegram_bot import bot as bot_module
            bot_module.last_alert_time[message.chat.id] = time.time()
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

    # Accept any text as location if language is set 
    @bot.message_handler(func=lambda msg: user_data and user_data.get(msg.chat.id, {}).get("language") and not user_data.get(msg.chat.id, {}).get("location") and msg.text and not msg.text.startswith("/"))
    def save_location_onboarding(message: Message):
        location = message.text.strip()
        lang = user_data[message.chat.id]["language"]
        csv_path = f"backend/DATASETS/risk_data_{lang}.csv"
        try:
            df = pd.read_csv(csv_path)
            regions = df["Region"].astype(str).tolist()
            regions_norm = [r.strip().lower() for r in regions]
        except Exception as e:
            bot.reply_to(message, "❌ Could not load region data. Please try again later.")
            print(f"CSV load error: {e}")
            return
        # Fuzzy match
        match, score = process.extractOne(location.lower(), regions_norm)
        if score >= 80:
            idx = regions_norm.index(match)
            canonical_region = regions[idx]
            if user_data is not None:
                user_data[message.chat.id] = user_data.get(message.chat.id, {})
                user_data[message.chat.id]["location"] = canonical_region
                user_data[message.chat.id]["alerts"] = True  # Enable alerts only after location is set
                user_data[message.chat.id]["onboarded"] = True
                save_user_data(user_data)
                from telegram_bot import bot as bot_module
                # Delay region alerts by 30 seconds after onboarding
                import threading
                def set_alert_time():
                    import time
                    time.sleep(30)
                    bot_module.last_alert_time[message.chat.id] = time.time()
                threading.Thread(target=set_alert_time, daemon=True).start()
            lang = user_data[message.chat.id].get("language", "en")
            msg = LOCATION_CONFIRMED_MSGS.get(lang, LOCATION_CONFIRMED_MSGS["en"]).format(location=canonical_region)
            bot.reply_to(message, msg)
            # Do NOT send welcome or help message here
        else:
            idx = regions_norm.index(match)
            suggestion = regions[idx]
            bot.reply_to(
                message,
                LOCATION_NOT_FOUND_MSGS.get(lang, LOCATION_NOT_FOUND_MSGS["en"])
            )
            return

    # Accept any text as location after /location command
    @bot.message_handler(func=lambda msg: hasattr(msg, 'reply_to_message') and msg.reply_to_message and msg.reply_to_message.text and ("farm location" in msg.reply_to_message.text or "Location:" in msg.reply_to_message.text))
    def update_location(message: Message):
        location = message.text.strip()
        lang = user_data[message.chat.id]["language"]
        csv_path = f"backend/DATASETS/risk_data_{lang}.csv"
        try:
            df = pd.read_csv(csv_path)
            regions = df["Region"].astype(str).tolist()
            regions_norm = [r.strip().lower() for r in regions]
        except Exception as e:
            bot.reply_to(message, "❌ Could not load region data. Please try again later.")
            print(f"CSV load error: {e}")
            return
        # Fuzzy match
        match, score = process.extractOne(location.lower(), regions_norm)
        if score >= 80:
            idx = regions_norm.index(match)
            canonical_region = regions[idx]
            if user_data is not None:
                user_data[message.chat.id]["location"] = canonical_region
                user_data[message.chat.id]["onboarded"] = True
                save_user_data(user_data)
            bot.reply_to(message, f"✅ Location updated to: {canonical_region}")
        else:
            idx = regions_norm.index(match)
            suggestion = regions[idx]
            bot.reply_to(message, f"❌ Location not found. Did you mean: {suggestion}? Available regions include: {', '.join(regions[:5])} ...")
            return

    # Block all other actions until setup is complete
    @bot.message_handler(func=lambda msg: not (user_data and user_data.get(msg.chat.id, {}).get("onboarded")))
    def block_until_setup(message: Message):
        info = user_data.get(message.chat.id, {}) if user_data else {}
        print(f"[DEBUG] block_until_setup triggered for chat_id={message.chat.id}, info={info}")
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
        lang = info.get("language", "en")
        location = info.get("location", "Not set")
        alerts = info.get("alerts", True)
        alerts_str = "ON" if alerts else "OFF"
        status_msg = STATUS_MSGS.get(lang, STATUS_MSGS["en"]).format(
            language=lang_map.get(lang, "English"),
            location=location,
            alerts_status=alerts_str
        )
        bot.reply_to(message, status_msg, parse_mode="Markdown")

    @bot.message_handler(commands=['about'])
    def about(message: Message):
        info = user_data.get(message.chat.id, {}) if user_data else {}
        lang = info.get("language", "en")
        about_msg = ABOUT_MSGS.get(lang, ABOUT_MSGS["en"])
        bot.reply_to(message, about_msg, parse_mode="Markdown")

    @bot.message_handler(commands=['help'])
    def send_help(message: Message):
        info = user_data.get(message.chat.id, {}) if user_data else {}
        lang = info.get("language", "en")
        help_msg = HELP_MSGS.get(lang, HELP_MSGS["en"])
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
                # Normalize both user location and region names for comparison
                user_loc_norm = location.strip().lower()
                df["Region_norm"] = df["Region"].astype(str).str.strip().str.lower()
                row = df[df["Region_norm"] == user_loc_norm]
                if not row.empty:
                    risk = row.iloc[0]["Overall_Risk"]
                    suggestion = row.iloc[0]["Suggestion"]
                    msg = f"⚠️ Alert for {location}:\nRisk: {risk}\nAdvice: {suggestion}"
                    bot.send_message(user_id, msg)
                    count += 1
            except Exception as e:
                print(f"Alert error for user {user_id}: {e}")
        bot.reply_to(message, f"✅ Sent alerts to {count} users.")
