import pandas as pd
import requests
import datetime
import os
from dotenv import load_dotenv

# Load file
load_dotenv()

#  API key from .env
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_rainfall_mm(region_name):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={region_name}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if "rain" in data:
            rain_mm = data["rain"].get("1h", 0)  # rainfall in last 1 hour
        else:
            rain_mm = 0

        return rain_mm
    except Exception as e:
        print(f"Error getting rainfall for {region_name}: {e}")
        return 0

def calculate_risk(soil_health, rainfall_mm, gw_status):
    score = 0

    # Soil health
    if soil_health == "Poor":
        score += 2
    elif soil_health == "Moderate":
        score += 1

    # Rainfall
    if rainfall_mm < 5:
        score += 2
    elif rainfall_mm < 20:
        score += 1

    # Groundwater
    if gw_status == "Critical":
        score += 2
    elif gw_status == "Low":
        score += 1

    if score >= 5:
        return "High", 90
    elif score >= 3:
        return "Medium", 60
    else:
        return "Low", 30

#function to predict collapse risk based on region
def predict_collapse(region):
    df = pd.read_csv("backend/datasets/risk_data.csv")  # CSV path
    row = df[df["Region"] == region]
    
    if not row.empty:
        soil = row.iloc[0]["Soil_Health"]
        gw = row.iloc[0]["GW_Status"]
        rainfall = get_rainfall_mm(region)

        risk, days = calculate_risk(soil, rainfall, gw)
        current_time = datetime.datetime.now().strftime("%d %b %Y, %H:%M")
        return f"{region}: Risk {risk}, collapse expected in {days} days (as of {current_time}, real-time rainfall: {rainfall} mm)."
    else:
        return "Region not found."

# local test
if __name__ == "__main__":
    print(predict_collapse("Punjab"))
    print(predict_collapse("Tamil Nadu"))
    print(predict_collapse("Kerala"))
