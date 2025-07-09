import pandas as pd
import requests
import datetime
import os
from dotenv import load_dotenv

# Optional import if translation needed later
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from telegram_bot.services.lang_utils import translate_message

# Load API key
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_rainfall_mm(region_name):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={region_name}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if "rain" in data:
            return data["rain"].get("1h", 0)
        return 0
    except Exception as e:
        print(f"Error fetching weather for {region_name}: {e}")
        return 0

def predict_collapse(region, lang_code="bn"):  # default to Bengali
    try:
        df = pd.read_csv("backend/DATASETS/risk_data_be.csv")
        df.columns = df.columns.str.strip()

        row = df[df["Region"].str.strip().str.lower() == region.strip().lower()]

        if not row.empty:
            soil = row.iloc[0]["Soil_Health"]
            gw = row.iloc[0]["Groundwater_Status"]
            risk = row.iloc[0]["Overall_Risk"]
            suggestion = row.iloc[0]["Suggestion"]
            rainfall = get_rainfall_mm(region)
            timestamp = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

            message = (
                f"📍 এলাকা: {region}\n"
                f"🧪 মাটির অবস্থা: {soil}\n"
                f"💧 ভূগর্ভস্থ জল: {gw}\n"
                f"⚠️ সামগ্রিক ঝুঁকি: {risk}\n"
                f"🌧️ বৃষ্টিপাত (১ ঘন্টা): {rainfall} mm\n"
                f"📌 পরামর্শ: {suggestion}\n"
                f"🕒 সময়: {timestamp}"
            )

            # Optional translation (disabled for now)
            # if lang_code != "bn":
            #     message = translate_message(message, lang_code)

            return message

        else:
            return f"❌ এলাকা '{region}' পাওয়া যায়নি।"

    except Exception as e:
        return f"❌ ত্রুটি: {e}"

# Run test
if __name__ == "__main__":
    print(predict_collapse("Punjab"))
    print(predict_collapse("Kerala"))
    print(predict_collapse("Bihar"))
