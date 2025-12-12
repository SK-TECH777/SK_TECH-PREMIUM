from pyrogram import Client, filters
from datetime import datetime, timedelta
import time
import config
from database import database as db

app: Client  # type: ignore

@Client.on_message(filters.command("premium_logs") & filters.user(config.OWNER_ID))
async def premium_logs_handler(client, message):
    logs = list(db.history_col.find({}))
    today = 0
    week = 0
    month = 0
    total = 0
    now = datetime.now()
    for entry in logs:
        amt = int(entry.get("amount", 0))
        ts = entry.get("timestamp", time.time())
        dt = datetime.fromtimestamp(ts)
        total += amt
        if dt.date() == now.date():
            today += amt
        if now - dt <= timedelta(days=7):
            week += amt
        if dt.year == now.year and dt.month == now.month:
            month += amt
    active_prem = db.premium_col.count_documents({})
    total_prem = db.premium_col.count_documents({})
    text = (
        "📊 **Premium Logs Panel**\n\n"
        f"💰 **Today's Earnings:** ₹{today}\n"
        f"📅 **This Week:** ₹{week}\n"
        f"🗓️ **This Month:** ₹{month}\n"
        f"🏦 **Total Earnings:** ₹{total}\n\n"
        f"👤 **Active Premium Users:** {active_prem}\n"
        f"📁 **Total Premium Users:** {total_prem}\n"
    )
    await message.reply(text)