import asyncio
import random
import string
import hashlib
import json
import os
import re
import time
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters
)
from playwright.async_api import async_playwright
from twocaptcha import TwoCaptcha
import httpx

# ═══════════════════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_execution.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION & SECRETS
# ═══════════════════════════════════════════════════════════════════════════

BOT_TOKEN = "8948043707:AAGDrCONfkuoydMQjHFPSAeFlouJvTv-AV0"
CHAT_ID = "8963867689"
TWOCAPTCHA_KEY = "6498bcd403bd611438b1fb68568355b1"
FIVESIM_API_KEY = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjIwNTIxMDQsImlhdCI6MTc5MDUxNjEwNCwicmF5IjoiNDMzNjhkNTQ5NGNlM2YzM2UzNTYwMGE1ZGIxOTc0NWUiLCJzdWIiOjQ1NzU0ODh9.csk2R9FNfET5ZhvdjBsOpVX-lYiVTHZCPw7UYFpZcCMUhNtjWJ-BhI2vUXB4F_8kIxU1Xlm6nAg4yraJ5lW5jP9xoZHiT6bu7drW_klEBMZ6pSVak_0RjtyCE5wMXeBqnxbsijd7sYhNz9JVXzHud6Qp7Nbaqr-Xwpqz9ilycM353h8c8G2nxr7Csb8xNSOiy1KXU-5LGfa8mErxHqyRQnVsr7gXpnVlSg4sObdrXbzO17UabirAKga0C3O3_ISUD3lsZLI2QDSaFW2LU_jh5SPg6cuCZpg86_JSxAgleLEth2tdxN0_lryw-NUrGGRGSnbtHwVOM5xUeKqMlBrBrw"

RESIDENTIAL_PROXIES = [
    "http://user:pass@res-proxy-1.com:8080",
    "http://user:pass@res-proxy-2.com:8080",
    "http://user:pass@res-proxy-3.com:8080",
]

DATACENTER_PROXIES = [
    "http://user:pass@dc-proxy-1.com:3128",
    "http://user:pass@dc-proxy-2.com:3128",
]

# ═══════════════════════════════════════════════════════════════════════════
# 1. ADVANCED DEVICE FINGERPRINTING ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class DeviceFingerprint:
    """Generate high-entropy unique mobile device fingerprints to evade anti-bot detection"""
    
    IPHONE_DEVICES = [
        {
            "model": "iPhone 15 Pro",
            "os": "iOS 17.4.1",
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
            "resolution": "390x844",
        },
        {
            "model": "iPhone 14",
            "os": "iOS 16.7.8",
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "resolution": "390x844",
        },
        {
            "model": "iPhone 13 Pro Max",
            "os": "iOS 17.2",
            "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "resolution": "428x926",
        }
    ]
    
    ANDROID_DEVICES = [
        {
            "model": "Samsung Galaxy S24 Ultra",
            "os": "Android 14",
            "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "resolution": "412x915",
        },
        {
            "model": "Google Pixel 8 Pro",
            "os": "Android 14",
            "ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "resolution": "480x1084",
        },
        {
            "model": "OnePlus 12",
            "os": "Android 14",
            "ua": "Mozilla/5.0 (Linux; Android 14; CPH2581) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "resolution": "412x932",
        }
    ]
    
    @staticmethod
    def generate():
        device_type = random.choice(['ios', 'android'])
        device = random.choice(DeviceFingerprint.IPHONE_DEVICES if device_type == 'ios' else DeviceFingerprint.ANDROID_DEVICES)
        
        idfa = hashlib.md5(str(random.random()).encode()).hexdigest()
        android_id = hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]
        
        return {
            "device_type": device_type,
            "model": device["model"],
            "os": device["os"],
            "user_agent": device["ua"],
            "screen_resolution": device["resolution"],
            "idfa": idfa,
            "android_id": android_id,
            "timezone": random.choice(["UTC", "IST", "EST", "PST", "GMT+5:30"]),
            "language": "en_US",
            "locale": random.choice(["en_US", "en_GB", "en_IN"]),
            "screen_density": random.choice([2, 2.5, 3]),
        }

# ═══════════════════════════════════════════════════════════════════════════
# 2. INTELLIGENT PROXY MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class ProxyManager:
    """Manages pool rotation, dead proxy blacklisting, and health checks"""
    
    def __init__(self, residential, datacenter):
        self.residential = residential.copy()
        self.datacenter = datacenter.copy()
        self.dead_proxies = set()
        self.last_used = {}
    
    async def validate_proxy(self, proxy_url):
        try:
            async with httpx.AsyncClient(proxy=proxy_url, timeout=7.0) as client:
                r = await client.get("https://httpbin.org/ip", timeout=7.0)
                return r.status_code == 200
        except Exception:
            return False
    
    async def get_residential_proxy(self):
        available = [p for p in self.residential if p not in self.dead_proxies]
        if not available:
            log.warning("No residential proxies available, falling back to datacenter")
            return await self.get_datacenter_proxy()
        
        available.sort(key=lambda x: self.last_used.get(x, datetime.min))
        proxy = available[0]
        
        if not await self.validate_proxy(proxy):
            self.dead_proxies.add(proxy)
            return await self.get_residential_proxy()
        
        self.last_used[proxy] = datetime.now()
        return proxy
    
    async def get_datacenter_proxy(self):
        available = [p for p in self.datacenter if p not in self.dead_proxies]
        if not available:
            return None
        
        proxy = random.choice(available)
        if not await self.validate_proxy(proxy):
            self.dead_proxies.add(proxy)
            return await self.get_datacenter_proxy()
        
        return proxy

proxy_manager = ProxyManager(RESIDENTIAL_PROXIES, DATACENTER_PROXIES)

# ═══════════════════════════════════════════════════════════════════════════
# 3. FIVESIM SMS VERIFICATION (PLAYWRIGHT API REQUEST BYPASS)
# ═══════════════════════════════════════════════════════════════════════════

class SMSVerification:
    """Handle SMS verification via FiveSim using Playwright session request context"""
    
    FIVESIM_API = "https://5sim.net/v1"
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    async def get_phone_number(self, country="usa", operator="any"):
        playwright = None
        browser = None
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            log.info("Bypassing Cloudflare on FiveSim...")
            await page.goto("https://5sim.net", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)
            
            url = f"{self.FIVESIM_API}/user/buy/activation/{country.lower()}/{operator}/instagram"
            log.info("Fetching phone number from FiveSim via Playwright API request context...")
            
            response = await page.request.get(
                url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                }
            )
            
            status = response.status
            body = await response.text()
            
            if status == 200:
                try:
                    data = json.loads(body)
                    if "phone" in data:
                        log.info(f"✅ Phone fetched: {data.get('phone')}")
                        return {
                            "phone": data.get("phone"),
                            "order_id": data.get("id"),
                            "price": data.get("price"),
                        }
                    else:
                        log.error(f"FiveSim JSON missing phone: {body}")
                except Exception as json_err:
                    log.error(f"JSON parse error: {json_err} | Body: {body}")
            else:
                log.error(f"FiveSim API status {status}: {body}")
            
            return None
            
        except Exception as e:
            log.error(f"SMS get phone error: {e}")
            return None
        finally:
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()
    
    async def get_sms_code(self, order_id, timeout=300):
        start_time = time.time()
        client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            },
            follow_redirects=True
        )
        
        while time.time() - start_time < timeout:
            try:
                r = await client.get(f"{self.FIVESIM_API}/user/check/{order_id}", timeout=10.0)
                if r.status_code == 200:
                    try:
                        data = r.json()
                    except Exception:
                        await asyncio.sleep(3)
                        continue
                    
                    if isinstance(data, dict):
                        status = data.get("status")
                        if status == "received":
                            sms_list = data.get("sms", [])
                            if sms_list:
                                sms_text = sms_list[0].get("text", "")
                                match = re.search(r'\b(\d{6})\b', sms_text)
                                if match:
                                    code = match.group(1)
                                    log.info(f"✅ SMS code extracted: {code}")
                                    await client.aclose()
                                    return code
                        elif status == "timeout":
                            log.error("SMS timeout on FiveSim")
                            await client.aclose()
                            return None
                await asyncio.sleep(3)
            except Exception as e:
                log.debug(f"SMS check error: {e}")
                await asyncio.sleep(3)
        
        await client.aclose()
        return None
    
    async def cancel_order(self, order_id):
        try:
            async with httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self.api_key}"},
                follow_redirects=True
            ) as client:
                await client.get(f"{self.FIVESIM_API}/user/cancel/{order_id}", timeout=10.0)
        except Exception as e:
            log.debug(f"Order cancel error: {e}")

sms_handler = SMSVerification(FIVESIM_API_KEY) if FIVESIM_API_KEY else None

# ═══════════════════════════════════════════════════════════════════════════
# 4. CAPTCHA SOLVER MODULE
# ═══════════════════════════════════════════════════════════════════════════

class CaptchaSolver:
    """Robust 2Captcha integration for hCaptcha/Recaptcha challenges"""
    
    def __init__(self, api_key):
        self.solver = TwoCaptcha(api_key) if api_key else None
        self.solve_count = 0
    
    async def solve_hcaptcha(self, sitekey, page_url):
        if not self.solver:
            return None
        try:
            result = self.solver.hcaptcha(sitekey=sitekey, pageurl=page_url)
            self.solve_count += 1
            return result.get('code')
        except Exception as e:
            log.error(f"hCaptcha solver failed: {e}")
            return None

captcha_solver = CaptchaSolver(TWOCAPTCHA_KEY)

# ═══════════════════════════════════════════════════════════════════════════
# 5. STEALTH BROWSER AUTOMATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

STEALTH_JS = """
    (() => {
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.__playwright;
        delete window.__pwInitScripts;
        
        if (!window.chrome) {
            window.chrome = {
                app: {isInstalled: false},
                runtime: {},
                loadTimes: () => ({}),
                csi: () => ({})
            };
        }
    })();
"""

async def human_delay(min_sec=0.8, max_sec=2.2):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def create_stealth_context(device_fp, proxy_url):
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage"
            ]
        )
        
        proxy_config = None
        if proxy_url:
            try:
                parsed = urlparse(proxy_url)
                proxy_config = {
                    "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port or 80}",
                    "username": parsed.username,
                    "password": parsed.password,
                }
            except:
                pass
        
        width, height = map(int, device_fp['screen_resolution'].split('x'))
        context = await browser.new_context(
            user_agent=device_fp['user_agent'],
            viewport={"width": width, "height": height},
            locale=device_fp['locale'],
            timezone_id=device_fp['timezone'],
            proxy=proxy_config,
            device_scale_factor=device_fp['screen_density'],
            has_touch=True,
            is_mobile=True,
        )
        await context.add_init_script(STEALTH_JS)
        return playwright, browser, context
    except Exception as e:
        log.error(f"Stealth context creation failed: {e}")
        return None, None, None

# ═══════════════════════════════════════════════════════════════════════════
# 6. INSTAGRAM AUTOMATED REGISTRATION WORKFLOW (ULTIMATE FALLBACK FIX)
# ═══════════════════════════════════════════════════════════════════════════

async def create_instagram_account(device_fp, proxy_url, status_cb=None, max_retries=3):
    playwright, browser, context, page, order_id = None, None, None, None, None
    
    for attempt in range(1, max_retries + 1):
        try:
            if status_cb:
                await status_cb(f"🚀 Registration Attempt {attempt}/{max_retries}")
                await status_cb("📱 Acquiring fresh phone number via FiveSim...")
            
            phone_data = await sms_handler.get_phone_number(country="usa")
            if not phone_data:
                raise Exception("Failed to secure phone number")
            
            phone = phone_data['phone']
            order_id = phone_data['order_id']
            
            playwright, browser, context = await create_stealth_context(device_fp, proxy_url)
            if not browser or not context:
                raise Exception("Browser initialization failed")
            
            page = await context.new_page()
            
            username = f"user_{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}"
            password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=18))
            first_name = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=6))
            last_name = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=6))
            dob_year = random.randint(1994, 2004)
            dob_month = random.randint(1, 12)
            dob_day = random.randint(1, 28)
            
            if status_cb:
                await status_cb("🌍 Navigating to Instagram signup portal...")
            
            await page.goto("https://www.instagram.com/accounts/emailsignup/", wait_until="networkidle", timeout=45000)
            await human_delay(3, 5)
            
            # 1. Handle Cookie consent / Dialogs if any
            try:
                for btn_text in ["Accept", "Allow all cookies", "Allow", "Only allow essential cookies"]:
                    btn = await page.query_selector(f'button:has-text("{btn_text}")')
                    if btn:
                        await btn.click()
                        await human_delay(1, 2)
                        break
            except:
                pass

            # 2. Check if Instagram asks for Birthday FIRST
            try:
                month_select = await page.query_selector('select[name*="month"]')
                if month_select:
                    log.info("ℹ️ Birthday selection appeared first, filling DOB...")
                    await page.select_option('select[name*="month"]', str(dob_month))
                    await page.select_option('select[name*="day"]', str(dob_day))
                    await page.select_option('select[name*="year"]', str(dob_year))
                    await human_delay(1, 2)
                    
                    next_btn = await page.query_selector('button:has-text("Next"), button[type="submit"]')
                    if next_btn:
                        await next_btn.click()
                        await human_delay(3, 5)
            except Exception as e:
                log.debug(f"DOB step skipped or not first: {e}")

            # 3. Switch to Phone Mode tab if required
            try:
                phone_toggle = await page.query_selector('button:has-text("phone"), button:has-text("Phone"), span:has-text("phone")')
                if phone_toggle:
                    await phone_toggle.click()
                    await human_delay(1, 2)
            except:
                pass
            
            # 4. Robust Phone Number / Email Field Fill with expanded fallback selectors
            if status_cb:
                await status_cb("📱 Entering phone number...")

            phone_field = None
            selectors = [
                'input[name="mobileOrEmail"]',
                'input[name="emailOrPhone"]',
                'input[name="phoneOrEmail"]',
                'input[type="tel"]',
                'input[name*="phone"]',
                'input[name*="email"]',
                'input[aria-label*="Mobile"]',
                'input[aria-label*="Phone"]',
                'input[aria-label*="Email"]',
                'input[data-testid*="phone"]',
                'input[data-testid*="email"]',
                'form input[type="text"]'
            ]
            
            for sel in selectors:
                try:
                    phone_field = await page.wait_for_selector(sel, timeout=4000)
                    if phone_field:
                        log.info(f"✅ Found phone/email field using selector: {sel}")
                        break
                except:
                    continue
            
            if not phone_field:
                raise Exception("Phone/Email input field not found on page! Instagram layout changed or blocked.")
                
            await phone_field.click()
            for char in phone:
                await phone_field.type(char)
                await human_delay(0.05, 0.15)
            
            # 5. Click Next after entering phone
            next_btn = await page.query_selector('button[type="submit"], button:has-text("Next"), button:has-text("Sign up")')
            if next_btn:
                await next_btn.click()
                await human_delay(3, 5)

            # 6. Fill Credentials securely on the next step
            if status_cb:
                await status_cb("📝 Filling account credentials...")

            await page.wait_for_selector('input[name="fullName"], input[name*="Name"]', timeout=15000)

            await page.fill('input[name="fullName"], input[name*="Name"]', f"{first_name} {last_name}")
            await human_delay(0.5, 1.0)
            
            await page.fill('input[name="username"], input[name*="username"]', username)
            await human_delay(0.5, 1.0)
            
            await page.fill('input[name="password"], input[name*="password"]', password)
            await human_delay(0.5, 1.0)
            
            # Submit credentials
            submit_btn = await page.query_selector('button[type="submit"]:has-text("Sign up"), button[type="submit"]:has-text("Next")')
            if submit_btn:
                await submit_btn.click()
                await human_delay(4, 7)
            
            # DOB Selection (if not already handled)
            try:
                month_sel = await page.query_selector('select[name*="month"]')
                if month_sel:
                    await page.select_option('select[name*="month"]', str(dob_month))
                    await page.select_option('select[name*="day"]', str(dob_day))
                    await page.select_option('select[name*="year"]', str(dob_year))
                    await human_delay(1, 2)
                    
                    confirm_dob = await page.query_selector('button:has-text("Next"), button[type="submit"]')
                    if confirm_dob:
                        await confirm_dob.click()
                        await human_delay(3, 5)
            except Exception as dob_err:
                log.debug(f"DOB selection skipped/failed: {dob_err}")
            
            # Handle SMS Verification Code Input
            if status_cb:
                await status_cb("📱 Awaiting SMS verification code...")
            
            code_input = await page.wait_for_selector('input[name="confirmationCode"], input[type="text"]', timeout=120000)
            sms_code = await sms_handler.get_sms_code(order_id, timeout=120)
            
            if sms_code:
                await code_input.fill(sms_code)
                await code_input.press("Enter")
                await human_delay(4, 6)
                if status_cb:
                    await status_cb("✅ Verification code accepted!")
            else:
                raise Exception("SMS code verification timeout")
            
            # Export session state cookies
            session_file = f"/tmp/ig_{username}_{int(time.time())}.json"
            try:
                await context.storage_state(path=session_file)
            except:
                pass
            
            return {
                "username": username,
                "password": password,
                "phone": phone,
                "device": device_fp['model'],
                "proxy": proxy_url,
                "status": "success",
                "created_at": datetime.now().isoformat(),
            }
            
        except Exception as e:
            log.error(f"❌ Attempt {attempt} failed: {e}")
            if page:
                try:
                    os.makedirs("debug_screenshots", exist_ok=True)
                    await page.screenshot(path=f"debug_screenshots/error_att_{attempt}_{int(time.time())}.png")
                except:
                    pass
            if order_id:
                await sms_handler.cancel_order(order_id)
            if attempt < max_retries:
                await asyncio.sleep(15)
        finally:
            if browser:
                try: await browser.close()
                except: pass
            if playwright:
                try: await playwright.stop()
                except: pass
    return None

# ═══════════════════════════════════════════════════════════════════════════
# TELEGRAM BOT HANDLERS & COMMANDS
# ═══════════════════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Create Accounts", callback_data="menu_create")],
        [InlineKeyboardButton("📊 Bot Status", callback_data="menu_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 *Instagram Automation & Account Creator Bot*\n\n"
        "⚡ Fully equipped with Cloudflare bypass & mobile fingerprinting.\n"
        "Use the inline buttons or commands below:\n\n"
        "📝 `/create [count]` - Start batch creation\n"
        "📈 `/status` - View health and statistics",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def create_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not sms_handler:
        await update.message.reply_text("❌ FiveSim API key is missing or invalid.")
        return
    
    try:
        count = int(ctx.args[0]) if ctx.args else 1
        if count > 20:
            await update.message.reply_text("⚠️ Max 20 accounts per batch to prevent rate limits.")
            count = 20
        
        msg = await update.message.reply_text(f"🚀 Initializing batch creation for {count} accounts...")
        
        created_accounts = []
        failed_count = 0
        
        for i in range(1, count + 1):
            device_fp = DeviceFingerprint.generate()
            proxy = await proxy_manager.get_residential_proxy() or await proxy_manager.get_datacenter_proxy()
            
            async def update_status_text(text):
                try:
                    await msg.edit_text(
                        f"🔄 **Batch Progress [{i}/{count}]**\n\n"
                        f"{text}\n\n"
                        f"✅ Success: `{len(created_accounts)}` | ❌ Failed: `{failed_count}`",
                        parse_mode="Markdown"
                    )
                except:
                    pass
            
            account_data = await create_instagram_account(device_fp, proxy, status_cb=update_status_text, max_retries=2)
            if account_data:
                created_accounts.append(account_data)
                await asyncio.sleep(random.uniform(30, 60))
            else:
                failed_count += 1
                await asyncio.sleep(20)
        
        # Save results to JSON file
        export_filename = f"instagram_accounts_{int(time.time())}.json"
        with open(export_filename, "w", encoding="utf-8") as f:
            json.dump({
                "total_requested": count,
                "successful": len(created_accounts),
                "failed": failed_count,
                "accounts": created_accounts
            }, f, indent=2)
        
        with open(export_filename, "rb") as f:
            await update.message.reply_document(
                document=f,
                caption=f"✅ *Batch Processing Complete!*\n\n📊 Total Created: `{len(created_accounts)}/{count}`",
                parse_mode="Markdown"
            )
        
        if os.path.exists(export_filename):
            os.remove(export_filename)
            
    except Exception as e:
        log.error(f"Create command error: {e}")
        await update.message.reply_text(f"❌ Execution error: {e}")

async def status_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 *System Status Report*\n\n"
        f"🛡️ Active Residential Proxies: `{len(RESIDENTIAL_PROXIES)}`\n"
        f"💀 Blacklisted Dead Proxies: `{len(proxy_manager.dead_proxies)}`\n"
        f"🔐 Total Captchas Solved: `{captcha_solver.solve_count}`\n"
        f"📱 SMS Provider: `FiveSim (Active)`",
        parse_mode="Markdown"
    )

async def button_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_status":
        await query.message.reply_text(
            f"📊 *Quick Status*\nDead Proxies: `{len(proxy_manager.dead_proxies)}` | Captchas Solved: `{captcha_solver.solve_count}`",
            parse_mode="Markdown"
        )
    elif query.data == "menu_create":
        await query.message.reply_text("💡 Send `/create 3` to start creating 3 accounts automatically.")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    log.info("🤖 Telegram Bot running with full production modules...")
    app.run_polling()

if __name__ == "__main__":
    main()
