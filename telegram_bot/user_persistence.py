import json
import os

user_data_path = 'user_data.json'

def save_user_data(user_data):
    with open(user_data_path, 'w') as f:
        json.dump(user_data, f)

def clean_user_data_file():
    import collections
    import re
    if not os.path.exists(user_data_path):
        print("user_data.json not found.")
        return
    with open(user_data_path, 'r') as f:
        raw = f.read()
    # Find all user ids and their last occurrence
    matches = list(re.finditer(r'"(\d+)":', raw))
    last_occurrence = collections.OrderedDict()
    for m in matches:
        last_occurrence[m.group(1)] = m.start()
    # Build a new dict with only the last occurrence for each user
    try:
        data = json.loads(raw)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return
    cleaned = {k: data[k] for k in last_occurrence.keys() if k in data}
    with open(user_data_path, 'w') as f:
        json.dump(cleaned, f, indent=2)
    print(f"Cleaned user_data.json. Kept users: {list(cleaned.keys())}")

if __name__ == "__main__":
    clean_user_data_file() 