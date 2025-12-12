import os

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "8352104584:AAGLADxKk1BMmnAwSpVdNrzPQpwJ-aUtSvs")
APP_ID = int(os.getenv("APP_ID", "22128383"))
API_HASH = os.getenv("API_HASH", "7992b5c5c9c6d34276c3dce9e46ba879")
OWNER_ID = int(os.getenv("OWNER_ID", "5960133511"))

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb+srv://sktech007:sktech007@cluster0.utm4vj5.mongodb.net/?appName=Cluster0")
DATABASE_NAME = os.getenv("DATABASE_NAME", "SkAnime")

VERIFY_MODE = os.getenv("VERIFY_MODE", "True").lower() in ("1","true","yes")
VERIFY_EXPIRE = int(os.getenv("VERIFY_EXPIRE", 86400))

SHORTLINK_API = os.getenv("SHORTLINK_API", "")
SHORTLINK_URL = os.getenv("SHORTLINK_URL", "")

VERIFICATION_BANNER = os.getenv("VERIFICATION_BANNER", "assets/verification_banner.jpg")
START_PIC = os.getenv("START_PIC", "assets/start_banner.jpg")

# Premium plan prices (INR)
PLANS = {
    "3": {"days": 3, "price": 25},
    "7": {"days": 7, "price": 49},
    "30": {"days": 30, "price": 99},
    "lifetime": {"days": 36500, "price": 399}
}

# UPI / Admin config
UPI_ID = os.getenv("UPI_ID", "sanjaykingboy9597-1@okicici")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@Minato_Sencie")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@Minato_Sencie")
QR_EXPIRE_TIME = int(os.getenv("QR_EXPIRE_TIME", 1200))

TG_BOT_WORKERS = int(os.getenv("TG_BOT_WORKERS", "50"))
