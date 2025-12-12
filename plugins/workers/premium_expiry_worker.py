import asyncio, time
from database import database as db
import config

async def premium_expiry_worker(app):
    while True:
        users = db.get_all_premium_users()
        now = time.time()
        for u in users:
            expiry_ts = u.get("expiry_ts", 0)
            if expiry_ts <= now:
                # remove premium
                db.premium_col.delete_one({"user_id": u["user_id"]})
                try:
                    await app.send_message(u["user_id"], "⚠️ **Your Premium Has Expired!**\nUse /premium to renew.")
                except:
                    pass
                try:
                    await app.send_message(config.OWNER_ID, f"ℹ️ Premium expired for user {u['user_id']}")
                except:
                    pass
        await asyncio.sleep(60)