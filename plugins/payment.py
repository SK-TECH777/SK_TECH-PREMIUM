from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import config, time, asyncio
from helper_func import generate_upi_qr_text, generate_upi_qr_image, gen_token
from database import database as db

app: Client  # type: ignore

def premium_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"3 days - ₹{config.PLANS['3']['price']}", callback_data="plan_3")],
        [InlineKeyboardButton(f"7 days - ₹{config.PLANS['7']['price']}", callback_data="plan_7")],
        [InlineKeyboardButton(f"30 days - ₹{config.PLANS['30']['price']}", callback_data="plan_30")],
        [InlineKeyboardButton(f"Lifetime - ₹{config.PLANS['lifetime']['price']}", callback_data="plan_lifetime")],
        [InlineKeyboardButton("◀ BACK", callback_data="back_main")]
    ])

def payment_buttons(req_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✔ I Paid", callback_data=f"paid_{req_id}")],
        [InlineKeyboardButton("🔄 Regenerate QR", callback_data=f"regen_{req_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{req_id}")]
    ])

@Client.on_callback_query(filters.regex(r"^get_premium$"))
async def show_premium(c: Client, q: CallbackQuery):
    await q.answer()
    await q.message.edit_caption("WELCOME TO PREMIUM!!\nSelect a plan below.", reply_markup=premium_kb())

@Client.on_callback_query(filters.regex(r"^plan_(.+)$"))
async def plan_selected(c: Client, q: CallbackQuery):
    key = q.data.split("_",1)[1]
    plan = config.PLANS.get(key)
    if not plan:
        return await q.answer("Invalid plan.", show_alert=True)
    days = plan["days"]
    price = plan["price"]

    upi_uri = generate_upi_qr_text(config.UPI_ID, amount=float(price), note=f"Premium {days} days")
    qr_path = generate_upi_qr_image(upi_uri)

    expires_at_ts = time.time() + config.QR_EXPIRE_TIME

    req_id = db.create_payment_request(q.from_user.id, key, days, price, upi_uri, qr_path, expires_at_ts)

    caption = (f"💳 Plan: {days} Days\n"
               f"💰 Price: ₹{price}\n\n"
               f"⏳ QR expires in {config.QR_EXPIRE_TIME//60} minutes\n\n"
               f"📲 Scan the QR above using any UPI app. After payment press 'I Paid' and upload screenshot.")
    qr_msg = await q.message.reply_photo(qr_path, caption=caption, reply_markup=payment_buttons(req_id))

    # notify admin (owner)
    try:
        admin_text = (f"🔔 New Payment Request\n\nUser: {q.from_user.mention}\nReq ID: `{req_id}`\nPlan: {days} days\nPrice: ₹{price}\nExpires at (UTC): {time.ctime(expires_at_ts)}")
        admin_msg = await c.send_message(config.OWNER_ID, admin_text, reply_markup=None, parse_mode="markdown")
        db.set_admin_msg_id(req_id, admin_msg.message_id)
    except Exception:
        pass

    # start expiry watcher in background for this request
    asyncio.create_task(_watch_single_qr_expiry(req_id, q.from_user.id))
    await q.answer("QR generated. Pay using the QR.", show_alert=True)

@Client.on_callback_query(filters.regex(r"^paid_(.+)$"))
async def user_paid(c: Client, q: CallbackQuery):
    req_id = q.data.split("_",1)[1]
    req = db.get_payment_request(req_id)
    if not req:
        return await q.answer("Request not found.", show_alert=True)
    if req["status"] not in ["pending", "awaiting_proof", "awaiting_review"]:
        return await q.answer("This request cannot be claimed.", show_alert=True)
    # prompt user to upload screenshot
    await q.answer()
    await q.message.reply_text("Thanks — now upload the payment screenshot here (as a photo). The proof will be sent to admin for review.")
    db.set_request_status(req_id, "awaiting_proof")

@Client.on_callback_query(filters.regex(r"^regen_(.+)$"))
async def regen_qr(c: Client, q: CallbackQuery):
    req_id = q.data.split("_",1)[1]
    req = db.get_payment_request(req_id)
    if not req:
        return await q.answer("Request not found.", show_alert=True)
    if req["status"] not in ["pending", "awaiting_proof", "awaiting_review"]:
        return await q.answer("Cannot regenerate.", show_alert=True)
    # new QR
    plan = config.PLANS.get(req["plan_key"])
    qr_path = generate_upi_qr_image(generate_upi_qr_text(config.UPI_ID, amount=req["price"], note=f"Premium {req['days']} days"))
    new_expires = time.time() + config.QR_EXPIRE_TIME
    # update db
    db.set_request_status(req_id, "pending")
    db.payments_col.update_one({"req_id": req_id}, {"$set": {"upi_uri": config.UPI_ID, "qr_path": qr_path, "expires_at": new_expires, "proof_file_id": None}})
    await q.answer("QR regenerated.", show_alert=True)
    await q.message.reply_photo(qr_path, caption=f"🔁 Regenerated QR. Expires in {config.QR_EXPIRE_TIME//60} minutes.", reply_markup=payment_buttons(req_id))
    asyncio.create_task(_watch_single_qr_expiry(req_id, q.from_user.id))

@Client.on_callback_query(filters.regex(r"^cancel_(.+)$"))
async def cancel_req(c: Client, q: CallbackQuery):
    req_id = q.data.split("_",1)[1]
    rec = db.get_payment_request(req_id)
    if not rec:
        return await q.answer("Request not found.", show_alert=True)
    if rec["status"] in ["paid", "expired", "cancelled"]:
        return await q.answer("Cannot cancel.", show_alert=True)
    db.set_request_status(req_id, "cancelled")
    await q.answer("Cancelled", show_alert=True)
    await q.message.reply_text("Your payment request was cancelled. Use the premium menu to start again.")

# user uploads payment screenshot (photo)
@Client.on_message(filters.private & filters.photo)
async def receive_proof(c: Client, m):
    user_id = m.from_user.id
    req = db.get_user_pending_request(user_id)
    if not req:
        return
    if req["status"] not in ["awaiting_proof", "pending"]:
        return
    file_id = m.photo[-1].file_id
    db.attach_proof(req["req_id"], file_id)
    # forward proof to admin with approve/reject buttons
    try:
        admin_caption = (f"🔔 Payment Proof Received\n\nUser: {m.from_user.mention}\nReq ID: `{req['req_id']}`\nPlan: {req['days']} days\nPrice: ₹{req['price']}\n")
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        forwarded = await c.send_photo(config.OWNER_ID, file_id, caption=admin_caption, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_{req['req_id']}"),
             InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{req['req_id']}")]
        ]), parse_mode="markdown")
        db.set_admin_msg_id(req["req_id"], forwarded.message_id)
        await m.reply_text("Proof forwarded to admin. Wait for approval.")
    except Exception:
        await m.reply_text("Unable to forward proof to admin. Try later.")

# Admin callbacks
@Client.on_callback_query(filters.regex(r"^admin_approve_(.+)$"))
async def admin_approve(c: Client, q: CallbackQuery):
    if q.from_user.id != config.OWNER_ID:
        return await q.answer("Unauthorized", show_alert=True)
    req_id = q.data.split("_",2)[2]
    rec = db.get_payment_request(req_id)
    if not rec:
        return await q.answer("Request not found.", show_alert=True)
    db.mark_paid(req_id, q.from_user.id)
    try:
        await c.send_message(rec["user_id"], f"✅ Payment approved. You are premium for {rec['days']} days.")
    except:
        pass
    await q.answer("Approved", show_alert=True)
    await q.message.edit_text(f"✅ Approved by {q.from_user.mention}\nReq ID: `{req_id}`", parse_mode="markdown")

@Client.on_callback_query(filters.regex(r"^admin_reject_(.+)$"))
async def admin_reject(c: Client, q: CallbackQuery):
    if q.from_user.id != config.OWNER_ID:
        return await q.answer("Unauthorized", show_alert=True)
    req_id = q.data.split("_",2)[2]
    rec = db.get_payment_request(req_id)
    if not rec:
        return await q.answer("Request not found", show_alert=True)
    db.mark_rejected(req_id, q.from_user.id)
    try:
        await c.send_message(rec["user_id"], f"❌ Your payment proof was rejected by admin. Please try again.")
    except:
        pass
    await q.answer("Rejected", show_alert=True)
    await q.message.edit_text(f"❌ Rejected by {q.from_user.mention}\nReq ID: `{req_id}`", parse_mode="markdown")

# QR expiry watcher for single request
async def _watch_single_qr_expiry(req_id: str, user_id: int):
    await asyncio.sleep(config.QR_EXPIRE_TIME)
    req = db.get_payment_request(req_id)
    if not req:
        return
    if req["status"] in ["paid", "rejected", "cancelled"]:
        return
    # expired -> notify user and delete record
    try:
        await app.send_message(user_id, f"⚠️ QR EXPIRED\n❌ PAYMENT NOT RECEIVED\n✉️ {config.ADMIN_USERNAME}")
    except:
        pass
    db.expire_and_delete_request(req_id)