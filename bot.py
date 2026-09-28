import time
import random
import string
import hashlib
import json
import os
import re
import logging
import asyncio
import concurrent.futures
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import httpx
from twocaptcha import TwoCaptcha

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
    "us6.cactussstp.com:3129:uncpjndo:w77Ebc0h2A",
    "hk1.cactussstp.com:8080:uncpjndo:w77Ebc0h2A",
    "it1.cactussstp.com:3129:bvmbsmie:shibby2511",
    "uk3.cactussstp.com:3129:uncpjndo:w77Ebc0h2A",
]

DATACENTER_PROXIES = [
    "px022409.pointtoserver.com:10780:purevpn0s551451:9dpdlc2nfxgj",
    "in-ban.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2",
]

# ═══════════════════════════════════════════════════════════════════════════
# 1. ADVANCED DEVICE FINGERPRINTING ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class DeviceFingerprint:
    IPHONE_DEVICES = [
        {"model": "iPhone 15 Pro", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1", "resolution": "390x844"},
        {"model": "iPhone 14", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1", "resolution": "390x844"},
    ]
    ANDROID_DEVICES = [
        {"model": "Samsung Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36", "resolution": "412x915"},
        {"model": "Google Pixel 8 Pro", "ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36", "resolution": "480x1084"},
    ]
    
    @staticmethod
    def generate():
        device_type = random.choice(['ios', 'android'])
        device = random.choice(DeviceFingerprint.IPHONE_DEVICES if device_type == 'ios' else DeviceFingerprint.ANDROID_DEVICES)
        return {
            "model": device["model"],
            "user_agent": device["ua"],
            "screen_resolution": device["resolution"]
        }

# ═══════════════════════════════════════════════════════════════════════════
# 2. INTELLIGENT PROXY MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class ProxyManager:
    def __init__(self, residential, datacenter):
        self.residential = residential.copy()
        self.datacenter = datacenter.copy()
        self.dead_proxies = set()
    
    def get_proxy(self):
        available = [p for p in self.residential if p not in self.dead_proxies]
        if not available:
            available = [p for p in self.datacenter if p not in self.dead_proxies]
        if not available:
            return None
        return random.choice(available)

proxy_manager = ProxyManager(RESIDENTIAL_PROXIES, DATACENTER_PROXIES)

# ═══════════════════════════════════════════════════════════════════════════
# 3. FIVESIM SMS VERIFICATION MODULE
# ═══════════════════════════════════════════════════════════════════════════

class SMSVerification:
    FIVESIM_API = "https://5sim.net/v1"
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    async def get_phone_number(self, country="usa"):
        url = f"{self.FIVESIM_API}/user/buy/activation/{country}/any/instagram"
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(url, headers=headers, timeout=15.0)
                if r.status_code == 200:
                    data = r.json()
                    return {"phone": data.get("phone"), "order_id": data.get("id")}
            except Exception as e:
                log.error(f"FiveSim Error: {e}")
        return None
    
    async def get_sms_code(self, order_id, timeout=180):
        url = f"{self.FIVESIM_API}/user/check/{order_id}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        start_time = time.time()
        async with httpx.AsyncClient() as client:
            while time.time() - start_time < timeout:
                try:
                    r = await client.get(url, headers=headers, timeout=10.0)
                    if r.status_code == 200:
                        data = r.json()
                        if data.get("status") == "received":
                            sms_list = data.get("sms", [])
                            if sms_list:
                                text = sms_list[0].get("text", "")
                                match = re.search(r'\b(\d{6})\b', text)
                                if match:
                                    return match.group(1)
                    await asyncio.sleep(4)
                except:
                    await asyncio.sleep(4)
        return None
    
    async def cancel_order(self, order_id):
        async with httpx.AsyncClient(headers={"Authorization": f"Bearer {self.api_key}"}) as client:
            try:
                await client.get(f"{self.FIVESIM_API}/user/cancel/{order_id}", timeout=10.0)
            except:
                pass

sms_handler = SMSVerification(FIVESIM_API_KEY)

# ═══════════════════════════════════════════════════════════════════════════
# 4. CAPTCHA SOLVER MODULE
# ═══════════════════════════════════════════════════════════════════════════

class CaptchaSolver:
    def __init__(self, api_key):
        self.solver = TwoCaptcha(api_key) if api_key else None
        self.solve_count = 0
    
    def solve_hcaptcha(self, sitekey, page_url):
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
# 5. UC INSTAGRAM AUTOMATION WORKFLOW (SYNC WORKER)
# ═══════════════════════════════════════════════════════════════════════════

def run_single_account_creation(device_fp, proxy_url, status_callback=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    phone_data = loop.run_until_complete(sms_handler.get_phone_number(country="usa"))
    if not phone_data:
        return None
    
    phone = phone_data["phone"]
    order_id = phone_data["order_id"]
    
    username = f"user_{random.randint(100000, 999999)}"
    password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$", k=16))
    full_name = "Alex " + ''.join(random.choices(string.ascii_letters, k=5))
    dob_year = random.randint(1995, 2003)
    dob_month = random.randint(1, 12)
    dob_day = random.randint(1, 28)

    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-agent={device_fp['user_agent']}")
    
    if proxy_url:
        options.add_argument(f"--proxy-server=http://{proxy_url}")

    driver = None
    try:
        log.info(f"🚀 Launching UC Browser with model {device_fp['model']}...")
        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.set_window_size(390, 844)

        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(5)

        wait = WebDriverWait(driver, 25)

        log.info("✍️ Filling registration details...")
        phone_input = wait.until(EC.presence_of_element_located((By.NAME, "emailOrPhone")))
        phone_input.send_keys(phone)
        
        driver.find_element(By.NAME, "fullName").send_keys(full_name)
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        time.sleep(1.5)
        
        # Click Sign Up
        signup_btn = driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Sign up')]")
        signup_btn.click()
        time.sleep(6)

        # Fill Birthday if requested
        try:
            month_select = driver.find_element(By.NAME, "month")
            if month_select:
                log.info("📅 Filling Birthday dropdowns...")
                from selenium.webdriver.support.ui import Select
                Select(month_select).select_by_value(str(dob_month))
                Select(driver.find_element(By.NAME, "day")).select_by_value(str(dob_day))
                Select(driver.find_element(By.NAME, "year")).select_by_value(str(dob_year))
                time.sleep(1)
                driver.find_element(By.XPATH, "//button[@type='button' and contains(text(), 'Next')]").click()
                time.sleep(5)
        except:
            pass

        # Wait for SMS code
        log.info("⏳ Waiting for SMS code from FiveSim...")
        code = loop.run_until_complete(sms_handler.get_sms_code(order_id, timeout=180))
        
        if not code:
            log.error("SMS code not received.")
            driver.quit()
            loop.run_until_complete(sms_handler.cancel_order(order_id))
            return None

        log.info(f"🔑 Entering SMS code: {code}")
        code_input = wait.until(EC.presence_of_element_located((By.NAME, "confirmationCode")))
        code_input.send_keys(code)
        
        driver.find_element(By.XPATH, "//button[@type='button' and contains(text(), 'Confirm')]").click()
        time.sleep(6)

        driver.quit()
        return {
            "username": username,
            "password": password,
            "phone": phone,
            "device": device_fp['model'],
            "created_at": datetime.now().isoformat()
        }

    except Exception as e:
        log.error(f"UC Automation Exception: {e}")
        if driver:
            try: driver.quit()
            except: pass
        loop.run_until_complete(sms_handler.cancel_order(order_id))
        return None

# ═══════════════════════════════════════════════════════════════════════════
# TELEGRAM BOT COMMANDS & HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 Create Accounts", callback_data="menu_create")],
        [InlineKeyboardButton("📊 Bot Status", callback_data="menu_status")]
    ]
    await update.message.reply_text(
        "🤖 *Instagram Advanced UC Automation Bot*\n\n"
        "⚡ Equipped with Proxy Rotation, Device Fingerprinting & UC Stealth Engine.\n\n"
        "📝 `/create [count]` - Start batch creation\n"
        "📈 `/status` - View health and statistics",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def create_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(ctx.args[0]) if ctx.args else 1
        if count > 10:
            count = 10
            
        msg = await update.message.reply_text(f"🚀 Initializing batch creation for {count} accounts using UC Engine...")
        
        created_accounts = []
        failed_count = 0
        
        loop = asyncio.get_running_loop()
        for i in range(1, count + 1):
            device_fp = DeviceFingerprint.generate()
            proxy = proxy_manager.get_proxy()
            
            await msg.edit_text(f"🔄 **Batch Progress [{i}/{count}]**\n📱 Device: `{device_fp['model']}`\n✅ Success: `{len(created_accounts)}` | ❌ Failed: `{failed_count}`", parse_mode="Markdown")
            
            with concurrent.futures.ThreadPoolExecutor() as pool:
                account_data = await loop.run_in_executor(pool, run_single_account_creation, device_fp, proxy)
            
            if account_data:
                created_accounts.append(account_data)
                await asyncio.sleep(random.uniform(15, 30))
            else:
                failed_count += 1
                await asyncio.sleep(10)
        
        export_filename = f"instagram_accounts_{int(time.time())}.json"
        with open(export_filename, "w", encoding="utf-8") as f:
            json.dump({"total": count, "success": len(created_accounts), "accounts": created_accounts}, f, indent=2)
        
        with open(export_filename, "rb") as f:
            await update.message.reply_document(document=f, caption=f"✅ *Batch Complete!*\n📊 Created: `{len(created_accounts)}/{count}`", parse_mode="Markdown")
        
        if os.path.exists(export_filename):
            os.remove(export_filename)
            
    except Exception as e:
        log.error(f"Create command error: {e}")
        await update.message.reply_text(f"❌ Execution error: {e}")

async def status_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📊 *System Status Report*\n\n"
        f"🛡️ Active Proxies: `{len(RESIDENTIAL_PROXIES) + len(DATACENTER_PROXIES)}`\n"
        f"🔐 Total Captchas Solved: `{captcha_solver.solve_count}`\n"
        f"📱 SMS Provider: `FiveSim (Active)`",
        parse_mode="Markdown"
    )

async def button_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "menu_status":
        await query.message.reply_text(f"📊 Proxies loaded: `{len(RESIDENTIAL_PROXIES)}`", parse_mode="Markdown")
    elif query.data == "menu_create":
        await query.message.reply_text("💡 Send `/create 3` to start creating 3 accounts automatically.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    log.info("🤖 Full-Featured UC Telegram Bot running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
