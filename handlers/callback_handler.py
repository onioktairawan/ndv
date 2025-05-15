from pyrogram.types import CallbackQuery
from main import app
from pyrogram import filters

@app.on_callback_query(filters.regex("^help$"))
async def help_handler(client, query: CallbackQuery):
    text = (
        "Bot ini untuk mengelola grup & channel Telegram Anda.\n"
        "Fitur utama:\n"
        "- 🔐 Login menggunakan OTP & 2FA\n"
        "- Lihat daftar grup & channel\n"
        "- Filter grup publik/privat\n"
        "- Pagination daftar\n"
        "- Keluar grup atau unsubs channel\n\n"
        "Gunakan tombol yang tersedia untuk navigasi."
    )
    await query.message.edit(text)
