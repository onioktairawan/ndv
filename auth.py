from pyrogram import Client, errors
from db import save_session, get_session, delete_session, update_last_active
from pyrogram.raw import functions, types
from pyrogram.raw.functions.account import SendCode, SignIn, SignUp, SignInTwoStep
from datetime import datetime

async def login_flow(bot, user_id, phone_number, code_callback, password_callback=None):
    """
    Alur login OTP + 2FA menggunakan raw API Telegram.
    code_callback: function untuk meminta OTP ke user (chat interaction)
    password_callback: function untuk meminta 2FA jika diperlukan
    """

    app = Client(f"user_{user_id}", api_id=bot.api_id, api_hash=bot.api_hash)
    await app.start()

    try:
        sent_code = await app.send(
            functions.auth.SendCode(
                phone_number=phone_number,
                api_id=bot.api_id,
                api_hash=bot.api_hash,
                settings=types.CodeSettings(
                    allow_flashcall=False,
                    current_number=True,
                    allow_app_hash=True,
                )
            )
        )
    except errors.PhoneNumberInvalid:
        await code_callback("Nomor telepon tidak valid, silakan coba lagi.")
        await app.stop()
        return None

    # Simpan phone_code_hash untuk login
    phone_code_hash = sent_code.phone_code_hash

    # Minta OTP
    otp = await code_callback("Masukkan kode OTP (dengan spasi agar tidak terdeteksi):")

    # Gabungkan kode OTP (hilangkan spasi)
    otp_code = otp.replace(" ", "")

    try:
        user = await app.invoke(
            SignIn(phone_number=phone_number, phone_code_hash=phone_code_hash, phone_code=otp_code)
        )
    except errors.SessionPasswordNeeded:
        # 2FA diperlukan, minta password
        if password_callback:
            password = await password_callback("Masukkan 2FA password:")
            user = await app.invoke(SignInTwoStep(password=password))
        else:
            await code_callback("2FA diperlukan tapi password_callback tidak disediakan.")
            await app.stop()
            return None
    except errors.PhoneCodeInvalid:
        await code_callback("Kode OTP tidak valid, silakan coba lagi.")
        await app.stop()
        return None
    except Exception as e:
        await code_callback(f"Login gagal: {e}")
        await app.stop()
        return None

    # Setelah berhasil login, dapatkan session_string untuk disimpan di db
    session_string = await app.export_session_string()

    # Simpan session ke database
    await save_session(user_id, {"string_session": session_string})

    await app.stop()
    return session_string

async def check_session_valid(bot, user_id):
    session = await get_session(user_id)
    if not session:
        return False

    from pyrogram import Client as UserClient
    try:
        user_client = UserClient(
            f"user_{user_id}",
            api_id=bot.api_id,
            api_hash=bot.api_hash,
            session_string=session["session_data"]["string_session"],
        )
        await user_client.start()
        await user_client.stop()
        return True
    except Exception:
        await delete_session(user_id)
        return False
