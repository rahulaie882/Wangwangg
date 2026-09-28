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
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from playwright.async_api import async_playwright
from twocaptcha import TwoCaptcha
import httpx
import pyotp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════

BOT_TOKEN = "8948043707:AAGDrCONfkuoydMQjHFPSAeFlouJvTv-AV0"
CHAT_ID = "8963867689"
TWOCAPTCHA_KEY = "6498bcd403bd611438b1fb68568355b1"
FIVESIM_API_KEY = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjIwNTIxMDQsImlhdCI6MTc5MDUxNjEwNCwicmF5IjoiNDMzNjhkNTQ5NGNlM2YzM2UzNTYwMGE1ZGIxOTc0NWUiLCJzdWIiOjQ1NzU0ODh9.csk2R9FNfET5ZhvdjBsOpVX-lYiVTHZCPw7UYFpZcCMUhNtjWJ-BhI2vUXB4F_8kIxU1Xlm6nAg4yraJ5lW5jP9xoZHiT6bu7drW_klEBMZ6pSVak_0RjtyCE5wMXeBqnxbsijd7sYhNz9JVXzHud6Qp7Nbaqr-Xwpqz9ilycM353h8c8G2nxr7Csb8xNSOiy1KXU-5LGfa8mErxHqyRQnVsr7gXpnVlSg4sObdrXbzO17UabirAKga0C3O3_ISUD3lsZLI2QDSaFW2LU_jh5SPg6cuCZpg86_JSxAgleLEth2tdxN0_lryw-NUrGGRGSnbtHwVOM5xUeKqMlBrBrw"

# Residential proxies
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
# 1. DEVICE FINGERPRINTING
# ═══════════════════════════════════════════════════════════════════════════

class DeviceFingerprint:
    """Generate unique mobile device fingerprints"""
    
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
        },
    ]
    
    ANDROID_DEVICES = [
        {
            "model": "Samsung Galaxy S24",
            "os": "Android 14",
            "ua": "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
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
            "ua": "Mozilla/5.0 (Linux; Android 14; OnePlus 12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "resolution": "440x956",
        },
        {
            "model": "Xiaomi 14 Ultra",
            "os": "Android 14",
            "ua": "Mozilla/5.0 (Linux; Android 14; M2304FY11C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "resolution": "480x1028",
        },
    ]
    
    @staticmethod
    def generate():
        """Generate unique device fingerprint"""
        device_type = random.choice(['ios', 'android'])
        
        if device_type == 'ios':
            device = random.choice(DeviceFingerprint.IPHONE_DEVICES)
        else:
            device = random.choice(DeviceFingerprint.ANDROID_DEVICES)
        
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
# 2. PROXY MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class ProxyManager:
    """Intelligent proxy rotation"""
    
    def __init__(self, residential, datacenter):
        self.residential = residential.copy()
        self.datacenter = datacenter.copy()
        self.dead_proxies = set()
        self.last_used = {}
    
    async def validate_proxy(self, proxy_url):
        """Validate proxy"""
        try:
            async with httpx.AsyncClient(
                proxy=proxy_url,
                timeout=7.0,
            ) as client:
                r = await client.get("https://httpbin.org/ip", timeout=7.0)
                return r.status_code == 200
        except Exception:
            return False
    
    async def get_residential_proxy(self):
        """Get residential proxy"""
        available = [p for p in self.residential if p not in self.dead_proxies]
        
        if not available:
            log.warning("No residential proxies, using datacenter")
            return await self.get_datacenter_proxy()
        
        available.sort(key=lambda x: self.last_used.get(x, datetime.min))
        proxy = available[0]
        
        is_valid = await self.validate_proxy(proxy)
        if not is_valid:
            self.dead_proxies.add(proxy)
            return await self.get_residential_proxy()
        
        self.last_used[proxy] = datetime.now()
        return proxy
    
    async def get_datacenter_proxy(self):
        """Get datacenter proxy"""
        available = [p for p in self.datacenter if p not in self.dead_proxies]
        if not available:
            return None
        
        proxy = random.choice(available)
        is_valid = await self.validate_proxy(proxy)
        
        if not is_valid:
            self.dead_proxies.add(proxy)
            return await self.get_datacenter_proxy()
        
        return proxy

proxy_manager = ProxyManager(RESIDENTIAL_PROXIES, DATACENTER_PROXIES)

# ═══════════════════════════════════════════════════════════════════════════
# 3. FIVESIM SMS VERIFICATION (FIXED & UPDATED)
# ═══════════════════════════════════════════════════════════════════════════

class SMSVerification:
    """Handle SMS verification via FiveSim (v1 Path Format Fixed)"""
    
    FIVESIM_API = "https://api.fivesim.net/v1"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            },
            follow_redirects=True
        )
    
    async def get_phone_number(self, country="USA", operator="any"):
        """Get temporary phone number"""
        try:
            url = f"{self.FIVESIM_API}/user/buy/activation/{country.lower()}/{operator}/instagram"
            
            r = await self.client.get(url, timeout=15.0)
            
            if r.status_code == 200:
                try:
                    data = r.json()
                    return {
                        "phone": data.get("phone"),
                        "order_id": data.get("id"),
                        "price": data.get("price"),
                    }
                except Exception as je:
                    log.error(f"JSON Decode Error. Response text: {r.text}")
                    return None
            
            log.error(f"Phone fetch failed: Status {r.status_code} - {r.text}")
            return None
            
        except Exception as e:
            log.error(f"SMS get phone error: {e}")
            return None
    
    async def get_sms_code(self, order_id, timeout=300):
        """Get SMS code from order"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                r = await self.client.get(
                    f"{self.FIVESIM_API}/user/check/{order_id}",
                    timeout=10.0
                )
                
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
                                    return code
                        elif status == "pending":
                            log.debug("Waiting for SMS...")
                        elif status == "timeout":
                            log.error("SMS timeout")
                            return None
                        
                        # Fallback for text parsing
                        sms_text = data.get("text", "")
                        match = re.search(r'\b(\d{6})\b', sms_text)
                        if match:
                            code = match.group(1)
                            log.info(f"✅ SMS code extracted: {code}")
                            return code
                
                await asyncio.sleep(3)
                
            except Exception as e:
                log.debug(f"SMS check error: {e}")
                await asyncio.sleep(3)
        
        log.error("SMS code retrieval timeout")
        return None
    
    async def cancel_order(self, order_id):
        """Cancel order"""
        try:
            await self.client.get(
                f"{self.FIVESIM_API}/user/cancel/{order_id}",
                timeout=10.0
            )
        except Exception as e:
            log.debug(f"Order cancel error: {e}")
    
    async def close(self):
        """Close client"""
        await self.client.aclose()

sms_handler = SMSVerification(FIVESIM_API_KEY) if FIVESIM_API_KEY else None

# ═══════════════════════════════════════════════════════════════════════════
# 4. CAPTCHA SOLVER
# ═══════════════════════════════════════════════════════════════════════════

class CaptchaSolver:
    """2Captcha integration"""
    
    def __init__(self, api_key):
        self.solver = TwoCaptcha(api_key) if api_key else None
        self.solve_count = 0
    
    async def solve_image_captcha(self, image_data):
        """Solve image CAPTCHA"""
        if not self.solver:
            return None
        
        try:
            if isinstance(image_data, str) and image_data.startswith('/'):
                result = self.solver.normal(open(image_data, 'rb'))
            else:
                result = self.solver.normal(image_data)
            
            self.solve_count += 1
            return result.get('code')
        except Exception as e:
            log.error(f"Image CAPTCHA failed: {e}")
            return None
    
    async def solve_recaptcha_v2(self, sitekey, page_url):
        """Solve reCAPTCHA v2"""
        if not self.solver:
            return None
        
        try:
            result = self.solver.recaptcha(sitekey=sitekey, pageurl=page_url)
            self.solve_count += 1
            return result.get('code')
        except Exception as e:
            log.error(f"reCAPTCHA v2 failed: {e}")
            return None
    
    async def solve_hcaptcha(self, sitekey, page_url):
        """Solve hCaptcha"""
        if not self.solver:
            return None
        
        try:
            result = self.solver.hcaptcha(sitekey=sitekey, pageurl=page_url)
            self.solve_count += 1
            return result.get('code')
        except Exception as e:
            log.error(f"hCaptcha failed: {e}")
            return None

captcha_solver = CaptchaSolver(TWOCAPTCHA_KEY)

# ═══════════════════════════════════════════════════════════════════════════
# 5. STEALTH JAVASCRIPT
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
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                const arr = [1, 2, 3, 4, 5];
                arr.item = i => arr[i];
                arr.namedItem = n => null;
                arr.refresh = () => {};
                return arr;
            }
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {
            if (param === 37445) return 'Intel Inc.';
            if (param === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter.call(this, param);
        };
        
        const origQuery = navigator.permissions.query;
        navigator.permissions.query = params =>
            params.name === 'notifications'
                ? Promise.resolve({state: Notification.permission})
                : origQuery(params);
        
        Object.defineProperty(window, 'outerHeight', {get: () => 1084});
        Object.defineProperty(window, 'outerWidth', {get: () => 1920});
    })();
"""

# ═══════════════════════════════════════════════════════════════════════════
# 6. BROWSER AUTOMATION
# ═══════════════════════════════════════════════════════════════════════════

async def human_delay(min_sec=0.5, max_sec=2.0):
    """Human-like delay"""
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)

async def create_stealth_context(device_fp, proxy_url):
    """Create stealth browser context"""
    try:
        playwright = await async_playwright().start()
        
        browser = await playwright.chromium.launch(
            headless=random.choice([True, False]),
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-gpu",
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
        
        return browser, context
        
    except Exception as e:
        log.error(f"Context creation failed: {e}")
        return None, None

# ═══════════════════════════════════════════════════════════════════════════
# 7. INSTAGRAM ACCOUNT CREATION (SMS ONLY)
# ═══════════════════════════════════════════════════════════════════════════

async def create_instagram_account(device_fp, proxy_url, status_cb=None, max_retries=3):
    """Create Instagram account with SMS verification only"""
    
    browser = None
    order_id = None
    
    for attempt in range(1, max_retries + 1):
        try:
            if status_cb:
                await status_cb(f"🚀 Attempt {attempt}/{max_retries}")
            
            # Get phone number
            if status_cb:
                await status_cb("📱 Getting phone number...")
            
            phone_data = await sms_handler.get_phone_number(country="USA")
            if not phone_data:
                raise Exception("Failed to get phone number")
            
            phone = phone_data['phone']
            order_id = phone_data['order_id']
            
            if status_cb:
                await status_cb(f"📞 Phone: {phone}")
            
            # Create browser
            browser, context = await create_stealth_context(device_fp, proxy_url)
            if not browser or not context:
                raise Exception("Browser creation failed")
            
            page = await context.new_page()
            
            # Generate credentials
            username = f"user{hashlib.md5(str(random.random()).encode()).hexdigest()[:8]}"
            password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^", k=18))
            first_name = ''.join(random.choices(string.ascii_uppercase, k=1)) + \
                        ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 7)))
            last_name = ''.join(random.choices(string.ascii_uppercase, k=1)) + \
                       ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 7)))
            
            dob = (datetime.now() - timedelta(days=random.randint(18*365, 50*365))).strftime("%Y-%m-%d")
            
            if status_cb:
                await status_cb(f"🌍 Opening Instagram...")
            
            # Navigate
            await page.goto("https://www.instagram.com/accounts/emailsignup/", wait_until="networkidle")
            await human_delay(2, 4)
            
            # Close popups
            try:
                close_btn = await page.query_selector('svg[aria-label="Close"]')
                if close_btn:
                    await close_btn.click()
                    await human_delay(1, 2)
            except:
                pass
            
            # ─── Phone signup option ───
            if status_cb:
                await status_cb("📱 Switching to phone signup...")
            
            try:
                phone_link = await page.query_selector('button:has-text("phone")')
                if phone_link:
                    await phone_link.click()
                    await human_delay(2, 3)
            except:
                pass
            
            # ─── Fill phone ───
            if status_cb:
                await status_cb(f"☎️ Filling phone number...")
            
            phone_field = await page.query_selector('input[type="tel"]') or \
                         await page.query_selector('input[name*="phone"]')
            
            if phone_field:
                await phone_field.click()
                await human_delay(0.5, 1.5)
                for char in phone:
                    await phone_field.type(char)
                    await human_delay(0.05, 0.15)
            
            await human_delay(1.5, 2.5)
            
            # ─── Fill full name ───
            if status_cb:
                await status_cb("👤 Filling name...")
            
            name_field = await page.query_selector('input[name="fullName"]')
            if name_field:
                await name_field.click()
                await human_delay(0.5, 1.5)
                full_name = f"{first_name} {last_name}"
                for char in full_name:
                    await name_field.type(char)
                    await human_delay(0.05, 0.15)
            
            await human_delay(1.5, 2.5)
            
            # ─── Fill username ───
            if status_cb:
                await status_cb(f"🔤 Username: {username}")
            
            username_field = await page.query_selector('input[name="username"]')
            if username_field:
                await username_field.click()
                await human_delay(0.5, 1.5)
                for char in username:
                    await username_field.type(char)
                    await human_delay(0.05, 0.15)
            
            await human_delay(1.5, 2.5)
            
            # ─── Fill password ───
            if status_cb:
                await status_cb("🔐 Setting password...")
            
            password_field = await page.query_selector('input[name="password"]')
            if password_field:
                await password_field.click()
                await human_delay(0.5, 1.5)
                for char in password:
                    await password_field.type(char)
                    await human_delay(0.05, 0.15)
            
            await human_delay(2, 3)
            
            # ─── Click Next ───
            if status_cb:
                await status_cb("➡️ Clicking next...")
            
            next_btn = await page.query_selector('button:has-text("Next")')
            if next_btn:
                await next_btn.click()
                await human_delay(3, 5)
            
            # ─── Handle CAPTCHA ───
            try:
                captcha_frame = await page.query_selector('iframe[title*="hCaptcha"]') or \
                               await page.query_selector('iframe[src*="hcaptcha"]')
                
                if captcha_frame:
                    if status_cb:
                        await status_cb("🔐 Solving CAPTCHA...")
                    
                    sitekey = await page.evaluate(
                        "document.querySelector('iframe[src*=\"hcaptcha\"]')?.src?.split('&')[0]?.split('=')[1] || ''",
                        force_expr=True
                    )
                    
                    if sitekey:
                        solution = await captcha_solver.solve_hcaptcha(sitekey, page.url)
                        if solution:
                            await page.evaluate(f"""
                                document.getElementById('h-captcha-response').innerText = '{solution}';
                            """)
                            await human_delay(2, 3)
            except Exception as e:
                log.debug(f"CAPTCHA: {e}")
            
            # ─── Date of birth ───
            if status_cb:
                await status_cb("📅 Setting DOB...")
            
            try:
                dob_parts = dob.split('-')
                
                month_select = await page.query_selector('select[name*="month"]')
                if month_select:
                    await month_select.select_option(dob_parts[1])
                    await human_delay(0.5, 1.5)
                
                day_select = await page.query_selector('select[name*="day"]')
                if day_select:
                    await day_select.select_option(dob_parts[2])
                    await human_delay(0.5, 1.5)
                
                year_select = await page.query_selector('select[name*="year"]')
                if year_select:
                    await year_select.select_option(dob_parts[0])
                    await human_delay(1, 2)
            except Exception as e:
                log.debug(f"DOB: {e}")
            
            # ─── Confirm DOB ───
            if status_cb:
                await status_cb("✅ Confirming...")
            
            confirm_btn = await page.query_selector('button:has-text("Next")')
            if confirm_btn:
                await confirm_btn.click()
                await human_delay(3, 5)
            
            # ─── SMS verification ───
            if status_cb:
                await status_cb(f"📱 Waiting for SMS on {phone}...")
            
            try:
                code_input = await page.wait_for_selector(
                    'input[type="text"]',
                    timeout=120000
                )
                
                if status_cb:
                    await status_cb("📨 Retrieving SMS code...")
                
                sms_code = await sms_handler.get_sms_code(order_id, timeout=120)
                
                if sms_code:
                    await code_input.fill(sms_code)
                    await human_delay(1, 2)
                    await code_input.press("Enter")
                    await human_delay(3, 5)
                    
                    if status_cb:
                        await status_cb("✅ SMS verified!")
                else:
                    raise Exception("SMS code not received")
            
            except Exception as e:
                log.error(f"SMS verification failed: {e}")
                if status_cb:
                    await status_cb(f"❌ SMS verification failed")
                raise
            
            # ─── Save session ───
            if status_cb:
                await status_cb("💾 Saving session...")
            
            session_file = f"/tmp/ig_{username}_{int(time.time())}.json"
            try:
                await context.storage_state(path=session_file)
            except:
                pass
            
            # ─── SUCCESS ───
            credentials = {
                "username": username,
                "phone": phone,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "dob": dob,
                "device": device_fp['model'],
                "proxy": proxy_url,
                "status": "success",
                "created_at": datetime.now().isoformat(),
                "session_file": session_file,
            }
            
            if status_cb:
                await status_cb(f"✅ Account created!")
            
            log.info(f"✅ Account created: {username}")
            return credentials
            
        except Exception as e:
            log.error(f"❌ Attempt {attempt} failed: {e}")
            if status_cb:
                await status_cb(f"❌ Error: {str(e)[:50]}")
            
            if order_id:
                await sms_handler.cancel_order(order_id)
            
            if attempt < max_retries:
                await asyncio.sleep(random.uniform(10, 20))
        
        finally:
            if browser:
                try:
                    await browser.close()
                except:
                    pass
    
    return None

# ═══════════════════════════════════════════════════════════════════════════
# TELEGRAM BOT
# ═══════════════════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "🤖 *Instagram Account Creator - SMS Only*\n\n"
        "✅ *Features:*\n"
        "• 🎭 Device Fingerprinting\n"
        "• 🌍 Residential Proxy Rotation\n"
        "• 📱 SMS Verification (FiveSim)\n"
        "• 🔐 CAPTCHA Solving\n"
        "• 🛡️ Anti-Detection Stealth\n"
        "• ⏱️ Human-like Delays\n\n"
        "📝 *Usage:*\n"
        "`/create 5` — Create 5 accounts\n"
        "`/status` — Check bot status\n\n"
        "⚡ *Ready to go!*",
        parse_mode="Markdown"
    )

async def create_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Create accounts"""
    
    if not sms_handler:
        await update.message.reply_text("❌ FiveSim API not configured")
        return
    
    try:
        count = int(ctx.args[0]) if ctx.args else 1
        
        if count < 1 or count > 50:
            await update.message.reply_text("⚠️ Enter 1-50")
            return
        
        msg = await update.message.reply_text(f"🚀 Creating {count} accounts...\n\n⏳ Starting...")
        
        accounts_created = []
        failed = 0
        
        for i in range(1, count + 1):
            device_fp = DeviceFingerprint.generate()
            proxy = await proxy_manager.get_residential_proxy()
            if not proxy:
                proxy = await proxy_manager.get_datacenter_proxy()
            
            async def update_status(text):
                try:
                    await msg.edit_text(
                        f"[{i}/{count}] {text}\n\n"
                        f"✅ Created: {len(accounts_created)}\n"
                        f"❌ Failed: {failed}"
                    )
                except:
                    pass
            
            creds = await create_instagram_account(
                device_fp,
                proxy,
                status_cb=update_status,
                max_retries=2
            )
            
            if creds:
                accounts_created.append(creds)
                await asyncio.sleep(random.uniform(45, 90))
            else:
                failed += 1
                await asyncio.sleep(30)
        
        export_data = {
            "total": count,
            "created": len(accounts_created),
            "failed": failed,
            "timestamp": datetime.now().isoformat(),
            "accounts": accounts_created
        }
        
        export_file = f"ig_accounts_{int(time.time())}.json"
        with open(export_file, "w") as f:
            json.dump(export_data, f, indent=2)
        
        with open(export_file, "rb") as f:
            await update.message.reply_document(
                document=f,
                caption=(
                    f"✅ *Complete!*\n\n"
                    f"📊 Created: `{len(accounts_created)}/{count}`\n"
                    f"❌ Failed: `{failed}`\n"
                    f"📱 Devices: `{len(set(c['device'] for c in accounts_created))}`"
                ),
                parse_mode="Markdown"
            )
        
        os.remove(export_file)
        
    except ValueError:
        await update.message.reply_text("Usage: `/create <number>`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def status_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Status"""
    await update.message.reply_text(
        f"🤖 *Bot Status*\n\n"
        f"✅ Residential Proxies: `{len([p for p in proxy_manager.residential if p not in proxy_manager.dead_proxies])}`\n"
        f"⚠️ Dead: `{len(proxy_manager.dead_proxies)}`\n"
        f"🔐 CAPTCHA Solved: `{captcha_solver.solve_count}`\n"
        f"⏱️ Time: `{datetime.now().strftime('%H:%M:%S')}`",
        parse_mode="Markdown"
    )

def main():
    """Start"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create_command))
    app.add_handler(CommandHandler("status", status_command))
    
    log.info("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
