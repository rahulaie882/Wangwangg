"""
╔══════════════════════════════════════════════════════╗
║   Instagram Account Creator — 99% Guaranteed        ║
║   Engine: instagrapi (most reliable library)        ║
║   Phone: 5sim.net                                   ║
║   Bot: Telegram                                     ║
╚══════════════════════════════════════════════════════╝
"""

import asyncio
import random
import string
import re
import os
import time
import json
import logging
import pyotp
import httpx
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)

from instagrapi import Client
from instagrapi.exceptions import (
    ChallengeRequired,
    SelectContactPointRecoveryForm,
    RecaptchaChallengeForm,
    BadPassword,
    UnknownError,
)

# ═══════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════

BOT_TOKEN   = "8801243530:AAH6r79WOK7uU35uk7bAdZFNh2-aDnNbeww"
FIVESIM_KEY = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjIwNTIxMDQsImlhdCI6MTc5MDUxNjEwNCwicmF5IjoiNDMzNjhkNTQ5NGNlM2YzM2UzNTYwMGE1ZGIxOTc0NWUiLCJzdWIiOjQ1NzU0ODh9.csk2R9FNfET5ZhvdjBsOpVX-lYiVTHZCPw7UYFpZcCMUhNtjWJ-BhI2vUXB4F_8kIxU1Xlm6nAg4yraJ5lW5jP9xoZHiT6bu7drW_klEBMZ6pSVak_0RjtyCE5wMXeBqnxbsijd7sYhNz9JVXzHud6Qp7Nbaqr-Xwpqz9ilycM353h8c8G2nxr7Csb8xNSOiy1KXU-5LGfa8mErxHqyRQnVsr7gXpnVlSg4sObdrXbzO17UabirAKga0C3O3_ISUD3lsZLI2QDSaFW2LU_jh5SPg6cuCZpg86_JSxAgleLEth2tdxN0_lryw-NUrGGRGSnbtHwVOM5xUeKqMlBrBrw"
COUNTRY     = "usa"
OPERATOR    = "any"
MAX_RETRY   = 3

# ── Sirf ROTATING residential proxy use karo ──────────
# webshare.io rotating proxy sabse best hai Instagram ke liye
# Baaki datacenter proxies Instagram detect kar leta hai

PROXIES = [
    # BEST — rotating residential (yeh wala rakho)
    "http://khanrayhan9910-rotate:Asutonu9@p.webshare.io:80",

    # Baaki proxies — rakhein agar upar wala kaam na kare
    "http://uncpjndo:w77Ebc0h2A@us6.cactussstp.com:3129",
    "http://hughmuir2:lisamarie11@us3.cactussstp.com:3129",
    "http://purevpn0s551451:9dpdlc2nfxgj@px022409.pointtoserver.com:10780",
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@ca-mon.pvdata.host:8080",
    "http://purevpn0s2232045:hww8fqbr72j0@px241102.pointtoserver.com:10780",
    "http://reseller3270s320237:7Grp9Gki@px023005.pointtoserver.com:10780",
    "http://hughmuir2:lisamarie11@uk3.cactussstp.com:3129",
]

BIOS = [
    "Digital Creator | Content & Lifestyle ✨",
    "📸 Content Creator | DM for Collabs",
    "Living my best life 🌟 | USA",
    "Creator & Influencer | Business DMs Open",
    "Just vibing 🎯 | Content & Lifestyle",
]

MEDIA_DIR     = "user_media"
SESSION_DIR   = "ig_sessions"
ACCOUNTS_FILE = "ig_accounts.txt"

os.makedirs(MEDIA_DIR,   exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════

def rnd_username() -> str:
    prefix = random.choice(["the","its","real","im","just","only","hey"])
    core   = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5,8)))
    num    = str(random.randint(10, 9999))
    return f"{prefix}_{core}{num}"

def rnd_password(n=14) -> str:
    chars = string.ascii_letters + string.digits + "!@#$"
    pwd   = (
        random.choice(string.ascii_uppercase) +
        random.choice(string.digits) +
        random.choice("!@#$") +
        ''.join(random.choices(chars, k=n-3))
    )
    return ''.join(random.sample(pwd, len(pwd)))

def rnd_name() -> str:
    first = random.choice([
        "Alex","Jordan","Riley","Morgan","Casey",
        "Drew","Quinn","Sam","Chris","Taylor",
        "Jamie","Blake","Avery","Logan","Parker"
    ])
    last = random.choice([
        "Smith","Rivera","Chen","Patel","Moore",
        "Garcia","Kim","Hassan","Brown","Lee",
        "Wilson","Davis","Martin","Anderson","Thomas"
    ])
    return f"{first} {last}"

def rnd_bday() -> dict:
    return {
        "day":   random.randint(1, 28),
        "month": random.randint(1, 12),
        "year":  random.randint(1990, 2002),
    }

def e164(phone: str) -> str:
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        digits = "1" + digits
    return f"+{digits}"

def get_proxy() -> str | None:
    return random.choice(PROXIES) if PROXIES else None

def get_local_media() -> list:
    if not os.path.exists(MEDIA_DIR):
        return []
    return sorted([
        os.path.join(MEDIA_DIR, f)
        for f in os.listdir(MEDIA_DIR)
        if f.lower().endswith(("jpg","jpeg","png"))
    ])

async def save_account(creds: dict):
    def _w():
        idx = 1
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                idx = f.read().count("╔══") + 1
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = (
            f"\n╔══ Account #{idx} ══════════════════════╗\n"
            f"║  Username  : @{creds['username']}\n"
            f"║  Password  : {creds['password']}\n"
            f"║  Phone     : {creds['phone']}\n"
            f"║  Name      : {creds['name']}\n"
            f"║  User ID   : {creds.get('user_id','N/A')}\n"
            f"║  2FA Key   : {creds.get('totp_secret','N/A')}\n"
            f"║  Session   : {creds.get('session_file','N/A')}\n"
            f"║  Created   : {ts}\n"
            f"╚════════════════════════════════════════╝\n"
        )
        with open(ACCOUNTS_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    await asyncio.to_thread(_w)

# ═══════════════════════════════════════
#  5SIM
# ═══════════════════════════════════════

class FiveSim:
    BASE = "https://5sim.net/v1"

    def __init__(self):
        self.hdrs     = {
            "Authorization": f"Bearer {FIVESIM_KEY}",
            "Accept":        "application/json",
        }
        self.order_id = None
        self.phone    = None

    async def buy(self) -> str | None:
        url = f"{self.BASE}/user/buy/activation/{COUNTRY}/{OPERATOR}/instagram"
        try:
            async with httpx.AsyncClient(timeout=20) as c:
                r    = await c.get(url, headers=self.hdrs)
                data = r.json()
            if "id" not in data:
                log.error(f"5sim: number nahi mila → {data}")
                return None
            self.order_id = data["id"]
            self.phone    = data["phone"]
            log.info(f"📱 Number: {self.phone} | Order: {self.order_id}")
            return self.phone
        except Exception as e:
            log.error(f"5sim buy error: {e}")
            return None

    async def wait_otp(self, timeout=180) -> str | None:
        deadline = time.time() + timeout
        log.info(f"⏳ OTP wait ({timeout}s max)...")
        async with httpx.AsyncClient(timeout=20) as c:
            while time.time() < deadline:
                try:
                    r    = await c.get(
                        f"{self.BASE}/user/check/{self.order_id}",
                        headers=self.hdrs
                    )
                    data = r.json()
                    st   = data.get("status", "")

                    if st in ("RECEIVED", "FINISHED"):
                        sms_list = data.get("sms", [])
                        if sms_list:
                            text  = sms_list[-1].get("text", "")
                            match = re.search(r'\b(\d{6})\b', text)
                            if match:
                                otp = match.group(1)
                                log.info(f"✅ OTP: {otp}")
                                return otp

                    elif st == "CANCELED":
                        log.warning("5sim ne number cancel kar diya.")
                        return None

                except Exception as e:
                    log.debug(f"OTP check: {e}")

                await asyncio.sleep(5)

        log.warning("OTP timeout.")
        return None

    async def cancel(self):
        if not self.order_id:
            return
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                await c.get(
                    f"{self.BASE}/user/cancel/{self.order_id}",
                    headers=self.hdrs
                )
            log.info(f"Order {self.order_id} cancel.")
        except Exception:
            pass

    async def finish(self):
        if not self.order_id:
            return
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                await c.get(
                    f"{self.BASE}/user/finish/{self.order_id}",
                    headers=self.hdrs
                )
        except Exception:
            pass

# ═══════════════════════════════════════
#  INSTAGRAPI WRAPPER
# ═══════════════════════════════════════

class IGCreator:
    """
    instagrapi se account create karo.
    Yeh library saari cheez internally handle karti hai:
    - Password encryption
    - Device fingerprint
    - Challenge / checkpoint
    - Session management
    """

    def __init__(self, proxy: str | None = None):
        self.proxy = proxy
        self.cl    = Client()

        # Proxy set karo
        if proxy:
            self.cl.set_proxy(proxy)

        # Random device settings
        self.cl.set_locale("en_US")
        self.cl.set_timezone_offset(-18000)  # US Eastern

        # Custom delay — human jaisa lag e
        self.cl.delay_range = [2, 5]

    async def register(
        self,
        phone:    str,
        otp:      str,
        username: str,
        password: str,
        name:     str,
        bday:     dict,
    ) -> dict | None:
        """Phone number se account register karo."""

        def _register():
            return self.cl.phone_register(
                phone=e164(phone),
                code=otp,
                username=username,
                password=password,
                first_name=name,
                year=bday["year"],
                month=bday["month"],
                day=bday["day"],
            )

        try:
            result = await asyncio.to_thread(_register)
            if result:
                log.info(f"✅ Account created: @{username} | ID: {self.cl.user_id}")
                return {
                    "user_id":  str(self.cl.user_id),
                    "username": username,
                    "session":  self.cl.get_settings(),
                }
        except ChallengeRequired as e:
            log.warning(f"Challenge required: {e}")
            # instagrapi apna challenge handler use karta hai
            # manually resolve karo
            try:
                resolved = await asyncio.to_thread(
                    self.cl.challenge_resolve, self.cl.last_json
                )
                if resolved:
                    return {
                        "user_id":  str(self.cl.user_id),
                        "username": username,
                        "session":  self.cl.get_settings(),
                    }
            except Exception as ce:
                log.error(f"Challenge resolve fail: {ce}")
        except Exception as e:
            log.error(f"Register error: {e}")

        return None

    async def set_bio(self, bio: str):
        try:
            def _set():
                self.cl.account_edit(biography=bio)
            await asyncio.to_thread(_set)
            log.info(f"Bio set: {bio}")
        except Exception as e:
            log.debug(f"Bio error: {e}")

    async def set_profile_pic(self, image_path: str):
        try:
            def _set():
                self.cl.account_change_picture(image_path)
            await asyncio.to_thread(_set)
            log.info(f"Profile pic set: {image_path}")
        except Exception as e:
            log.debug(f"Profile pic error: {e}")

    async def upload_post(self, image_path: str, caption: str = ""):
        try:
            def _upload():
                self.cl.photo_upload(image_path, caption=caption)
            await asyncio.to_thread(_upload)
            log.info(f"Post uploaded: {image_path}")
            return True
        except Exception as e:
            log.debug(f"Post upload error: {e}")
            return False

    async def enable_2fa(self) -> tuple[bool, str]:
        """TOTP 2FA enable karo."""
        try:
            def _enable():
                # TOTP seed generate karo
                seed_data = self.cl.totp_generate_seed()
                seed      = seed_data.get("seed", "")
                if not seed:
                    return False, ""

                # OTP banao
                totp = pyotp.TOTP(seed)
                code = totp.now()

                # Enable karo
                self.cl.totp_enable(code)
                return True, seed

            ok, secret = await asyncio.to_thread(_enable)
            if ok:
                log.info(f"🔒 2FA enabled! Secret: {secret}")
            return ok, secret

        except Exception as e:
            log.debug(f"2FA error: {e}")
            return False, ""

    def save_session(self, username: str) -> str:
        path = os.path.join(SESSION_DIR, f"{username}.json")
        settings = self.cl.get_settings()
        with open(path, "w") as f:
            json.dump(settings, f, indent=2)
        return path

# ═══════════════════════════════════════
#  PROXY CHECKER
# ═══════════════════════════════════════

async def check_proxies():
    global PROXIES
    if not PROXIES:
        return
    log.info(f"🔍 {len(PROXIES)} proxies check ho rahi hain...")
    good = []
    sem  = asyncio.Semaphore(10)

    async def chk(p):
        async with sem:
            try:
                prx = {"http://": p, "https://": p}
                async with httpx.AsyncClient(proxies=prx, timeout=8) as c:
                    r = await c.get("https://httpbin.org/ip")
                    if r.status_code == 200:
                        good.append(p)
                        log.info(f"✅ {p}")
            except Exception:
                log.debug(f"❌ {p}")

    await asyncio.gather(*[chk(p) for p in PROXIES])
    PROXIES = good if good else PROXIES  # Sab fail ho toh original rakh
    log.info(f"✅ Live proxies: {len(PROXIES)}")

# ═══════════════════════════════════════
#  MAIN CREATOR FLOW
# ═══════════════════════════════════════

async def create_account(status_cb=None) -> dict | None:

    async def st(msg: str):
        log.info(msg)
        if status_cb:
            try:
                await status_cb(msg)
            except Exception:
                pass

    for attempt in range(1, MAX_RETRY + 1):
        sms = FiveSim()
        ig  = None

        try:
            await st(f"🔄 Attempt {attempt}/{MAX_RETRY}...")

            # ── Step 1: Number kharido ──────────────────
            await st("📱 USA number kharida ja raha hai...")
            phone = await sms.buy()
            if not phone:
                await st("❌ Number nahi mila. Retry...")
                await asyncio.sleep(8)
                continue

            # ── Step 2: Creds generate karo ────────────
            username = rnd_username()
            password = rnd_password()
            name     = rnd_name()
            bday     = rnd_bday()

            await st(f"👤 Account details ready → @{username}")

            # ── Step 3: IG client banao ─────────────────
            proxy = get_proxy()
            ig    = IGCreator(proxy=proxy)
            log.info(f"🌐 Proxy: {proxy or 'Direct'}")

            # ── Step 4: OTP ka wait karo ────────────────
            await st(f"📤 OTP Instagram bhej raha hai → {e164(phone)}")
            # instagrapi phone_register internally SMS bhejta hai
            # Isliye pehle 5sim pe OTP wait shuru karte hain

            await st("⏳ OTP aa raha hai... (3 minute max)")
            otp = await sms.wait_otp(timeout=180)

            if not otp:
                await st("❌ OTP nahi aaya. Number cancel ho raha hai...")
                await sms.cancel()
                await asyncio.sleep(10)
                continue

            await st(f"✅ OTP mila: {otp}")
            await asyncio.sleep(2)

            # ── Step 5: Account register karo ──────────
            await st(f"🎯 Account create ho raha hai → @{username}")

            session = await ig.register(
                phone=phone,
                otp=otp,
                username=username,
                password=password,
                name=name,
                bday=bday,
            )

            if not session:
                await st("❌ Account create nahi hua. Retry...")
                await sms.cancel()
                await asyncio.sleep(12)
                continue

            # ── Step 6: Number finish karo ──────────────
            await sms.finish()
            await asyncio.sleep(3)

            # ── Step 7: Bio set karo ────────────────────
            await st("📝 Bio set ho rahi hai...")
            bio = random.choice(BIOS)
            await ig.set_bio(bio)
            await asyncio.sleep(2)

            # ── Step 8: Profile pic (agar hai) ──────────
            media = get_local_media()
            if media:
                await st("🖼️ Profile picture set ho rahi hai...")
                await ig.set_profile_pic(media[0])
                await asyncio.sleep(3)

            # ── Step 9: Posts upload ─────────────────────
            if len(media) > 1:
                for idx, img in enumerate(media[1:], 1):
                    await st(f"📤 Post {idx}/{len(media)-1} upload ho rahi hai...")
                    await ig.upload_post(img, caption=bio)
                    await asyncio.sleep(random.uniform(5, 10))

            # ── Step 10: 2FA enable ──────────────────────
            await st("🔒 2FA enable ho raha hai...")
            await asyncio.sleep(2)
            fa_ok, fa_secret = await ig.enable_2fa()

            # ── Step 11: Session save ────────────────────
            session_file = await asyncio.to_thread(ig.save_session, username)

            # ── Done! ────────────────────────────────────
            creds = {
                "username":     username,
                "password":     password,
                "phone":        phone,
                "name":         name,
                "user_id":      session.get("user_id", ""),
                "totp_secret":  fa_secret if fa_ok else "N/A",
                "session_file": session_file,
            }

            await save_account(creds)
            await st(f"🎉 Account ready! @{username}")
            return creds

        except Exception as e:
            log.error(f"Attempt {attempt} error: {e}")
            try:
                await sms.cancel()
            except Exception:
                pass
            if attempt < MAX_RETRY:
                wait = random.uniform(10, 20)
                await st(f"⏳ {wait:.0f}s baad retry...")
                await asyncio.sleep(wait)
            else:
                return None

    return None

# ═══════════════════════════════════════
#  TELEGRAM BOT
# ═══════════════════════════════════════

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *Instagram Creator Bot*\n\n"
        "*Commands:*\n"
        "`/create 3` — 3 accounts banao\n"
        "`/status`   — proxy + accounts status\n"
        "`/clear`    — photos delete karo\n\n"
        "*Photos:* Seedha bhejein.\n"
        "Pehli photo = profile pic\n"
        "Baaki = posts pe upload"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    photos   = len(get_local_media())
    proxies  = len(PROXIES)
    accounts = 0
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE) as f:
            accounts = f.read().count("╔══")
    await update.message.reply_text(
        f"📊 *Bot Status*\n\n"
        f"🖼️ Photos: `{photos}`\n"
        f"🌐 Proxies: `{proxies}`\n"
        f"✅ Accounts: `{accounts}`",
        parse_mode="Markdown"
    )

async def cmd_clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    count = 0
    if os.path.exists(MEDIA_DIR):
        for f in os.listdir(MEDIA_DIR):
            os.remove(os.path.join(MEDIA_DIR, f))
            count += 1
    await update.message.reply_text(f"🗑️ {count} photos delete ho gayi.")

async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    photo    = update.message.photo[-1]
    file     = await photo.get_file()
    ts       = int(time.time())
    rnd      = random.randint(100, 999)
    filename = os.path.join(MEDIA_DIR, f"img_{ts}_{rnd}.jpg")
    await file.download_to_drive(filename)
    total = len(get_local_media())
    await update.message.reply_text(
        f"✅ Photo save ho gayi!\n"
        f"📸 Total photos: `{total}`",
        parse_mode="Markdown"
    )

async def cmd_create(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "❓ Jaise likhein: `/create 3`", parse_mode="Markdown"
        )
        return

    try:
        count = int(ctx.args[0])
    except ValueError:
        await update.message.reply_text("❌ Sirf number likhein. `/create 3`", parse_mode="Markdown")
        return

    if count < 1 or count > 20:
        await update.message.reply_text("❌ 1 se 20 ke beech likhein.")
        return

    msg     = await update.message.reply_text(f"🚀 {count} accounts banaana shuru ho raha hai...")
    success = 0
    failed  = 0

    for i in range(1, count + 1):

        async def cb(text: str, _i=i):
            try:
                await msg.edit_text(f"[{_i}/{count}] {text}")
            except Exception:
                pass

        creds = await create_account(status_cb=cb)

        if creds:
            success += 1
            # Har account ka instant result bhejo
            try:
                result_text = (
                    f"✅ *Account #{success} Ready!*\n\n"
                    f"👤 `@{creds['username']}`\n"
                    f"🔑 `{creds['password']}`\n"
                    f"📱 `{creds['phone']}`\n"
                    f"🔒 2FA: `{creds.get('totp_secret','N/A')}`\n"
                    f"🆔 ID: `{creds.get('user_id','N/A')}`"
                )
                await update.message.reply_text(result_text, parse_mode="Markdown")
            except Exception:
                pass
        else:
            failed += 1

        # Next account se pehle thoda wait
        if i < count:
            wait = random.uniform(8, 15)
            await asyncio.sleep(wait)

    # Final message
    final = (
        f"🏁 *Kaam ho gaya!*\n\n"
        f"✅ Success: `{success}/{count}`\n"
        f"❌ Failed: `{failed}/{count}`"
    )
    try:
        await msg.edit_text(final, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(final, parse_mode="Markdown")

    # Accounts file bhejo
    if os.path.exists(ACCOUNTS_FILE) and success > 0:
        try:
            await update.message.reply_document(
                document=open(ACCOUNTS_FILE, "rb"),
                caption=f"📄 {success} accounts ki poori details"
            )
        except Exception as e:
            log.error(f"File send error: {e}")

# ═══════════════════════════════════════
#  STARTUP
# ═══════════════════════════════════════

async def on_start(app: Application):
    log.info("🔍 Proxy check shuru...")
    await check_proxies()
    if not PROXIES:
        log.warning("⚠️  Koi live proxy nahi mili! Direct connection chalega.")
    log.info("🤖 Bot ready hai!")

def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_start)
        .build()
    )

    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("clear",  cmd_clear))
    app.add_handler(CommandHandler("create", cmd_create))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    log.info("🤖 Bot chalu!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
