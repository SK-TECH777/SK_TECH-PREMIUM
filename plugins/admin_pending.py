from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import config, time
from database import database as db

app: Client  # type: ignore

@Client.on_message(filters.command("pending_payments") & filters.user(config.OWNER_ID))
async def pending_payments_cmd(c: Client, m):
    reqs = db.get_all_pending_requests()
    if not reqs:
        return await m.reply_text("✅ No pending payments.")
    for r in reqs:
        remaining = int((r["expires_at"] - time.time()) / 60)
        if remaining < 0: remaining = 0
        text = (f"👤 User: {r['user_id']}\n"
                f"🆔 Req ID: `{r['req_id']}`\n"
                f"💎 Plan: {r['days']} days\n"
                f"💰 Amount: ₹{r['price']}\n"
                f"⏳ Time left: {remaining} min\n")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{r['req_id']}"),
             InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{r['req_id']}")],
            [InlineKeyboardButton("Mark Expired", callback_data=f"admin_expire_{r['req_id']}")]
        ])
        await m.reply_text(text, reply_markup=kb, parse_mode="markdown")