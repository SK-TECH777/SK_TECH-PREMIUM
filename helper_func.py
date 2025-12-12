import random, string, time, os, requests, qrcode
from datetime import datetime
import config

def gen_token(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def make_short_link(long_url: str) -> str:
    api = config.SHORTLINK_API or config.SHORTLINK_URL
    if not api:
        return long_url
    try:
        resp = requests.post(api, json={"url": long_url}, timeout=7)
        data = resp.json()
        return data.get("short") or data.get("url") or long_url
    except Exception:
        return long_url

def generate_upi_qr_text(upiid: str, amount: float = 0.0, note: str = "Premium"):
    params = f"upi://pay?pa={upiid}&pn=PREMIUM&cu=INR"
    if amount:
        params += f"&am={amount:.2f}"
    if note:
        params += f"&tn={note}"
    return params

def generate_upi_qr_image(upi_uri: str, filename: str = None) -> str:
    if filename is None:
        filename = f"qr_{int(time.time())}.png"
    save_dir = os.path.join(os.getcwd(), "assets")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    img = qrcode.make(upi_uri)
    img.save(save_path)
    return save_path