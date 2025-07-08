import os

def save_photo_temp(bot, message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    path = "temp.jpg"
    with open(path, 'wb') as f:
        f.write(downloaded_file)
    return path 