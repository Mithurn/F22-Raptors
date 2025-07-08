def get_lang_from_text(text: str) -> str:
    lang_map = {
        "English": "en", "हिन्दी": "hi", "தமிழ்": "ta", "తెలుగు": "te", "বাংলা": "bn"
    }
    return lang_map.get(text, "en")

def set_user_lang(user_id, lang_code, user_languages):
    user_languages[user_id] = lang_code

def get_user_lang(user_id, user_languages):
    return user_languages.get(user_id, "en") 