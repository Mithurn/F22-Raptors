import os
import requests
from dotenv import load_dotenv
from backend.gemini_chat import translate_remedy  

load_dotenv()


#remedies mockup
REMEDIES = {
    "early_blight": {
        "en": "Remove affected leaves. Use neem oil spray every 5 days.",
        "hi": "प्रभावित पत्तों को हटा दें। हर 5 दिन में नीम तेल का छिड़काव करें।",
        "ta": "பாதிக்கப்பட்ட இலைகளை அகற்றவும். ஐந்து நாட்களுக்கு ஒருமுறை நீம் எண்ணெய் தெளிக்கவும்.",
        "te": "ప్రమాదంలో ఉన్న ఆకులను తొలగించండి. ప్రతి 5 రోజులకు నిమ్ ఆయిల్‌ను స్ప్రే చేయండి.",
        "bn": "আক্রান্ত পাতাগুলি সরান। প্রতি ৫ দিনে নিম তেল স্প্রে করুন।"
    },
    "late_blight": {
        "en": "Spray with copper-based fungicides. Avoid overhead watering.",
        "hi": "कॉपर-आधारित फफूंदनाशकों का छिड़काव करें। ऊपर से पानी न डालें।",
        "ta": "காப்பர் அடிப்படையிலான பூஞ்சை எதிர்ப்புகளால் தெளிக்கவும். மேலிருந்து நீர் ஊற்ற வேண்டாம்.",
        "te": "కాపర్ ఆధారిత ఫంగీసైడ్‌లను స్ప్రే చేయండి. పై నుండి నీటిని పోయడం మానండి.",
        "bn": "তামা-ভিত্তিক ছত্রাকনাশক স্প্রে করুন। উপর থেকে জল ঢালবেন না।"
    },
    "bacterial_spot": {
        "en": "Use streptomycin or copper sprays. Remove infected parts.",
        "hi": "स्ट्रेप्टोमाइसिन या तांबे के स्प्रे का उपयोग करें। संक्रमित हिस्सों को हटा दें।",
        "ta": "ஸ்ட்ரெப்டோமைசின் அல்லது காப்பர் தெளிவுகளைப் பயன்படுத்தவும். பாதிக்கப்பட்ட பகுதிகளை அகற்றவும்.",
        "te": "స్ట్రెప్టోమైసిన్ లేదా కాపర్ స్ప్రేలను ఉపయోగించండి. అంటుకున్న భాగాలను తీసివేయండి.",
        "bn": "স্ট্রেপ্টোমাইসিন বা তামার স্প্রে ব্যবহার করুন। সংক্রামিত অংশগুলি সরিয়ে ফেলুন।"
    },
    "leaf_mold": {
        "en": "Improve airflow. Apply sulfur spray.",
        "hi": "हवा का संचार सुधारें। सल्फर स्प्रे का उपयोग करें।",
        "ta": "காற்றோட்டத்தை மேம்படுத்தவும். சல்பர் ஸ்பிரேயை பயன்படுத்தவும்.",
        "te": "గాలీవాతావరణాన్ని మెరుగుపరచండి. సల్ఫర్ స్ప్రే వాడండి.",
        "bn": "বাতাস চলাচল উন্নত করুন। সালফার স্প্রে ব্যবহার করুন।"
    },
    "healthy": {
        "en": "No issues detected. Maintain good watering and fertilization.",
        "hi": "कोई समस्या नहीं पाई गई। अच्छी सिंचाई और उर्वरक बनाए रखें।",
        "ta": "பிரச்சனை எதுவும் கண்டறியப்படவில்லை. நல்ல நீர்ப்பாசனத்தையும் உரமிடுதலையும் பேணுங்கள்.",
        "te": "ఏ సమస్యలు కనిపించలేదు. మంచిగా నీరు పోయడం మరియు ఎరువులు వేయడం కొనసాగించండి.",
        "bn": "কোনও সমস্যা পাওয়া যায়নি। সঠিক জলসেচ ও সার প্রয়োগ বজায় রাখুন।"
    },
    "k_deficiency": {
        "en": "Apply potassium-rich fertilizer. Avoid overwatering.",
        "hi": "पोटैशियम युक्त उर्वरक डालें। अधिक पानी से बचें।",
        "ta": "பொட்டாசியம் நிறைந்த உரம் இடவும். அதிகமாக நீர் ஊற்ற வேண்டாம்.",
        "te": "పొటాషియం అధికంగా ఉన్న ఎరువులను వాడండి. ఎక్కువ నీరు పోయడం నివారించండి.",
        "bn": "পটাশিয়াম-সমৃদ্ধ সার প্রয়োগ করুন। অতিরিক্ত জল দেওয়া এড়িয়ে চলুন।"
    }
}

# Disease name translations
DISEASE_NAMES = {
    "early_blight": {
        "en": "Early Blight",
        "hi": "अर्ली ब्लाइट",
        "ta": "ஆர்லி பிளைட்",
        "te": "అర్లీ బ్లైట్",
        "bn": "আর্লি ব্লাইট"
    },
    "late_blight": {
        "en": "Late Blight",
        "hi": "लेट ब्लाइट",
        "ta": "லேட் பிளைட்",
        "te": "లేట్ బ్లైట్",
        "bn": "লেট ব্লাইট"
    },
    "bacterial_spot": {
        "en": "Bacterial Spot",
        "hi": "बैक्टीरियल स्पॉट",
        "ta": "பாக்டீரியல் ஸ்பாட்",
        "te": "బాక్టీరియల్ స్పాట్",
        "bn": "ব্যাকটেরিয়াল স্পট"
    },
    "leaf_mold": {
        "en": "Leaf Mold",
        "hi": "लीफ मोल्ड",
        "ta": "இலை பூஞ்சை",
        "te": "ఆకు అచ్చుపోతు",
        "bn": "পাতার ছাঁচ"
    },
    "healthy": {
        "en": "Healthy",
        "hi": "स्वस्थ",
        "ta": "ஆரோக்கியம்",
        "te": "ఆరోగ్యంగా ఉంది",
        "bn": "সুস্থ"
    },
    "k_deficiency": {
        "en": "Potassium Deficiency",
        "hi": "पोटैशियम की कमी",
        "ta": "பொட்டாசியம் குறைபாடு",
        "te": "పొటాషియం లోపం",
        "bn": "পটাশিয়ামের ঘাটতি"
    }
}

def detect_crop_disease(image_path, lang_code="en"):
    api_key = os.getenv("ROBOFLOW_API_KEY")
    project = os.getenv("ROBOFLOW_PROJECT")
    version = os.getenv("ROBOFLOW_VERSION")

    url = f"https://detect.roboflow.com/{project}/{version}?api_key={api_key}"

    with open(image_path, "rb") as img:
        response = requests.post(url, files={"file": img})

    if response.status_code == 200:
        predictions = response.json().get("predictions", [])
        if not predictions:
            return "🌱 No visible diseases detected."

        result = "🧪 Detected:\n"
        for p in predictions:
            label = p["class"]
            conf = round(p["confidence"] * 100, 2)

            # Debug prints
            print(f"Roboflow label: '{label}', lang_code: '{lang_code}'")
            print(f"DISEASE_NAMES.get(label): {DISEASE_NAMES.get(label)}")

            # Get disease name in user's language, fallback to English
            disease_name = DISEASE_NAMES.get(label, {}).get(lang_code, label)

            remedy_text = REMEDIES.get(label, {}).get(lang_code)
            if not remedy_text:
                remedy_text = REMEDIES.get(label, {}).get("en", "⚠️ No remedy info available.")

            # Remove confidence percentage from result
            result += f"- {disease_name}\n💊 Remedy: {remedy_text}\n\n"
        return result
    else:
        print("❌ Roboflow error:", response.text)
        return "❌ Detection failed."
