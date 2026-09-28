import asyncio
import random
import string
import httpx
import re
import time
import os
import logging
import pyotp
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)
from playwright.async_api import async_playwright
from twocaptcha import TwoCaptcha

# ─── CONFIG ────────────────────────────────────────────────────────────────

BOT_TOKEN = "8948043707:AAFBVyGi1GQzEpijFyojD0lPd_COFXhdB5Q"
CHAT_ID   = "8963867689"

CONFIG = {
    "twocaptcha_key": "6498bcd403bd611438b1fb68568355b1",
    "fivesim_key":    "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjIwNTIxMDQsImlhdCI6MTc5MDUxNjEwNCwicmF5IjoiNDMzNjhkNTQ5NGNlM2YzM2UzNTYwMGE1ZGIxOTc0NWUiLCJzdWIiOjQ1NzU0ODh9.csk2R9FNfET5ZhvdjBsOpVX-lYiVTHZCPw7UYFpZcCMUhNtjWJ-BhI2vUXB4F_8kIxU1Xlm6nAg4yraJ5lW5jP9xoZHiT6bu7drW_klEBMZ6pSVak_0RjtyCE5wMXeBqnxbsijd7sYhNz9JVXzHud6Qp7Nbaqr-Xwpqz9ilycM353h8c8G2nxr7Csb8xNSOiy1KXU-5LGfa8mErxHqyRQnVsr7gXpnVlSg4sObdrXbzO17UabirAKga0C3O3_ISUD3lsZLI2QDSaFW2LU_jh5SPg6cuCZpg86_JSxAgleLEth2tdxN0_lryw-NUrGGRGSnbtHwVOM5xUeKqMlBrBrw",
    "country":        "usa",
    "operator":       "any",
    "headless":       True,
    "max_retries":    3,
}

PROXIES = [
    "http://uncpjndo:w77Ebc0h2A@Us6.cactussstp.com:3129",
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
    "http://g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2@id-jak.pvdata.host:8080",
]

# Mobile iPhone UAs — Instagram server pe zyada trusted hain
MOBILE_USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
]

BIOS = [
    "Digital Creator | Content & Lifestyle",
    "📸 Creator | Business Inquiries Below",
    "Official Page | Creator & Influencer",
    "Content Creator | Collab? DM me",
]

MEDIA_DIR   = "user_media"
SESSION_DIR = "ig_sessions"
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(SESSION_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger(__name__)

# ─── ANTI-DETECTION SCRIPT ─────────────────────────────────────────────────

STEALTH_JS = """
    // webdriver flag hata do
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

    // plugins — real browser jaisa
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const arr = [1, 2, 3, 4, 5];
            arr.item = function(i) { return this[i]; };
            arr.namedItem = function(n) { return null; };
            arr.refresh = function() {};
            return arr;
        }
    });

    // languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });

    // Chromium automation artifacts delete karo
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    delete window.__playwright;
    delete window.__pwInitScripts;

    // Chrome object add karo — headless mein nahi hota
    if (!window.chrome) {
        window.chrome = {
            app: { isInstalled: false, InstallState: {}, RunningState: {} },
            runtime: { onConnect: null, onMessage: null },
            loadTimes: function() { return {}; },
            csi: function() { return {}; }
        };
    }

    // Permission API spoof
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters)
    );

    // WebGL vendor spoof
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter.call(this, parameter);
    };
"""

# ─── PROXY / UA HELPERS ────────────────────────────────────────────────────

async def filter_live_proxies():
    global PROXIES
    if not PROXIES:
        return
    log.info("🔍 Proxies check ki ja rahi hain...")
    valid_proxies = []
    for proxy in PROXIES:
        try:
            # FIX: httpx 0.27 mein proxy= use hota hai, proxies= nahi
            async with httpx.AsyncClient(
                proxy=proxy,
                timeout=7.0
            ) as client:
                r = await client.get("https://httpbin.org/ip")
                if r.status_code == 200:
                    valid_proxies.append(proxy)
        except Exception:
            pass
    if valid_proxies:
        PROXIES = valid_proxies
    log.info(f"✨ Total Live Proxies: {len(PROXIES)}")


def get_proxy_for_playwright() -> dict | None:
    if not PROXIES:
        return None
    proxy_url = random.choice(PROXIES)
    parsed = urlparse(proxy_url)
    if parsed.username and parsed.password:
        server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
        return {
            "server":   server,
            "username": parsed.username,
            "password": parsed.password,
        }
    return {"server": proxy_url}


def get_mobile_ua() -> str:
    return random.choice(MOBILE_USER_AGENTS)

# ─── RANDOM DATA ───────────────────────────────────────────────────────────

def rnd_username() -> str:
    prefix = random.choice(["the", "its", "real", "im", "just"])
    core   = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 8)))
    suffix = str(random.randint(10, 999))
    return f"{prefix}_{core}{suffix}"


def rnd_password(length=14) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=length))


def rnd_name() -> str:
    first = random.choice(["Alex", "Jordan", "Riley", "Morgan", "Casey", "Drew", "Quinn", "Sam"])
    last  = random.choice(["Smith", "Rivera", "Chen", "Patel", "Moore", "Garcia", "Kim", "Hassan"])
    return f"{first} {last}"


def rnd_birthday() -> dict:
    return {
        "month": str(random.randint(1, 12)),
        "day":   str(random.randint(1, 28)),
        "year":  str(random.randint(1990, 2000)),
    }

# ─── FILE HELPERS ──────────────────────────────────────────────────────────

async def save_to_file(creds: dict):
    filename = "ig_accounts.txt"
    def _write():
        index = 1
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                index = f.read().count("--- Account #") + 1
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
    files = [
        os.path.join(MEDIA_DIR, f)
        for f in os.listdir(MEDIA_DIR)
        if f.lower().endswith(('png', 'jpg', 'jpeg'))
    ]
    files.sort()
    return files

# ─── CAPTCHA ───────────────────────────────────────────────────────────────

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
            return False
        solver = TwoCaptcha(CONFIG["twocaptcha_key"])
        result = await asyncio.to_thread(solver.recaptcha, sitekey=sitekey, url=page.url)
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
            return True
    except Exception:
        pass
    return False

# ─── INSTAGRAM POPUP / OVERLAY HANDLER ─────────────────────────────────────

async def dismiss_overlays(page):
    """
    Instagram kai tarah ke popups dikhata hai:
    - Cookie consent (GDPR)
    - "Use the app" banner
    - "Save login info" dialog
    - Notification permission
    Ye sab dismiss karta hai taaki signup form accessible ho.
    """
    overlay_map = [
        # Cookie consent — EU/US servers pe aata hai
        'button[data-cookiebanner="accept_button"]',
        'button:has-text("Allow all cookies")',
        'button:has-text("Allow essential and optional cookies")',
        'button:has-text("Accept All")',
        'button:has-text("Accept")',
        # "Not Now" dialogs
        'button:has-text("Not Now")',
        'button:has-text("Not now")',
        # "Use the app" interstitial
        'div[role="dialog"] button:has-text("Not now")',
        # Close buttons
        'button[aria-label="Close"]',
        'svg[aria-label="Close"]',
    ]
    for selector in overlay_map:
        try:
            btn = await page.query_selector(selector)
            if btn:
                visible = await btn.is_visible()
                if visible:
                    await btn.click()
                    log.info(f"🍪 Overlay dismiss kiya: {selector}")
                    await asyncio.sleep(random.uniform(1.0, 2.0))
        except Exception:
            pass


async def log_page_inputs(page) -> list:
    """Debug: page pe kaunse inputs hain ye log karta hai"""
    try:
        inputs = await page.evaluate("""
            () => Array.from(document.querySelectorAll('input')).map(i => ({
                name:        i.name        || '',
                type:        i.type        || '',
                placeholder: i.placeholder || '',
                ariaLabel:   i.getAttribute('aria-label') || '',
                id:          i.id          || '',
                visible:     i.offsetParent !== null
            }))
        """)
        log.info(f"🔍 Page inputs: {inputs}")
        return inputs
    except Exception:
        return []

# ─── MAIL.TM ───────────────────────────────────────────────────────────────

class MailTM:
    BASE = "https://api.mail.tm"

    def __init__(self):
        self.email    = None
        self.password = None
        self.token    = None

    async def create(self) -> str:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{self.BASE}/domains")
            domain = r.json()["hydra:member"][0]["domain"]
            user   = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
            self.email    = f"{user}@{domain}"
            self.password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            await c.post(f"{self.BASE}/accounts", json={"address": self.email, "password": self.password})
            r = await c.post(f"{self.BASE}/token",    json={"address": self.email, "password": self.password})
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
                        d    = await c.get(f"{self.BASE}/messages/{msg['id']}", headers=headers)
                        body = d.json().get("text", "") + d.json().get("html", "")
                        match = re.search(r'\b(\d{6})\b', body)
                        if match:
                            return match.group(1)
                except Exception:
                    pass
                await asyncio.sleep(5)
        return None

# ─── 5SIM ──────────────────────────────────────────────────────────────────

class FiveSim:
    BASE = "https://5sim.net/v1"

    def __init__(self):
        self.headers  = {"Authorization": f"Bearer {CONFIG['fivesim_key']}", "Accept": "application/json"}
        self.order_id = None
        self.phone    = None

    async def buy(self) -> str | None:
        country  = CONFIG.get("country",  "usa")
        operator = CONFIG.get("operator", "any")
        async with httpx.AsyncClient(timeout=20) as c:
            url = f"{self.BASE}/user/buy/activation/{country}/{operator}/instagram"
            r   = await c.get(url, headers=self.headers)
            try:
                data = r.json()
            except Exception:
                return None
            if "id" not in data:
                return None
            self.order_id = data.get("id")
            self.phone    = data.get("phone")
        return self.phone

    async def wait_sms(self, timeout=120) -> str | None:
        deadline = time.time() + timeout
        async with httpx.AsyncClient(timeout=20) as c:
            while time.time() < deadline:
                try:
                    url  = f"{self.BASE}/user/check/{self.order_id}"
                    r    = await c.get(url, headers=self.headers)
                    data = r.json()
                    if data.get("status") == "RECEIVED":
                        sms   = data.get("sms", [{}])
                        text  = sms[0].get("text", "") if sms else ""
                        match = re.search(r'\b(\d{6})\b', text)
                        if match:
                            return match.group(1)
                except Exception:
                    pass
                await asyncio.sleep(5)
        return None

    async def finish(self):
        """SMS milne ke baad order finish karo — balance waste na ho"""
        if not self.order_id:
            return
        async with httpx.AsyncClient(timeout=10) as c:
            try:
                url = f"{self.BASE}/user/finish/{self.order_id}"
                await c.get(url, headers=self.headers)
            except Exception:
                pass

    async def cancel(self):
        if not self.order_id:
            return
        async with httpx.AsyncClient(timeout=10) as c:
            try:
                url = f"{self.BASE}/user/cancel/{self.order_id}"
                await c.get(url, headers=self.headers)
            except Exception:
                pass

# ─── BROWSER HELPERS ───────────────────────────────────────────────────────

async def human_type_smart(page, selectors: list, text: str):
    """
    Multiple selectors try karta hai — pehla jo milta hai usme type karta hai.
    fill() se pehle try karta hai, keyboard fallback bhi hai.
    """
    for selector in selectors:
        try:
            element = await page.wait_for_selector(selector, timeout=6000, state="visible")
            if element:
                await element.click()
                await asyncio.sleep(random.uniform(0.3, 0.7))
                # Pehle fill() try karo (fast but less human)
                await element.fill(text)
                await asyncio.sleep(random.uniform(0.2, 0.5))
                # Verify fill kaam kiya
                val = await element.input_value()
                if val == text:
                    return
                # fill() fail hua — keyboard type use karo
                await element.fill("")
                for ch in text:
                    await page.keyboard.type(ch, delay=random.randint(60, 180))
                    if random.random() < 0.08:
                        await asyncio.sleep(random.uniform(0.1, 0.25))
                return
        except Exception:
            continue
    raise Exception(f"Failed to find or type into selectors: {selectors}")


async def smart_fill_by_evaluation(page, field_hints: list, text: str) -> bool:
    """
    Nuclear fallback: JS se input dhundh ke fill karo.
    Jab koi bhi selector kaam na kare tab use hota hai.
    """
    try:
        filled = await page.evaluate(f"""
            (hints) => {{
                const inputs = Array.from(document.querySelectorAll('input'));
                for (const hint of hints) {{
                    const found = inputs.find(i =>
                        (i.name && i.name.toLowerCase().includes(hint)) ||
                        (i.placeholder && i.placeholder.toLowerCase().includes(hint)) ||
                        (i.getAttribute('aria-label') && i.getAttribute('aria-label').toLowerCase().includes(hint)) ||
                        (i.type && i.type.toLowerCase().includes(hint))
                    );
                    if (found && found.offsetParent !== null) {{
                        found.focus();
                        found.value = "{text}";
                        found.dispatchEvent(new Event('input', {{bubbles: true}}));
                        found.dispatchEvent(new Event('change', {{bubbles: true}}));
                        return true;
                    }}
                }}
                return false;
            }}
        """, field_hints)
        return filled
    except Exception:
        return False


async def human_delay(min_sec=1.5, max_sec=3.5):
    await asyncio.sleep(random.uniform(min_sec, max_sec))


async def field_ok(page, selector: str, timeout=60000) -> bool:
    try:
        await page.wait_for_selector(selector, timeout=timeout, state="visible")
        return True
    except Exception:
        return False

# ─── IG POST UPLOAD ────────────────────────────────────────────────────────

async def upload_posts_to_ig(page, image_paths: list, status_cb):
    if not image_paths:
        return
    for idx, img_path in enumerate(image_paths, start=1):
        try:
            await status_cb(f"📤 Post {idx}/{len(image_paths)} upload ho rahi hai...")
            await page.goto("https://www.instagram.com/", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)
            create_btn = await page.query_selector(
                'svg[aria-label="New Post"], '
                'svg[aria-label="Create"], '
                'span:has-text("Create"), '
                'a[href="/create/select/"]'
            )
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

# ─── 2FA SETUP ─────────────────────────────────────────────────────────────

async def enable_authenticator_2fa(page, status_cb) -> tuple[bool, str]:
    await status_cb("🔒 Authenticator App 2FA enable ki ja rahi hai...")
    try:
        await page.goto(
            "https://www.instagram.com/accounts/security_privacy/",
            wait_until="networkidle",
            timeout=60000
        )
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
                    secret_key  = ""
                    if secret_elem:
                        secret_key = (await secret_elem.inner_text()).strip().replace(" ", "")
                    else:
                        body_text = await page.inner_text("body")
                        match = re.search(r'\b([A-Z2-7]{16,32})\b', body_text)
                        if match:
                            secret_key = match.group(1)
                    if secret_key:
                        totp        = pyotp.TOTP(secret_key)
                        current_otp = totp.now()
                        next_btn2   = await page.query_selector('button:has-text("Next")')
                        if next_btn2:
                            await next_btn2.click()
                            await asyncio.sleep(2)
                        otp_input = await page.query_selector('input[name="verificationCode"], input[type="text"]')
                        if otp_input:
                            await otp_input.click()
                            for ch in current_otp:
                                await page.keyboard.type(ch, delay=random.randint(50, 150))
                            await asyncio.sleep(1)
                            confirm_btn = await page.query_selector(
                                'button:has-text("Confirm"), '
                                'button:has-text("Next"), '
                                'button[type="submit"]'
                            )
                            if confirm_btn:
                                await confirm_btn.click()
                                await asyncio.sleep(3)
                                return True, secret_key
        return False, "N/A"
    except Exception:
        return False, "N/A"

# ─── MAIN ACCOUNT CREATOR ──────────────────────────────────────────────────

async def create_ig_account(status_cb=None) -> dict | None:

    async def status(msg: str):
        log.info(msg)
        if status_cb:
            await status_cb(f"⚙️ {msg}")

    max_retries = CONFIG.get("max_retries", 3)

    for attempt in range(1, max_retries + 1):
        mail    = MailTM()
        sms     = FiveSim()
        browser = None
        page    = None

        try:
            await status(f"🔄 Attempt {attempt}/{max_retries} shuru ho raha hai...")

            await status("📧 Temp email create ho rahi hai...")
            email = await mail.create()

            await status(f"📱 {CONFIG['country'].upper()} ka phone number kharida ja raha hai...")
            phone = await sms.buy()
            if not phone:
                await status("❌ Phone number allocate nahi ho saka, retry...")
                continue

            media_files = get_local_media()
            profile_pic = media_files[0] if media_files else None
            # FIX: profile pic ko posts se alag karo
            post_images = media_files[1:] if len(media_files) > 1 else []

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
                "session_file":  "N/A",
            }

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=CONFIG["headless"],
                    proxy=get_proxy_for_playwright(),
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-infobars",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-features=IsolateOrigins,site-per-process",
                        "--no-first-run",
                        "--no-zygote",
                        "--disable-gpu",
                        "--disable-software-rasterizer",
                        "--window-size=390,844",
                        "--hide-scrollbars",
                        "--mute-audio",
                    ]
                )

                # Mobile iPhone context — Instagram ke liye zyada trusted
                ua = get_mobile_ua()
                ctx = await browser.new_context(
                    user_agent=ua,
                    viewport={"width": 390, "height": 844},
                    device_scale_factor=3,
                    is_mobile=True,
                    has_touch=True,
                    locale="en-US",
                    timezone_id="America/New_York",
                    permissions=["geolocation"],
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Sec-Fetch-Mode": "navigate",
                    }
                )

                # Anti-detection stealth script inject karo
                await ctx.add_init_script(STEALTH_JS)
                page = await ctx.new_page()

                try:
                    # ── 1. Instagram signup page open karo ──
                    await status("🌐 Instagram signup page khul rahi hai...")
                    try:
                        await page.goto(
                            "https://www.instagram.com/accounts/emailsignup/",
                            wait_until="networkidle",
                            timeout=90000
                        )
                    except Exception:
                        # networkidle timeout — domcontentloaded pe fallback
                        await page.goto(
                            "https://www.instagram.com/accounts/emailsignup/",
                            wait_until="domcontentloaded",
                            timeout=60000
                        )

                    await human_delay(4.0, 7.0)

                    # ── 2. Redirect check — agar login page pe gaya to wapas jao ──
                    current_url = page.url
                    page_title  = await page.title()
                    log.info(f"📍 Landed: {current_url} | Title: {page_title}")

                    if "login" in current_url or current_url.rstrip("/") == "https://www.instagram.com":
                        log.info("🔁 Redirect mila — signup URL pe wapas ja raha hai...")
                        await page.goto(
                            "https://www.instagram.com/accounts/emailsignup/",
                            wait_until="networkidle",
                            timeout=60000
                        )
                        await human_delay(3.0, 5.0)

                    # ── 3. Overlays/popups dismiss karo ──
                    await dismiss_overlays(page)
                    await human_delay(2.0, 3.0)

                    # ── 4. Page inputs debug log ──
                    inputs_found = await log_page_inputs(page)
                    if not inputs_found:
                        log.warning("⚠️ Koi input nahi mila page pe — screenshot le raha hun")

                    # ── 5. Email field — comprehensive selectors ──
                    email_selectors = [
                        'input[name="emailOrPhone"]',
                        'input[name="email"]',
                        'input[type="email"]',
                        'input[autocomplete="email"]',
                        'input[autocomplete="username"]',
                        'input[placeholder*="email" i]',
                        'input[placeholder*="mobile" i]',
                        'input[aria-label*="email" i]',
                        'input[aria-label*="mobile" i]',
                        'input[aria-label*="phone" i]',
                    ]

                    # Wait for any input to appear
                    try:
                        await page.wait_for_selector(
                            ', '.join(email_selectors),
                            timeout=60000,
                            state="visible"
                        )
                    except Exception:
                        # Fallback: JS se fill karo
                        log.warning("⚠️ Standard selectors nahi mile — JS fallback use kar raha hun")
                        filled = await smart_fill_by_evaluation(
                            page, ["email", "phone", "mobile", "text"], creds["email"]
                        )
                        if not filled:
                            page_url   = page.url
                            page_title = await page.title()
                            screenshot_path = f"debug_attempt_{attempt}.png"
                            try:
                                await page.screenshot(path=screenshot_path, full_page=True)
                                log.error(f"📸 Debug screenshot: {screenshot_path}")
                            except Exception:
                                pass
                            raise Exception(
                                f"Signup form nahi mila. URL: {page_url} | Title: {page_title}"
                            )

                    await human_type_smart(page, email_selectors, creds["email"])
                    await human_delay(1.0, 2.0)

                    # ── 6. Full Name ──
                    await human_type_smart(page, [
                        'input[name="fullName"]',
                        'input[name="cueFullName"]',
                        'input[aria-label*="Full Name" i]',
                        'input[placeholder*="Full Name" i]',
                        'input[autocomplete="name"]',
                    ], creds["name"])
                    await human_delay(1.0, 2.0)

                    # ── 7. Username ──
                    await human_type_smart(page, [
                        'input[name="username"]',
                        'input[name="cueUsername"]',
                        'input[aria-label*="Username" i]',
                        'input[placeholder*="Username" i]',
                        'input[autocomplete="username"]',
                    ], creds["username"])
                    await human_delay(1.0, 2.0)

                    # ── 8. Password ──
                    await human_type_smart(page, [
                        'input[name="password"]',
                        'input[type="password"]',
                        'input[aria-label*="Password" i]',
                        'input[placeholder*="Password" i]',
                        'input[autocomplete="new-password"]',
                    ], creds["password"])
                    await human_delay(2.0, 3.5)

                    # ── 9. Submit ──
                    submit_selectors = [
                        'button[type="submit"]',
                        'button:has-text("Next")',
                        'button:has-text("Sign up")',
                        'button:has-text("Create")',
                    ]
                    for sel in submit_selectors:
                        try:
                            btn = await page.query_selector(sel)
                            if btn and await btn.is_visible():
                                await btn.click()
                                break
                        except Exception:
                            continue

                    await human_delay(4.0, 6.0)
                    await solve_captcha_if_present(page)

                    # ── 10. Birthday ──
                    try:
                        bday = creds["birthday"]
                        if await field_ok(page, 'select[title="Month:"]', timeout=25000):
                            await page.select_option('select[title="Month:"]', bday["month"])
                            await human_delay(0.8, 1.5)
                            await page.select_option('select[title="Day:"]',   bday["day"])
                            await human_delay(0.8, 1.5)
                            await page.select_option('select[title="Year:"]',  bday["year"])
                            await human_delay(1.0, 2.0)
                            submit_btn = await page.query_selector('button[type="submit"]')
                            if submit_btn:
                                await submit_btn.click()
                            await human_delay(3.0, 5.0)
                    except Exception:
                        pass

                    # ── 11. Email verification code ──
                    email_code_selectors = [
                        'input[name="email_confirmation_code"]',
                        'input[name="confirmationCode"]',
                        'input[aria-label*="confirmation" i]',
                        'input[placeholder*="code" i]',
                    ]
                    email_field_found = False
                    for sel in email_code_selectors:
                        if await field_ok(page, sel, timeout=35000):
                            email_field_found = True
                            break

                    if email_field_found:
                        await status("📬 Email confirmation code ka intezar hai...")
                        code = await mail.wait_code(timeout=120)
                        if code:
                            await human_type_smart(page, email_code_selectors, code)
                            await human_delay(1.0, 2.0)
                            submit_btn = await page.query_selector('button[type="submit"]')
                            if submit_btn:
                                await submit_btn.click()
                            await human_delay(3.0, 5.0)
                        else:
                            await status("⚠️ Email code nahi mila — continue kar raha hun...")

                    # ── 12. Phone verification ──
                    phone_selectors = [
                        'input[name="phone_number"]',
                        'input[type="tel"]',
                        'input[aria-label*="phone" i]',
                        'input[placeholder*="phone" i]',
                    ]
                    phone_field_found = False
                    for sel in phone_selectors:
                        if await field_ok(page, sel, timeout=30000):
                            phone_field_found = True
                            break

                    if phone_field_found:
                        await human_type_smart(page, phone_selectors, creds["phone"])
                        await human_delay(1.0, 2.0)
                        submit_btn = await page.query_selector('button[type="submit"]')
                        if submit_btn:
                            await submit_btn.click()
                        await human_delay(2.0, 4.0)

                        await status("📩 SMS verification code ka intezar hai...")
                        sms_code = await sms.wait_sms(timeout=120)
                        if sms_code:
                            # FIX: finish karo — balance waste na ho
                            await sms.finish()
                            sms_verify_selectors = [
                                'input[name="verification_code"]',
                                'input[name="sms_code"]',
                                'input[aria-label*="code" i]',
                                'input[placeholder*="code" i]',
                            ]
                            await human_type_smart(page, sms_verify_selectors, sms_code)
                            await human_delay(1.0, 2.0)
                            submit_btn = await page.query_selector('button[type="submit"]')
                            if submit_btn:
                                await submit_btn.click()
                            await human_delay(3.0, 5.0)
                        else:
                            await status("⚠️ SMS code nahi mila — continue kar raha hun...")

                    # ── 13. Profile picture ──
                    if profile_pic:
                        await status("🖼️ Profile Picture lagayi ja rahi hai...")
                        await page.goto(
                            "https://www.instagram.com/accounts/edit/",
                            wait_until="networkidle",
                            timeout=60000
                        )
                        await human_delay(2.0, 4.0)
                        pic_input = await page.query_selector('input[type="file"]')
                        if pic_input:
                            await pic_input.set_input_files(profile_pic)
                            await human_delay(3.0, 5.0)

                    # ── 14. Bio ──
                    try:
                        bio_field = await page.query_selector('textarea[name="biography"]')
                        if bio_field:
                            await bio_field.fill(creds["bio"])
                            await human_delay(1.0, 2.0)
                            submit_btn = await page.query_selector('button[type="submit"]')
                            if submit_btn:
                                await submit_btn.click()
                            await human_delay(2.0, 3.0)
                    except Exception:
                        pass

                    # ── 15. Posts upload ──
                    if post_images:
                        await upload_posts_to_ig(page, post_images, status)

                    # ── 16. 2FA enable ──
                    success_2fa, secret_key = await enable_authenticator_2fa(page, status)
                    if success_2fa:
                        creds["two_fa_status"] = "Enabled (Authenticator App)"
                        creds["two_fa_key"]    = secret_key

                    # ── 17. Session save ──
                    session_filename = os.path.join(SESSION_DIR, f"{creds['username']}.json")
                    await ctx.storage_state(path=session_filename)
                    creds["session_file"] = session_filename

                except Exception as inner_e:
                    # Screenshot + URL log on failure
                    if page:
                        try:
                            screenshot_path = f"error_attempt_{attempt}.png"
                            await page.screenshot(path=screenshot_path, full_page=True)
                            current_url = page.url
                            log.error(f"❌ Error Screenshot: {screenshot_path} | URL: {current_url}")
                        except Exception:
                            pass
                    raise inner_e

                finally:
                    if browser:
                        await browser.close()

            await save_to_file(creds)
            return creds

        except Exception as outer_e:
            log.error(f"🚨 Critical error on attempt {attempt}: {outer_e}")
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

# ─── TELEGRAM HANDLERS ─────────────────────────────────────────────────────

def is_authorized(update: Update) -> bool:
    """Sirf owner use kar sake bot ko"""
    return str(update.effective_user.id) == CHAT_ID


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Instagram Bulk Account Creator*\n\n"
        "📋 *Commands:*\n"
        "1️⃣ Pehle apni photos bhej dein bot mein\n"
        "2️⃣ `/create 3` — 3 accounts banao\n"
        "3️⃣ `/clear` — saved photos delete karo\n"
        "4️⃣ `/sessions` — session files delete karo\n\n"
        "⚡ Bot ready hai!",
        parse_mode="Markdown"
    )


async def handle_photos(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    photo    = update.message.photo[-1]
    file     = await photo.get_file()
    filename = os.path.join(MEDIA_DIR, f"media_{int(time.time())}_{random.randint(100, 999)}.jpg")
    await file.download_to_drive(filename)
    total = len(get_local_media())
    await update.message.reply_text(f"✅ Photo save ho gayi! Total media stored: {total}")


async def clear_media_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    count = 0
    if os.path.exists(MEDIA_DIR):
        for f in os.listdir(MEDIA_DIR):
            os.remove(os.path.join(MEDIA_DIR, f))
            count += 1
    await update.message.reply_text(f"🗑️ Sabhi {count} saved photos delete kar di gayi hain.")


async def clear_sessions_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return
    count = 0
    if os.path.exists(SESSION_DIR):
        for f in os.listdir(SESSION_DIR):
            os.remove(os.path.join(SESSION_DIR, f))
            count += 1
    await update.message.reply_text(f"🗑️ Sabhi {count} session files delete kar di gayi hain.")


async def create_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("❌ Unauthorized.")
        return

    try:
        args = ctx.args
        if not args:
            await update.message.reply_text(
                "⚠️ Kripya sankhya batayein. Jaise: `/create 3`",
                parse_mode="Markdown"
            )
            return

        count = int(args[0])
        if count < 1 or count > 50:
            await update.message.reply_text("⚠️ 1 se 50 ke beech number do.")
            return

        media_count = len(get_local_media())
        if media_count == 0:
            await update.message.reply_text("⚠️ Pehle kam se kam ek photo bot mein bhej dein!")
            return

        msg = await update.message.reply_text(f"🚀 Total {count} accounts banana shuru ho raha hai...")

        success_count = 0
        for i in range(1, count + 1):
            current_i = i  # closure ke liye capture

            async def status_update(text: str, _i=current_i):
                try:
                    await msg.edit_text(f"[{_i}/{count}] {text}")
                except Exception:
                    pass

            creds = await create_ig_account(status_cb=status_update)
            if creds:
                success_count += 1
            else:
                await asyncio.sleep(5)

        if os.path.exists("ig_accounts.txt"):
            # FIX: file handle properly close ho
            with open("ig_accounts.txt", "rb") as f:
                await update.message.reply_document(
                    document=f,
                    caption=(
                        f"✅ Task Complete!\n"
                        f"Total {success_count}/{count} accounts ban gaye.\n"
                        f"Saari details file mein saved hain."
                    )
                )
        else:
            await update.message.reply_text("❌ Koi bhi account nahi ban saka.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def post_init(application: Application):
    await filter_live_proxies()
    # Owner ko startup notification
    try:
        live = len(PROXIES)
        await application.bot.send_message(
            chat_id=CHAT_ID,
            text=f"🤖 Bot started!\n✅ Live proxies: {live}"
        )
    except Exception:
        pass


def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("clear",    clear_media_command))
    app.add_handler(CommandHandler("sessions", clear_sessions_command))
    app.add_handler(CommandHandler("create",   create_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photos))

    log.info("🤖 Bot started successfully...")
    app.run_polling()


if __name__ == "__main__":
    main()
