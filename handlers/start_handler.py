from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    text = (
        "Selamat datang di Bot Manajemen Grup & Channel.\n\n"
        "Gunakan menu di bawah untuk login dan mengelola grup serta channel Anda.\n\n"
        "Semua proses login menggunakan OTP dan 2FA langsung di sini."
    )
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔐 Login", callback_data="login_start")],
            [InlineKeyboardButton("❓ Bantuan", callback_data="help")],
        ]
    )
    await message.reply(text, reply_markup=keyboard)
