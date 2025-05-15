from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from db import get_session, update_last_active
from config import ITEMS_PER_PAGE
from pyrogram import Client as UserClient

async def fetch_user_chats(user_client):
    dialogs = []
    async for dialog in user_client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup", "channel"]:
            dialogs.append(dialog)
    return dialogs

def build_keyboard(chats, page, filter_type):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_chats = chats[start:end]

    buttons = []
    for chat in page_chats:
        chat_id = chat.chat.id
        chat_title = chat.chat.title or "No Title"
        buttons.append([
            InlineKeyboardButton(f"{chat_title[:30]}", callback_data=f"leave_{chat_id}")
        ])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{filter_type}_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{(len(chats)-1)//ITEMS_PER_PAGE+1}", callback_data="noop"))
    if end < len(chats):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{filter_type}_{page+1}"))
    buttons.append(nav_buttons)

    # Filter buttons
    filter_buttons = [
        InlineKeyboardButton("Filter: Semua", callback_data="filter_all"),
        InlineKeyboardButton("Filter: Grup/Publik", callback_data="filter_public"),
        InlineKeyboardButton("Filter: Privat", callback_data="filter_private"),
    ]
    buttons.append(filter_buttons)

    return InlineKeyboardMarkup(buttons)

@Client.on_callback_query(filters.regex("^show_chats$"))
async def show_chats(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    session = await get_session(user_id)
    if not session:
        await query.answer("Sesi kamu sudah habis, silakan login ulang.", show_alert=True)
        return

    user_client = UserClient(
        f"user_{user_id}",
        api_id=client.api_id,
        api_hash=client.api_hash,
        session_string=session["session_data"]["string_session"],
    )
    await user_client.start()

    all_chats = await fetch_user_chats(user_client)
    await update_last_active(user_id)

    # Simpan state chats dan page di memori atau db (disini contoh simpan di STATE dict)
    client.STATE = getattr(client, "STATE", {})
    client.STATE[user_id] = {"chats": all_chats, "page": 0, "filter": "all"}

    keyboard = build_keyboard(all_chats, 0, "all")
    await query.message.edit("Daftar Grup & Channel (Filter: Semua, Halaman 1)", reply_markup=keyboard)
    await user_client.stop()

@Client.on_callback_query(filters.regex("^page_"))
async def paginate(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data.split("_")
    filter_type = data[1]
    page = int(data[2])

    client.STATE = getattr(client, "STATE", {})
    state = client.STATE.get(user_id)
    if not state:
        await query.answer("Sesi kamu sudah habis atau tidak ada data, silakan ulangi.")
        return

    chats = state["chats"]
    if filter_type != "all":
        if filter_type == "public":
            chats = [c for c in chats if not getattr(c.chat, "is_private", False)]
        elif filter_type == "private":
            chats = [c for c in chats if getattr(c.chat, "is_private", False)]

    state["page"] = page
    state["filter"] = filter_type

    keyboard = build_keyboard(chats, page, filter_type)
    await query.message.edit(
        f"Daftar Grup & Channel (Filter: {filter_type.capitalize()}, Halaman {page+1}/{(len(chats)-1)//ITEMS_PER_PAGE +1})",
        reply_markup=keyboard,
    )

@Client.on_callback_query(filters.regex("^leave_"))
async def handle_leave_group(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    chat_id = int(data.split("_")[1])
    session = await get_session(user_id)
    if not session:
        await query.answer("Sesi kamu sudah habis, silakan login ulang.", show_alert=True)
        return

    from pyrogram import Client as UserClient
    user_client = UserClient(
        f"user_{user_id}",
        api_id=client.api_id,
        api_hash=client.api_hash,
        session_string=session["session_data"]["string_session"],
    )
    await user_client.start()
    try:
        await user_client.leave_chat(chat_id)
        await query.answer("Berhasil keluar dari grup/channel.")
        await query.message.delete()
    except Exception as e:
        await query.answer(f"Gagal keluar: {e}", show_alert=True)
    await user_client.stop()
