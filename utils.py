from pyrogram.types import Message, CallbackQuery

async def edit_or_reply(obj, text, **kwargs):
    try:
        if isinstance(obj, CallbackQuery):
            await obj.message.edit(text, **kwargs)
        elif isinstance(obj, Message):
            await obj.reply(text, **kwargs)
    except Exception as e:
        print("edit_or_reply error:", e)

