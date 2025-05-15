# main.py
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Import handler-setelah app didefinisikan agar handler bisa pakai app
import handlers.start_handler
import handlers.auth_handler
import handlers.groups_handler
import handlers.callback_handler

if __name__ == "__main__":
    print("Bot berjalan...")
    app.run()
