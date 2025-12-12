from pymongo import MongoClient
from datetime import datetime, timedelta
import time, random, string, os
import config

_client = MongoClient(config.DATABASE_URL)
_db = _client[config.DATABASE_NAME]

users_col = _db.get_collection("users")
premium_col = _db.get_collection("premium")
tokens_col = _db.get_collection("verify_tokens")
payments_col = _db.get_collection("payment_requests")
history_col = _db.get_collection("payment_history")

# indexes
users_col.create_index("user_id", unique=True)
premium_col.create_index("user_id", unique=True)
tokens_col.create_index("token", unique=True)
payments_col.create_index("req_id", unique=True)
history_col.create_index("txn_id", unique=True)

def _gen_req_id(length: int = 10):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

# VERIFY functions (kept minimal)
def is_user_verified(user_id: int):
    rec = users_col.find_one({"user_id": user_id})
    if not rec:
        return False
    if not rec.get("is_verified", False):
        return False
    exp = rec.get("verified_until")
    if exp and isinstance(exp, datetime):
        if datetime.utcnow() > exp:
            users_col.update_one({"user_id": user_id}, {"$set": {"is_verified": False}})
            return False
        return True
    return False

def set_user_verified(user_id: int, duration_seconds: int):
    until = datetime.utcnow() + timedelta(seconds=duration_seconds)
    users_col.update_one({"user_id": user_id},
                         {"$set": {"is_verified": True, "verified_until": until, "verified_at": datetime.utcnow()}},
                         upsert=True)
    return until

# PAYMENT request functions
def create_payment_request(user_id: int, plan_key: str, days: int, price: int, upi_uri: str, qr_path: str, expires_at_ts: float):
    req_id = _gen_req_id(12)
    doc = {
        "req_id": req_id,
        "user_id": user_id,
        "plan_key": plan_key,
        "days": days,
        "price": price,
        "upi_uri": upi_uri,
        "qr_path": qr_path,
        "status": "pending",
        "created_at": time.time(),
        "expires_at": expires_at_ts,
        "proof_file_id": None,
        "admin_msg_id": None,
        "notes": None
    }
    payments_col.insert_one(doc)
    return req_id

def get_payment_request(req_id: str):
    return payments_col.find_one({"req_id": req_id})

def get_user_pending_request(user_id: int):
    return payments_col.find_one({"user_id": user_id, "status": {"$in": ["pending", "awaiting_proof", "awaiting_review"]}})

def get_all_pending_requests():
    return list(payments_col.find({"status": {"$in": ["pending", "awaiting_proof", "awaiting_review"]}}).sort("created_at", -1))

def set_request_status(req_id: str, status: str):
    payments_col.update_one({"req_id": req_id}, {"$set": {"status": status}})
    return payments_col.find_one({"req_id": req_id})

def attach_proof(req_id: str, file_id: str):
    payments_col.update_one({"req_id": req_id}, {"$set": {"proof_file_id": file_id, "status": "awaiting_review"}})
    return payments_col.find_one({"req_id": req_id})

def set_admin_msg_id(req_id: str, msg_id: int):
    payments_col.update_one({"req_id": req_id}, {"$set": {"admin_msg_id": msg_id}})

def mark_paid(req_id: str, admin_user_id: int):
    rec = payments_col.find_one({"req_id": req_id})
    if not rec:
        return None
    user_id = rec["user_id"]
    days = rec["days"]
    expiry_ts = time.time() + days*24*3600
    premium_col.update_one({"user_id": user_id}, {"$set": {"expiry_ts": expiry_ts, "plan_key": rec["plan_key"]}}, upsert=True)
    payments_col.update_one({"req_id": req_id}, {"$set": {"status": "paid", "approved_by": admin_user_id, "paid_at": time.time()}})
    history_col.insert_one({
        "txn_id": req_id,
        "user_id": user_id,
        "amount": rec["price"],
        "plan_key": rec["plan_key"],
        "status": "paid",
        "admin_id": admin_user_id,
        "timestamp": time.time()
    })
    return payments_col.find_one({"req_id": req_id})

def mark_rejected(req_id: str, admin_user_id: int):
    rec = payments_col.find_one({"req_id": req_id})
    if not rec:
        return None
    payments_col.update_one({"req_id": req_id}, {"$set": {"status": "rejected", "rejected_by": admin_user_id, "rejected_at": time.time()}})
    history_col.insert_one({
        "txn_id": req_id,
        "user_id": rec["user_id"],
        "amount": rec["price"],
        "plan_key": rec["plan_key"],
        "status": "rejected",
        "admin_id": admin_user_id,
        "timestamp": time.time()
    })
    return payments_col.find_one({"req_id": req_id})

def expire_and_delete_request(req_id: str):
    rec = payments_col.find_one({"req_id": req_id})
    if not rec:
        return None
    payments_col.delete_one({"req_id": req_id})
    history_col.insert_one({
        "txn_id": req_id,
        "user_id": rec["user_id"],
        "amount": rec["price"],
        "plan_key": rec["plan_key"],
        "status": "expired",
        "admin_id": None,
        "timestamp": time.time()
    })
    return rec

# PREMIUM helpers
def add_premium(user_id: int, days: int):
    expiry_ts = time.time() + days*24*3600
    premium_col.update_one({"user_id": user_id}, {"$set": {"expiry_ts": expiry_ts}}, upsert=True)
    return expiry_ts

def is_premium(user_id: int):
    rec = premium_col.find_one({"user_id": user_id})
    if not rec:
        return False
    return rec.get("expiry_ts", 0) > time.time()

def get_premium_expiry(user_id: int):
    rec = premium_col.find_one({"user_id": user_id})
    return rec.get("expiry_ts") if rec else None

def get_all_premium_users():
    return list(premium_col.find({}))