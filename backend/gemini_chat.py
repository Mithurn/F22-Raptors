import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

def translate_remedy(text, target_lang):
    if target_lang == "en":
        return text  

    prompt = (
        f"Translate this agricultural advice into {target_lang}:\n"
        f"{text}\n\n"
        f"Make it short and farmer-friendly."
    )


def ask_crop_doctor(question, language_code="en"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    #languages
    lang_map = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "bn": "Bengali"
    }
    full_lang = lang_map.get(language_code, "English")

    prompt = (
        f"You are an experienced, friendly crop doctor giving advice to a farmer.\n"
        f"Respond in this language: {full_lang}.\n"
        f"- Use only 3 to 5 short, clear bullet points.\n"
        f"- Do not add greetings, intros, or explanations.\n"
        f"- Each point should be simple, practical, and helpful.\n"
        f"- Avoid technical terms or long sentences.\n"
        f"- Add emojis if helpful.\n"
        f"\n"
        f"Farmer's question: {question}"
    )

    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(body))
        result = response.json()
        if 'candidates' not in result:
            print('❌ Gemini API unexpected response:', result)
            return "⚠️ Sorry, I couldn't get a valid answer from Gemini. Please try again later."
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print("❌ Gemini API error:", e)
        return "⚠️ Sorry, I couldn't process that. Please try again."
