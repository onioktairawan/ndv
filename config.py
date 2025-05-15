import os

API_ID = int(os.getenv("API_ID", "14359445"))
API_HASH = os.getenv("API_HASH", "2f409670095a6bc7f6faa5b1324df2f6")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7768837888:AAFp9J3EwuaNL_c7MRXAzbFWdI2uYyM1Mhw")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://idopop3:Irawanoni@oni.a8z7e6x.mongodb.net/?retryWrites=true&w=majority&appName=oni")

# Session expire time in seconds (30 minutes)
SESSION_EXPIRE = 1800
ITEMS_PER_PAGE = 6
