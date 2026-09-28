import asyncio
import random
import string
import logging
from playwright.async_api import async_playwright
from twocaptcha import TwoCaptcha
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ═══════════════════════════════════════════════════════════════════════════
# LOGGING & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

BOT_TOKEN = "8948043707:AAGDrCONfkuoydMQjHFPSAeFlouJvTv-AV0"
TWOCAPTCHA_KEY = "6498bcd403bd611438b1fb68568355b1"
FIVESIM_API_KEY = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjIwNTIxMDQsImlhdCI6MTc5MDUxNjEwNCwicmF5IjoiNDMzNjhkNTQ5NGNlM2YzM2UzNTYwMGE1ZGIxOTc0NWUiLCJzdWIiOjQ1NzU0ODh9.csk2R9FNfET5ZhvdjBsOpVX-lYiVTHZCPw7UYFpZcCMUhNtjWJ-BhI2vUXB4F_8kIxU1Xlm6nAg4yraJ5lW5jP9xoZHiT6bu7drW_klEBMZ6pSVak_0RjtyCE5wMXeBqnxbsijd7sYhNz9JVXzHud6Qp7Nbaqr-Xwpqz9ilycM353h8c8G2nxr7Csb8xNSOiy1KXU-5LGfa8mErxHqyRQnVsr7gXpnVlSg4sObdrXbzO17UabirAKga0C3O3_ISUD3lsZLI2QDSaFW2LU_jh5SPg6cuCZpg86_JSxAgleLEth2tdxN0_lryw-NUrGGRGSnbtHwVOM5xUeKqMlBrBrw"

# Proxy Pool from your list
RAW_PROXIES = [
    "us6.cactussstp.com:3129:uncpjndo:w77Ebc0h2A",
    "hk1.cactussstp.com:8080:uncpjndo:w77Ebc0h2A",
    "it1.cactussstp.com:3129:bvmbsmie:shibby2511",
    "uk3.cactussstp.com:3129:uncpjndo:w77Ebc0h2A",
    "in1.cactussstp.com:8080:yefprelf:dr2gsmab",
    "au1.cactussstp.com:3129:bvmbsmie:shibby2511",
    "lv1.cactussstp.com:81:uncpjndo:w77Ebc0h2A",
    "us3.cactussstp.com:3129:hughmuir2:lisamarie11",
    "ca1.cactussstp.com:81:uncpjndo:w77Ebc0h2A",
    "ch1.cactussstp.com:8080:yefprelf:dr2gsmab",
    "my1.cactussstp.com:81:uncpjndo:w77Ebc0h2A",
    "px022409.pointtoserver.com:10780:purevpn0s551451:9dpdlc2nfxgj",
    "in-ban.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2",
    "p.webshare.io:80:khanrayhan9910-rotate:Asutonu9",
    "37.49.150.244:41731:1TCNvZkNJiZZPGX:sQfBBjZGVDqYl9V",
    "uk2.cactussstp.com:81:uncpjndo:w77Ebc0h2A",
    "px591801.pointtoserver.com:10780:purevpn0s551451:9dpdlc2nfxgj",
    "px241102.pointtoserver.com:10780:purevpn0s2232045:hww8fqbr72j0",
    "p103.squidproxies.com:9238:1401:FVRHsSXw2DNK",
    "px022507.pointtoserver.com:10780:purevpn0s551451:9dpdlc2nfxgj",
    "it-mil.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2",
    "px023005.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "au-per.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2",
    "px152201.pointtoserver.com:10780:purevpn0s8732217:i67s60ep",
    "my-kua.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2",
    "px400501.pointtoserver.com:10780:purevpn0s7397024:6CU9ZvexLGTqpB",
    "px051703.pointtoserver.com:10780:reseller3270s320237:7Grp9Gki",
    "uk3.cactussstp.com:3129:hughmuir2:lisamarie11",
    "sk-bra.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2",
    "px410701.pointtoserver.com:10780:purevpn0s551451:9dpdlc2nfxgj",
    "uk3.cactussstp.com:81:bvmbsmie:shibby2511",
    "au1.cactussstp.com:8080:uncpjndo:w77Ebc0h2A",
    "px051003.pointtoserver.com:10780:purevpn0s2232045:hww8fqbr72j0",
    "us6.cactussstp.com:3129:hughmuir2:lisamarie11",
    "px043006.pointtoserver.com:10780:purevpn0s11340994:ak3t35fp",
    "px420602.pointtoserver.com:10780:purevpn0s551451:9dpdlc2nfxgj",
    "px040805.pointtoserver.com:10780:purevpn0s7397024:6CU9ZvexLGTqpB",
    "uk2.cactussstp.com:8080:hughmuir2:lisamarie11",
    "ca-mon.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2",
    "se-got.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2",
    "id-jak.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2"
]

def get_random_proxy_dict():
    p = random.choice(RAW_PROXIES)
    parts = p.split(":")
    if len(parts) == 4:
        host, port, user, pwd = parts
        return {
            "server": f"http://{host}:{port}",
            "username": user,
            "password": pwd
        }
    elif len(parts) == 2:
        host, port = parts
        return {"server": f"http://{host}:{port}"}
    return {"server": f"http://{p}"}

# ═══════════════════════════════════════════════════════════════════════════
# FIVESIM API HANDLER
# ═══════════════════════════════════════════════════════════════════════════

class FiveSimAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://5sim.net/v1"

    async def get_number(self, country="usa"):
        url = f"{self.base_url}/user/buy/activation/{country}/any/instagram"
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
        url = f"https://5sim.net/v1/user/check/{order_id}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}
        start_time = asyncio.get_event_loop().time()
        async with httpx.AsyncClient() as client:
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    r = await client.get(url, headers=headers, timeout=10.0)
                    if r.status_code == 200:
                        data = r.json()
                        if data.get("status") == "received":
                            sms_list = data.get("sms", [])
                            if sms_list:
                                text = sms_list[0].get("text", "")
                                import re
                                match = re.search(r'\b(\d{6})\b', text)
                                if match:
                                    return match.group(1)
                    await asyncio.sleep(4)
                except:
                    await asyncio.sleep(4)
        return None

    async def cancel(self, order_id):
        async with httpx.AsyncClient() as client:
            try:
                await client.get(f"https://5sim.net/v1/user/cancel/{order_id}", headers={"Authorization": f"Bearer {self.api_key}"})
            except:
                pass

# ═══════════════════════════════════════════════════════════════════════════
# PLAYWRIGHT AUTOMATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

async def run_playwright_signup(status_cb=None):
    fivesim = FiveSimAPI(FIVESIM_API_KEY)
    
    if status_cb:
        await status_cb("📱 Buying number from FiveSim...")
    phone_data = await fivesim.get_number(country="usa")
    if not phone_data:
        return None
    
    phone = phone_data["phone"]
    order_id = phone_data["order_id"]
    
    username = f"user_{random.randint(100000, 999999)}"
    password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$", k=16))
    full_name = "Alex " + ''.join(random.choices(string.ascii_letters, k=5))

    proxy_cfg = get_random_proxy_dict()
    log.info(f"Using proxy server: {proxy_cfg.get('server')}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            proxy=proxy_cfg,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()

        try:
            if status_cb:
                await status_cb("🌍 Opening Instagram signup page...")
            await page.goto("https://www.instagram.com/accounts/emailsignup/", timeout=60000)
            await page.wait_for_load_state("networkidle")

            if status_cb:
                await status_cb("✍️ Filling registration details...")
            
            # Fill phone/email field
            await page.fill('input[name="emailOrPhone"]', phone)
            await page.fill('input[name="fullName"]', full_name)
            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)

            await page.click('button:has-text("Sign up")')
            await asyncio.sleep(5)

            # Check if SMS code input appears
            if status_cb:
                await status_cb("⏳ Waiting for SMS code from FiveSim...")
            code = await fivesim.get_sms_code(order_id)
            if not code:
                log.error("SMS code not received.")
                await fivesim.cancel(order_id)
                await browser.close()
                return None

            if status_cb:
                await status_cb(f"🔑 Entering SMS code: {code}")
            
            # Type verification code if input field exists
            await page.fill('input[name="confirmationCode"]', code)
            await page.click('button:has-text("Confirm")')
            await asyncio.sleep(5)

            await browser.close()
            return {"username": username, "password": password, "phone": phone}

        except Exception as e:
            log.error(f"Playwright Automation Exception: {e}")
            await fivesim.cancel(order_id)
            await browser.close()
            return None

# ═══════════════════════════════════════════════════════════════════════════
# TELEGRAM BOT HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Instagram Playwright Automation Bot Active!\n\nUse `/create` to register.")

async def create_command(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🚀 Starting Playwright automation...")
    
    async def update_status(text):
        try:
            await msg.edit_text(f"🔄 **Status:** {text}", parse_mode="Markdown")
        except:
            pass

    account = await run_playwright_signup(status_cb=update_status)
    
    if account:
        await update.message.reply_text(
            f"✅ **Account Created Successfully!**\n\n"
            f"👤 Username: `{account['username']}`\n"
            f"🔑 Password: `{account['password']}`\n"
            f"📱 Phone: `{account['phone']}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("❌ Account creation failed. Check logs.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create_command))
    log.info("🤖 Bot polling started with Playwright stack...")
    app.run_polling()

if __name__ == "__main__":
    main()
