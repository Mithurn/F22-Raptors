from telebot.types import Message
import logging

def register_admin_handlers(bot, user_data, admin_id):
    @bot.message_handler(commands=['broadcast'])
    def broadcast(message: Message):
        if message.from_user.id != admin_id:
            bot.reply_to(message, "❌ You are not authorized to use this command.")
            return
        parts = message.text.split(' ', 1)
        if len(parts) != 2 or not parts[1].strip():
            bot.reply_to(message, "❌ Usage: /broadcast <message>")
            return
        broadcast_msg = parts[1].strip()
        count = 0
        for user_id in user_data.keys():
            try:
                bot.send_message(int(user_id), f"📢 Broadcast: {broadcast_msg}")
                count += 1
            except Exception as e:
                logging.error(f"[ADMIN] Broadcast error for user {user_id}: {e}")
        bot.reply_to(message, f"✅ Broadcast sent to {count} users.") 