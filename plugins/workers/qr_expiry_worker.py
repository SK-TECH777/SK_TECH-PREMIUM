import asyncio, time
from database import database as db
import config

async def qr_expiry_worker(app):
    while True:
        pendings = db.get_all_pending_requests()
        now = time.time()
        for p in pendings:
            if p.get("expires_at", 0) <= now:
                try:
                    await app.send_message(p["user_id"], f"⚠️ QR EXPIRED\n❌ PAYMENT NOT RECEIVED\n✉️ {config.ADMIN_USERNAME}")
                except:
                    pass
                db.expire_and_delete_request(p["req_id"])
        await asyncio.sleep(60)