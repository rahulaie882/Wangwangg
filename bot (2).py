import asyncio
import random
import string
import httpx
import json
import re
import time
import os
import logging
import pyotp
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)
from playwright.async_api import async_playwright
from twocaptcha import TwoCaptcha

# ─── CONFIG ────────────────────────────────────────────────────────────────

BOT_TOKEN = "8979340651:AAFG1IkfQ7LQ71v-0tKPPaD2dH5MfWf5sOY"   # BotFather se token yahan daalein
CHAT_ID   = "7010776848"              # Apna chat ID

CONFIG = {
    "twocaptcha_key": "6498bcd403bd611438b1fb68568355b1",
    "fivesim_key":    "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjIwNTIxMDQsImlhdCI6MTc5MDUxNjEwNCwicmF5IjoiNDMzNjhkNTQ5NGNlM2YzM2UzNTYwMGE1ZGIxOTc0NWUiLCJzdWIiOjQ1NzU0ODh9.csk2R9FNfET5ZhvdjBsOpVX-lYiVTHZCPw7UYFpZcCMUhNtjWJ-BhI2vUXB4F_8kIxU1Xlm6nAg4yraJ5lW5jP9xoZHiT6bu7drW_klEBMZ6pSVak_0RjtyCE5wMXeBqnxbsijd7sYhNz9JVXzHud6Qp7Nbaqr-Xwpqz9ilycM353h8c8G2nxr7Csb8xNSOiy1KXU-5LGfa8mErxHqyRQnVsr7gXpnVlSg4sObdrXbzO17UabirAKga0C3O3_ISUD3lsZLI2QDSaFW2LU_jh5SPg6cuCZpg86_JSxAgleLEth2tdxN0_lryw-NUrGGRGSnbtHwVOM5xUeKqMlBrBrw",
    "country":        "usa",          # Ab USA ka number kharida jayega
    "operator":       "any",          # Operator
    "headless":       True,
    "max_retries":    3,
}

PROXIES = [
    "http://uncpjndo:w77Ebc0h2A@us6.cactussstp.com:3129",
    "http://uncpjndo:w77Ebc0h2A@hk1.cactussstp.com:8080",
    "http://bvmbsmie:shibby2511@it1.cactussstp.com:3129",
    "http://uncpjndo:w77Ebc0h2A@uk3.cactussstp.com:3129",
    "http://yefprelf:dr2gsmab@in1.cactussstp.com:8080",
    "http://bvmbsmie:shibby2511@au1.cactussstp.com:3129",
    "http://uncpjndo:w77Ebc0h2A@lv1.cactussstp.com:81",
    "http://hughmuir2:lisamarie11@us3.cactussstp.com:3129",
    "http://uncpjndo:w77Ebc0h2A@ca1.cactussstp.com:81",
    "http://yefprelf:dr2gsmab@ch1.cactussstp.com:8080",
    "http://uncpjndo:w77Ebc0h2A@my1.cactussstp.com:81",
    "http://purevpn0s551451:9dpdlc2nfxgj@px022409.pointtoserver.com:10780",
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@in-ban.pvdata.host:8080",
    "http://khanrayhan9910-rotate:Asutonu9@p.webshare.io:80",
    "http://1TCNvZkNJiZZPGX:sQfBBjZGVDqYl9V@37.49.150.244:41731",
    "http://uncpjndo:w77Ebc0h2A@uk2.cactussstp.com:81",
    "http://purevpn0s551451:9dpdlc2nfxgj@px591801.pointtoserver.com:10780",
    "http://purevpn0s2232045:hww8fqbr72j0@px241102.pointtoserver.com:10780",
    "http://1401:FVRHsSXw2DNK@p103.squidproxies.com:9238",
    "http://purevpn0s551451:9dpdlc2nfxgj@px022507.pointtoserver.com:10780",
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@it-mil.pvdata.host:8080",
    "http://reseller3270s320237:7Grp9Gki@px023005.pointtoserver.com:10780",
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@au-per.pvdata.host:8080",
    "http://purevpn0s8732217:i67s60ep@px152201.pointtoserver.com:10780",
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@my-kua.pvdata.host:8080",
    "http://purevpn0s7397024:6CU9ZvexLGTqpB@px400501.pointtoserver.com:10780",
    "http://reseller3270s320237:7Grp9Gki@px051703.pointtoserver.com:10780",
    "http://hughmuir2:lisamarie11@uk3.cactussstp.com:3129",
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@sk-bra.pvdata.host:8080",
    "http://purevpn0s551451:9dpdlc2nfxgj@px410701.pointtoserver.com:10780",
    "http://bvmbsmie:shibby2511@uk3.cactussstp.com:81",
    "http://uncpjndo:w77Ebc0h2A@au1.cactussstp.com:8080",
    "http://purevpn0s2232045:hww8fqbr72j0@px051003.pointtoserver.com:10780",
    "http://hughmuir2:lisamarie11@us6.cactussstp.com:3129",
    "http://purevpn0s11340994:ak3t35fp@px043006.pointtoserver.com:10780",
    "http://purevpn0s551451:9dpdlc2nfxgj@px420602.pointtoserver.com:10780",
    "http://purevpn0s7397024:6CU9ZvexLGTqpB@px040805.pointtoserver.com:10780",
    "http://hughmuir2:lisamarie11@uk2.cactussstp.com:8080",
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@ca-mon.pvdata.host:8080",
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@se-got.pvdata.host:8080",
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@id-jak.pvdata.host:8080"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

BIOS = [
    "Digital Creator | Content & Lifestyle",
    "📸 Creator | Business Inquiries Below",
    "Official Page | Creator & Influencer",
    "Content Creator | Collab? DM me",
]

# Media & Session storage folders
MEDIA_DIR = "user_media"
SESSION_DIR = "ig_sessions"
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ─── PROXY CHECKER ─────────────────────────────────────────────────────────

async def filter_live_proxies():
    global PROXIES
    if not PROXIES:
        log.info("⚠️ Koi proxy list mein nahi hai, direct connection use hoga.")
        return

    log.info("🔍 Proxies check ki ja rahi hain... Live proxies filter ho rahi hain.")
    valid_proxies = []
    
    for proxy in PROXIES:
        try:
            async with httpx.AsyncClient(proxies={"http://": proxy, "https://": proxy}, timeout=7.0) as client:
                r = await client.get("https://httpbin.org/ip")
                if r.status_code == 200:
                    valid_proxies.append(proxy)
                    log.info(f"✅ Live Proxy Found: {proxy}")
                else:
                    log.warning(f"❌ Dead Proxy Ignored (Status {r.status_code}): {proxy}")
        except Exception as e:
            log.warning(f"❌ Dead Proxy Ignored (Error): {proxy} -> {e}")
                
    PROXIES = valid_proxies
    log.info(f"✨ Total Live & Working Proxies saved: {len(PROXIES)}")

# ─── HELPERS ───────────────────────────────────────────────────────────────

def rnd_username() -> str:
    prefix = random.choice(["the","its","real","im","just"])
    core   = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5,8)))
    suffix = str(random.randint(10, 999))
    return f"{prefix}_{core}{suffix}"

def rnd_password(length=14) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=length))

def rnd_name() -> str:
    first = random.choice(["Alex","Jordan","Riley","Morgan","Casey","Drew","Quinn","Sam"])
    last  = random.choice(["Smith","Rivera","Chen","Patel","Moore","Garcia","Kim","Hassan"])
    return f"{first} {last}"

def rnd_birthday() -> dict:
    return {
        "month": str(random.randint(1, 12)),
        "day":   str(random.randint(1, 28)),
        "year":  str(random.randint(1990, 2000)),
    }

def get_proxy():
    if not PROXIES:
        return None
    return {"server": random.choice(PROXIES)}

def get_ua() -> str:
    return random.choice(USER_AGENTS)

async def save_to_file(creds: dict):
    filename = "ig_accounts.txt"
    def _write():
        index = 1
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                index = content.count("--- Account #") + 1

        live_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"--- Account #{index} ---\n")
            f.write(f"Email: {creds['email']}\n")
            f.write(f"Password: {creds['password']}\n")
            f.write(f"Username: @{creds['username']}\n")
            f.write(f"Phone: {creds['phone']}\n")
            f.write(f"Bio: {creds['bio']}\n")
            f.write(f"2FA Status: {creds.get('two_fa_status', 'Not Enabled')}\n")
            f.write(f"2FA Secret Key: {creds.get('two_fa_key', 'N/A')}\n")
            f.write(f"Session File: {creds.get('session_file', 'N/A')}\n")
            f.write(f"Live Date & Time: {live_time}\n")
            f.write(f"-----------------------\n\n")
    
    await asyncio.to_thread(_write)

def get_local_media() -> list:
    if not os.path.exists(MEDIA_DIR):
        return []
    files = [os.path.join(MEDIA_DIR, f) for f in os.listdir(MEDIA_DIR) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    files.sort()
    return files

# ─── 2CAPTCHA SOLVER INTEGRATION ───────────────────────────────────────────

async def solve_captcha_if_present(page) -> bool:
    try:
        captcha_elem = await page.query_selector('.g-recaptcha, iframe[src*="recaptcha"]')
        if not captcha_elem:
            return False

        log.info("🧩 Captcha detect hua! 2Captcha se solve kar rahe hain...")
        
        sitekey = await page.evaluate('''() => {
            const elem = document.querySelector('.g-recaptcha') || document.querySelector('iframe[src*="recaptcha"]');
            if (!elem) return null;
            if (elem.dataset && elem.dataset.sitekey) return elem.dataset.sitekey;
            const src = elem.src || '';
            const match = src.match(/k=([^&]+)/);
            return match ? match[1] : null;
        }''')

        if not sitekey:
            sitekey = await page.evaluate('''() => {
                for (let script of document.querySelectorAll('script')) {
                    let text = script.innerText;
                    let match = text.match(/["']sitekey["']\s*:\s*["']([^"']+)["']/);
                    if (match) return match[1];
                }
                return null;
            }''')

        if not sitekey:
            log.warning("⚠️ Captcha sitekey nahi mil saki.")
            return False

        solver = TwoCaptcha(CONFIG["twocaptcha_key"])
        result = await asyncio.to_thread(
            solver.recaptcha,
            sitekey=sitekey,
            url=page.url
        )
        
        code = result.get('code')
        if code:
            await page.evaluate(f'''() => {{
                const textarea = document.querySelector('#g-recaptcha-response') || document.querySelector('[name="g-recaptcha-response"]');
                if (textarea) {{
                    textarea.value = `{code}`;
                    textarea.style.display = 'block';
                }}
            }}''')
            await asyncio.sleep(2)
            log.info("✅ Captcha successfully solve aur inject ho gaya!")
            return True

    except Exception as e:
        log.error(f"❌ Captcha solve karte waqt error aaya: {e}")
    
    return False

# ─── MAIL.TM & 5SIM (WITH COUNTRY FILTER) ──────────────────────────────────

class MailTM:
    BASE = "https://api.mail.tm"

    def __init__(self):
        self.email    = None
        self.password = None
        self.token    = None

    async def create(self) -> str:
        async with httpx.AsyncClient(timeout=20) as c:
            r      = await c.get(f"{self.BASE}/domains")
            domain = r.json()["hydra:member"][0]["domain"]
            user   = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
            self.email    = f"{user}@{domain}"
            self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            await c.post(f"{self.BASE}/accounts", json={"address": self.email, "password": self.password})
            r = await c.post(f"{self.BASE}/token", json={"address": self.email, "password": self.password})
            self.token = r.json().get("token")
        return self.email

    async def wait_code(self, timeout=120) -> str | None:
        headers  = {"Authorization": f"Bearer {self.token}"}
        deadline = time.time() + timeout
        async with httpx.AsyncClient(timeout=20) as c:
            while time.time() < deadline:
                try:
                    r    = await c.get(f"{self.BASE}/messages", headers=headers)
                    msgs = r.json().get("hydra:member", [])
                    for msg in msgs:
                        d     = await c.get(f"{self.BASE}/messages/{msg['id']}", headers=headers)
                        body  = d.json().get("text","") + d.json().get("html","")
                        match = re.search(r'\b(\d{6})\b', body)
                        if match:
                            return match.group(1)
                except Exception:
                    pass
                await asyncio.sleep(5)
        return None

class FiveSim:
    BASE = "https://5sim.net/v1"

    def __init__(self):
        self.headers  = {"Authorization": f"Bearer {CONFIG['fivesim_key']}", "Accept": "application/json"}
        self.order_id = None
        self.phone    = None

    async def buy(self) -> str | None:
        country = CONFIG.get("country", "usa")
        operator = CONFIG.get("operator", "any")
        
        async with httpx.AsyncClient(timeout=20) as c:
            url = f"{self.BASE}/user/buy/activation/{country}/{operator}/instagram"
            r = await c.get(url, headers=self.headers)
            
            try:
                data = r.json()
            except Exception:
                log.error(f"❌ 5Sim Response Error: {r.text}")
                return None
            
            if "id" not in data:
                log.error(f"❌ Number purchase fail ho gaya. Response: {data}")
                return None
                
            self.order_id = data.get("id")
            self.phone    = data.get("phone")
        return self.phone

    async def wait_sms(self, timeout=120) -> str | None:
        deadline = time.time() + timeout
        async with httpx.AsyncClient(timeout=20) as c:
            while time.time() < deadline:
                try:
                    url = f"{self.BASE}/user/check/{self.order_id}"
                    r = await c.get(url, headers=self.headers)
                    data = r.json()
                    
                    if data.get("status") == "RECEIVED":
                        sms = data.get("sms", [{}])
                        text = sms[0].get("text", "") if sms else ""
                        match = re.search(r'\b(\d{6})\b', text)
                        if match:
                            return match.group(1)
                except Exception:
                    pass
                await asyncio.sleep(5)
        return None

    async def cancel(self):
        if not self.order_id:
            return
        async with httpx.AsyncClient(timeout=10) as c:
            try:
                url = f"{self.BASE}/user/cancel/{self.order_id}"
                await c.get(url, headers=self.headers)
            except Exception:
                pass

# ─── BROWSER & POST AUTOMATION ─────────────────────────────────────────────

async def human_type(page, selector: str, text: str):
    await page.click(selector)
    for ch in text:
        await page.keyboard.type(ch, delay=random.randint(60, 200))
    await asyncio.sleep(random.uniform(0.3, 0.8))

async def field_ok(page, selector: str, timeout=5000) -> bool:
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:
        return False

async def upload_posts_to_ig(page, image_paths: list, status_cb):
    if not image_paths:
        return
    
    for idx, img_path in enumerate(image_paths, start=1):
        try:
            await status_cb(f"📤 Post {idx}/{len(image_paths)} upload ho rahi hai...")
            await page.goto("https://www.instagram.com/", wait_until="networkidle")
            await asyncio.sleep(3)

            create_btn = await page.query_selector('svg[aria-label="New Post"], span:has-text("Create")')
            if create_btn:
                await create_btn.click()
                await asyncio.sleep(2)

                file_input = await page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(img_path)
                    await asyncio.sleep(3)

                    for _ in range(3):
                        next_btn = await page.query_selector('button:has-text("Next"), button:has-text("Share")')
                        if next_btn:
                            await next_btn.click()
                            await asyncio.sleep(3)
                    
                    await status_cb(f"✅ Post {idx} successfully publish ho gayi!")
                    await asyncio.sleep(5)
        except Exception as e:
            await status_cb(f"⚠️ Post {idx} upload fail: {e}")

async def enable_authenticator_2fa(page, status_cb) -> tuple[bool, str]:
    await status_cb("🔒 Authenticator App 2FA enable ki ja rahi hai...")
    try:
        await page.goto("https://www.instagram.com/accounts/security_privacy/", wait_until="networkidle")
        await asyncio.sleep(3)
        two_fa_link = await page.query_selector('a[href*="two_factor"]')
        if two_fa_link:
            await two_fa_link.click()
            await asyncio.sleep(2)
            app_radio = await page.query_selector('input[value="TOTP"], span:has-text("Authentication app")')
            if app_radio:
                await app_radio.click()
                await asyncio.sleep(1.5)
                next_btn = await page.query_selector('button:has-text("Next")')
                if next_btn:
                    await next_btn.click()
                    await asyncio.sleep(3)
                    manual_setup = await page.query_selector('span:has-text("Can\'t scan"), button:has-text("setup manually")')
                    if manual_setup:
                        await manual_setup.click()
                        await asyncio.sleep(2)
                    
                    secret_elem = await page.query_selector('code, span[class*="key"]')
                    secret_key = ""
                    if secret_elem:
                        secret_key = await secret_elem.inner_text()
                        secret_key = secret_key.strip().replace(" ", "")
                    else:
                        body_text = await page.inner_text("body")
                        match = re.search(r'\b([A-Z2-7]{16,32})\b', body_text)
                        if match:
                            secret_key = match.group(1)
                    
                    if secret_key:
                        totp = pyotp.TOTP(secret_key)
                        current_otp = totp.now()
                        next_btn2 = await page.query_selector('button:has-text("Next")')
                        if next_btn2:
                            await next_btn2.click()
                            await asyncio.sleep(2)
                        
                        otp_input = await page.query_selector('input[name="verificationCode"], input[type="text"]')
                        if otp_input:
                            await otp_input.click()
                            for ch in current_otp:
                                await page.keyboard.type(ch, delay=random.randint(50, 150))
                            await asyncio.sleep(1)
                            confirm_btn = await page.query_selector('button:has-text("Confirm"), button:has-text("Next"), button[type="submit"]')
                            if confirm_btn:
                                await confirm_btn.click()
                                await asyncio.sleep(3)
                                return True, secret_key
        return False, "N/A"
    except Exception as e:
        return False, "N/A"

# ─── CORE ACCOUNT CREATOR WITH RETRY LOGIC ─────────────────────────────────

async def create_ig_account(status_cb=None) -> dict | None:
    async def status(msg: str):
        log.info(msg)
        if status_cb:
            await status_cb(f"⚙️ {msg}")

    max_retries = CONFIG.get("max_retries", 3)
    
    for attempt in range(1, max_retries + 1):
        mail = MailTM()
        sms  = FiveSim()
        browser = None
        
        try:
            await status(f"🔄 Attempt {attempt}/{max_retries} shuru ho raha hai...")
            
            await status("📧 Temp email create ho rahi hai...")
            email = await mail.create()

            await status(f"📱 {CONFIG['country'].upper()} ka phone number kharida ja raha hai...")
            phone = await sms.buy()
            if not phone:
                await status("❌ Phone number allocate nahi ho saka, retry kar rahe hain...")
                continue

            media_files = get_local_media()
            profile_pic = media_files[0] if media_files else None
            post_images = media_files

            creds = {
                "email":         email,
                "phone":         phone,
                "username":      rnd_username(),
                "password":      rnd_password(),
                "name":          rnd_name(),
                "birthday":      rnd_birthday(),
                "bio":           random.choice(BIOS),
                "two_fa_status": "Not Enabled",
                "two_fa_key":    "N/A",
                "session_file":  "N/A"
            }

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=CONFIG["headless"],
                    proxy=get_proxy(),
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-infobars",
                        "--window-size=1280,800",
                        "--disable-blink-features=AutomationControlled"
                    ]
                )
                ctx = await browser.new_context(
                    user_agent=get_ua(),
                    viewport={"width": 1280, "height": 800},
                    locale="en-US"
                )
                
                await ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
                page = await ctx.new_page()

                try:
                    await status("🌐 Instagram signup page khul rahi hai...")
                    await page.goto("https://www.instagram.com/accounts/emailsignup/", wait_until="networkidle")
                    await asyncio.sleep(3)

                    await human_type(page, 'input[name="emailOrPhone"]', creds["email"])
                    await human_type(page, 'input[name="fullName"]',     creds["name"])
                    await human_type(page, 'input[name="username"]',     creds["username"])
                    await human_type(page, 'input[name="password"]',     creds["password"])
                    
                    await page.click('button[type="submit"]')
                    await asyncio.sleep(3)

                    await solve_captcha_if_present(page)

                    try:
                        bday = creds["birthday"]
                        if await field_ok(page, 'select[title="Month:"]', timeout=4000):
                            await page.select_option('select[title="Month:"]', bday["month"])
                            await page.select_option('select[title="Day:"]',   bday["day"])
                            await page.select_option('select[title="Year:"]',  bday["year"])
                            await page.click('button[type="submit"]')
                            await asyncio.sleep(3)
                    except Exception:
                        pass

                    if await field_ok(page, 'input[name="email_confirmation_code"]', timeout=5000):
                        await status("📬 Email confirmation code ka intezar hai...")
                        code = await mail.wait_code(timeout=120)
                        if code:
                            await human_type(page, 'input[name="email_confirmation_code"]', code)
                            await page.click('button[type="submit"]')
                            await asyncio.sleep(3)

                    if await field_ok(page, 'input[name="phone_number"]', timeout=5000):
                        await human_type(page, 'input[name="phone_number"]', creds["phone"])
                        await page.click('button[type="submit"]')
                        await asyncio.sleep(2)
                        
                        await status("📩 SMS verification code ka intezar hai...")
                        sms_code = await sms.wait_sms(timeout=120)
                        if sms_code:
                            await human_type(page, 'input[name="verification_code"]', sms_code)
                            await page.click('button[type="submit"]')
                            await asyncio.sleep(3)

                    if profile_pic:
                        await status("🖼️ Custom Profile Picture lagayi ja rahi hai...")
                        await page.goto("https://www.instagram.com/accounts/edit/", wait_until="networkidle")
                        await asyncio.sleep(2)
                        pic_input = await page.query_selector('input[type="file"]')
                        if pic_input:
                            await pic_input.set_input_files(profile_pic)
                            await asyncio.sleep(3)

                    try:
                        bio_field = await page.query_selector('textarea[name="biography"]')
                        if bio_field:
                            await bio_field.fill(creds["bio"])
                            submit = await page.query_selector('button[type="submit"]')
                            if submit:
                                await submit.click()
                                await asyncio.sleep(2)
                    except Exception:
                        pass

                    if post_images:
                        await upload_posts_to_ig(page, post_images, status)

                    success_2fa, secret_key = await enable_authenticator_2fa(page, status)
                    if success_2fa:
                        creds["two_fa_status"] = "Enabled (Authenticator App)"
                        creds["two_fa_key"] = secret_key

                    session_filename = os.path.join(SESSION_DIR, f"{creds['username']}.json")
                    await ctx.storage_state(path=session_filename)
                    creds["session_file"] = session_filename

                except Exception as inner_e:
                    raise inner_e

                finally:
                    if browser:
                        await browser.close()

            await save_to_file(creds)
            return creds

        except Exception as outer_e:
            log.error(f"Critical error on attempt {attempt}: {outer_e}")
            if browser:
                try:
                    await browser.close()
                except Exception:
                    pass
            await sms.cancel()
            if attempt < max_retries:
                await asyncio.sleep(5)
                continue
            return None
            
    return None

# ─── TELEGRAM BOT COMMANDS & HANDLERS ──────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Instagram Bulk Account Creator*\n\n"
        "1️⃣ Bot mein apni photos bhej dein (Pehli photo profile pic banegi aur sabhi photos posts par publish hongi).\n"
        "2️⃣ Phir command bhejein: `/create 3`",
        parse_mode="Markdown"
    )

async def handle_photos(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    
    filename = os.path.join(MEDIA_DIR, f"media_{int(time.time())}_{random.randint(100,999)}.jpg")
    await file.download_to_drive(filename)
    
    total_media = len(get_local_media())
    await update.message.reply_text(f"✅ Photo save ho gayi! Total media stored: {total_media}")

async def clear_media_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    count = 0
    if os.path.exists(MEDIA_DIR):
        for f in os.listdir(MEDIA_DIR):
            os.remove(os.path.join(MEDIA_DIR, f))
            count += 1
    await update.message.reply_text(f"🗑️ Sabhi {count} saved photos delete kar di gayi hain.")

async def create_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        args = ctx.args
        if not args:
            await update.message.reply_text("⚠️ Kripya sankhya batayein. Jaise: `/create 3`", parse_mode="Markdown")
            return

        count = int(args[0])
        media_count = len(get_local_media())
        if media_count == 0:
            await update.message.reply_text("⚠️ Pehle kam se kam ek photo bot mein bhej dein!")
            return

        msg = await update.message.reply_text(f"🚀 Total {count} accounts banana shuru ho raha hai ({media_count} photos ke sath)...")

        success_count = 0
        for i in range(1, count + 1):
            async def status_update(text: str):
                try:
                    await msg.edit_text(f"[{i}/{count}] {text}")
                except Exception:
                    pass

            creds = await create_ig_account(status_cb=status_update)
            if creds:
                success_count += 1
            else:
                await asyncio.sleep(5)

        if os.path.exists("ig_accounts.txt"):
            await update.message.reply_document(
                document=open("ig_accounts.txt", "rb"),
                caption=f"✅ Task Complete! Total {success_count}/{count} accounts ban gaye aur file mein details saved hain."
            )
        else:
            await update.message.reply_text("❌ Koi bhi account nahi ban saka.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def post_init(application: Application):
    await filter_live_proxies()

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear_media_command))
    app.add_handler(CommandHandler("create", create_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photos))
    
    log.info("🤖 Bot started successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()
