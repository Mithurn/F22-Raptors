import json
import os

user_data_path = 'user_data.json'

def save_user_data(user_data):
    with open(user_data_path, 'w') as f:
        json.dump(user_data, f) 