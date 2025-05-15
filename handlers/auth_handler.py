from main import app
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from auth import login_flow, check_session_valid
from db import delete_session

STATE = {}

@app.on_callback_query(filters.regex("^login_start$"))
async def login_start(client, query: CallbackQuery):
    user_id = query.from_user.id
    STATE[user_id] = {"step": "ask_phone"}
    await query.message.edit("Masukkan nomor telepon Anda dengan kode negara, contoh: +6281234567890")

@app.on_message(filters.private)
async def message_handler(client, message: Message):
    user_id = message.from_user.id
    if user_id not in STATE:
        return

    state = STATE[user_id]

    if state["step"] == "ask_phone":
        phone = message.text.strip()
        state["phone"] = phone
        state["step"] = "ask_code"
        await message.reply("Silakan masukkan kode OTP yang sudah dikirim ke nomor Anda (pakai spasi agar tidak terdeteksi):")

    elif state["step"] == "ask_code":
        otp = message.text.strip()
        state["otp"] = otp
        state["step"] = "processing"

        async def code_callback(text):
            await message.reply(text)
            return otp

        async def password_callback(text):
            await message.reply(text)
            response = await client.listen(message.chat.id)
            return response.text

        session_string = await login_flow(client, user_id, state["phone"], code_callback, password_callback)
        if session_string:
            await message.reply("Login berhasil! Anda bisa mulai mengelola grup & channel Anda.")
            del STATE[user_id]
        else:
            await message.reply("Login gagal, coba ulangi dari awal dengan menekan tombol 🔐 Login.")
            del STATE[user_id]

@app.on_callback_query(filters.regex("^logout$"))
async def logout(client, query: CallbackQuery):
    user_id = query.from_user.id
    await delete_session(user_id)
    await query.message.edit("Anda sudah logout. Untuk login ulang, klik tombol 🔐 Login.")
