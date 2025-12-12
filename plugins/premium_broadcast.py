from pyrogram import Client, filters
import config
from database import database as db

app: Client  # type: ignore

@Client.on_message(filters.command("pbroadcast") & filters.user(config.OWNER_ID))
async def pbroadcast_handler(client, message):
    if len(message.command) < 2:
        return await message.reply("ℹ️ Usage: /pbroadcast Your message")
    text = message.text.split(" ", 1)[1]
    users = list(db.get_all_premium_users())
    total = len(users)
    sent = 0
    await message.reply(f"📢 Starting Premium Broadcast to {total} users...")
    for user in users:
        try:
            await client.send_message(user["user_id"], text)
            sent += 1
        except:
            pass
    await client.send_message(config.OWNER_ID, f"📢 Premium Broadcast Completed\nTotal users: {total}\nDelivered: {sent}")