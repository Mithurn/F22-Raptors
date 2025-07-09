import json
import os

user_data_path = 'user_data.json'

def load_user_data():
    if os.path.exists(user_data_path):
        with open(user_data_path, 'r') as f:
            data = json.load(f)
        # Ensure all keys are strings
        return {str(k): v for k, v in data.items()}
    return {}

def save_user_data(user_data):
    # Ensure only one entry per user (dict keys are unique, but check for accidental duplicates in input)
    clean_data = {}
    for k, v in user_data.items():
        clean_data[str(k)] = v  # Always use string keys
    with open(user_data_path, 'w') as f:
        json.dump(clean_data, f) 
    print(f"[DEBUG] [save_user_data] Saved user_data: {clean_data}") 