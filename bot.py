# language: Python, file: ig_creator.py
# deps: pip install -r requirements.txt

import os
import re
import csv
import sys
import time
import json
import random
import string
import subprocess
import logging
from datetime import datetime

import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from twocaptcha import TwoCaptcha

# ── config (Railway Variables se aata hai) ────────────────────────────────
BOT_TOKEN      = os.environ.get("BOT_TOKEN", "")
TWOCAPTCHA_KEY = os.environ.get("TWOCAPTCHA_KEY", "")
FIVESIM_KEY    = os.environ.get("FIVESIM_KEY", "")
SMS_COUNTRY    = os.environ.get("SMS_COUNTRY", "russia")

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

CREATED_CSV = "created.csv"
OUT_JSON    = "accounts.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler("bot.log", encoding="utf-8"),
              logging.StreamHandler()],
)
log = logging.getLogger("ig")

# ── chromium major version (Docker ke chromium se match) ─────────────────
def chromium_major():
    for binary in ("chromium", "/usr/bin/chromium", "chromium-browser"):
        try:
            out = subprocess.check_output([binary, "--version"],
                                          text=True, timeout=5,
                                          stderr=subprocess.DEVNULL)
            m = re.search(r"(\d+)\.", out)
            if m:
                return int(m.group(1))
        except Exception:
            continue
    return None

# ── device fingerprints ───────────────────────────────────────────────────
IPHONES = [
    {"model": "iPhone 15 Pro", "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1", "res": (390, 844)},
    {"model": "iPhone 14",     "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",     "res": (390, 844)},
]
ANDROIDS = [
    {"model": "Galaxy S24 Ultra", "ua": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",  "res": (412, 915)},
    {"model": "Pixel 8 Pro",      "ua": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36", "res": (480, 1084)},
]

def gen_device():
    return random.choice(IPHONES if random.random() < 0.6 else ANDROIDS)

# ── proxy pool ────────────────────────────────────────────────────────────
class ProxyPool:
    def __init__(self, res, dc):
        self.res, self.dc, self.dead = list(res), list(dc), set()
    def get(self):
        for pool in (self.res, self.dc):
            live = [p for p in pool if p not in self.dead]
            if live:
                return random.choice(live)
        return None
    def mark_dead(self, p):
        if p:
            self.dead.add(p)

proxies = ProxyPool(RESIDENTIAL_PROXIES, DATACENTER_PROXIES)

# ── 5sim (sync) ───────────────────────────────────────────────────────────
class FiveSim:
    BASE = "https://5sim.net/v1"
    def __init__(self, key):
        self.h = {"Authorization": f"Bearer {key}", "Accept": "application/json"}
    def buy(self, country=SMS_COUNTRY, product="instagram"):
        r = requests.get(f"{self.BASE}/user/buy/activation/{country}/any/{product}",
                         headers=self.h, timeout=20)
        if r.status_code != 200:
            log.error("5sim buy %s: %s", r.status_code, r.text[:200])
            return None
        d = r.json()
        log.info("5sim number %s (order %s)", d.get("phone"), d.get("id"))
        return {"phone": d.get("phone"), "order_id": d.get("id")}
    def code(self, order_id, timeout=300):
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(5)
            try:
                r = requests.get(f"{self.BASE}/user/check/{order_id}",
                                 headers=self.h, timeout=10)
            except requests.RequestException:
                continue
            if r.status_code != 200:
                continue
            d = r.json()
            st = d.get("status")
            if st in ("CANCELED", "TIMEOUT", "BANNED"):
                log.error("5sim order died: %s", st)
                return None
            if st == "RECEIVED":
                sms = d.get("sms") or []
                if sms:
                    m = re.search(r"\b(\d{6})\b", sms[-1].get("text", ""))
                    if m:
                        return m.group(1)
        return None
    def finish(self, oid):
        try: requests.get(f"{self.BASE}/user/finish/{oid}", headers=self.h, timeout=10)
        except Exception: pass
    def cancel(self, oid):
        try: requests.get(f"{self.BASE}/user/cancel/{oid}", headers=self.h, timeout=10)
        except Exception: pass

sms = FiveSim(FIVESIM_KEY)

# ── 2captcha ──────────────────────────────────────────────────────────────
class Captcha:
    def __init__(self, key):
        self.s = TwoCaptcha(key) if key else None
        self.count = 0
    def hcaptcha(self, sitekey, url):
        if not self.s: return None
        try:
            r = self.s.hcaptcha(sitekey=sitekey, pageurl=url)
            self.count += 1
            log.info("hCaptcha solved")
            return r.get("code")
        except Exception as e:
            log.error("hCaptcha: %s", e)
            return None
    def recaptcha(self, sitekey, url):
        if not self.s: return None
        try:
            r = self.s.recaptcha(sitekey=sitekey, url=url, version="v3",
                                 action="signup")
            self.count += 1
            log.info("reCaptcha v3 solved")
            return r.get("code")
        except Exception as e:
            log.error("reCaptcha v3: %s", e)
            return None

captcha = Captcha(TWOCAPTCHA_KEY)

# ── helpers ───────────────────────────────────────────────────────────────
def find_first(driver, locators, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        for by, val in locators:
            try:
                for el in driver.find_elements(by, val):
                    if el.is_displayed():
                        return el
            except Exception:
                pass
        time.sleep(0.5)
    return None

def detect_captcha(driver):
    html = driver.page_source
    m = re.search(r'"sitekey"\s*:\s*"([0-9a-fA-F-]{20,})"', html)
    sitekey = m.group(1) if m else None
    if "hcaptcha.com" in html or "h-captcha" in html:
        return ("hcaptcha", sitekey)
    if "recaptcha/api.js" in html or "g-recaptcha" in html or "grecaptcha" in html:
        return ("recaptcha", sitekey)
    return None

def inject_token(driver, kind, token):
    field = "h-captcha-response" if kind == "hcaptcha" else "g-recaptcha-response"
    driver.execute_script("""
        const name = arguments[0], tok = arguments[1];
        document.querySelectorAll('[name="'+name+'"]').forEach(e => e.value = tok);
        const byId = document.getElementById(name);
        if (byId) { byId.value = tok; byId.innerHTML = tok; }
    """, field, token)

def solve_if_present(driver):
    cap = detect_captcha(driver)
    if not cap:
        return True
    kind, sitekey = cap
    if not sitekey:
        log.warning("captcha present, no sitekey")
        return False
    log.info("solving %s", kind)
    token = (captcha.hcaptcha(sitekey, driver.current_url)
             if kind == "hcaptcha"
             else captcha.recaptcha(sitekey, driver.current_url))
    if not token:
        return False
    inject_token(driver, kind, token)
    time.sleep(1.5)
    return True

def account_live(driver):
    url = driver.current_url
    if any(x in url for x in ("emailsignup", "/confirm", "/challenge", "/suspended")):
        return False
    if driver.find_elements(By.XPATH, "//*[@aria-label='Home']"):
        return True
    if driver.find_elements(By.XPATH, "//*[contains(@href,'/explore/')]"):
        return True
    return False

# ── worker ────────────────────────────────────────────────────────────────
def create_one(device, proxy, country=SMS_COUNTRY):
    order = sms.buy(country=country)
    if not order:
        return None
    phone, order_id = order["phone"], order["order_id"]

    username = f"u{random.randint(10**9, 10**10 - 1)}"
    password = "".join(random.choices(string.ascii_letters + string.digits + "!@#", k=14))
    full_name = "Alex " + "".join(random.choices(string.ascii_letters, k=5))
    y, m, d = random.randint(1995, 2003), random.randint(1, 12), random.randint(1, 28)

    opts = uc.ChromeOptions()
    opts.headless = True
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=390,844")
    opts.add_argument(f"--user-agent={device['ua']}")
    if proxy:
        opts.add_argument(f"--proxy-server=http://{proxy}")

    driver = None
    try:
        log.info("launch %s via %s", device["model"], proxy)
        vm = chromium_major()
        driver = uc.Chrome(options=opts, version_main=vm) if vm else uc.Chrome(options=opts)
        driver.set_window_size(*device["res"])
        driver.get("https://www.instagram.com/accounts/emailsignup/")
        time.sleep(5)
        solve_if_present(driver)

        el = find_first(driver, [(By.NAME, "emailOrPhone"),
                                 (By.XPATH, "//input[@aria-label='Mobile number or email']")])
        if not el:
            raise RuntimeError("phone field missing")
        el.send_keys(phone)

        fn = find_first(driver, [(By.NAME, "fullName")], timeout=8)
        if fn: fn.send_keys(full_name)

        for _ in range(3):
            u = find_first(driver, [(By.NAME, "username")], timeout=8)
            if not u: break
            u.clear(); u.send_keys(username); time.sleep(1.2)
            if not driver.find_elements(By.XPATH,
                    "//*[contains(text(),'not available') or contains(text(),'already taken')]"):
                break
            username = f"u{random.randint(10**9, 10**10 - 1)}"

        pw = find_first(driver, [(By.NAME, "password")], timeout=8)
        if pw: pw.send_keys(password)
        time.sleep(1.5)

        solve_if_present(driver)

        btn = find_first(driver, [(By.XPATH, "//button[@type='submit']"),
                                  (By.XPATH, "//button[contains(.,'Sign up')]"),
                                  (By.XPATH, "//button[contains(.,'Next')]")], timeout=10)
        if not btn:
            raise RuntimeError("signup button missing")
        btn.click(); time.sleep(6)

        month = find_first(driver, [(By.NAME, "month")], timeout=4)
        if month:
            Select(month).select_by_value(str(m))
            Select(driver.find_element(By.NAME, "day")).select_by_value(str(d))
            Select(driver.find_element(By.NAME, "year")).select_by_value(str(y))
            time.sleep(1)
            nb = find_first(driver, [(By.XPATH, "//button[contains(.,'Next')]")], timeout=5)
            if nb: nb.click()
            time.sleep(5)

        solve_if_present(driver)

        log.info("waiting 5sim code (order %s)", order_id)
        code = sms.code(order_id, timeout=300)
        if not code:
            log.error("no SMS code")
            sms.cancel(order_id)
            return None
        log.info("code %s", code)

        code_field = find_first(driver, [
            (By.NAME, "confirmationCode"),
            (By.NAME, "email_confirmation_code"),
            (By.NAME, "confirmation_code"),
            (By.XPATH, "//input[@inputmode='numeric']"),
            (By.XPATH, "//input[@type='tel']"),
        ], timeout=20)
        if not code_field:
            raise RuntimeError("code field missing")
        code_field.clear(); code_field.send_keys(code)

        conf = find_first(driver, [(By.XPATH, "//button[contains(.,'Confirm') or contains(.,'Next')]")],
                          timeout=10)
        if conf: conf.click()
        time.sleep(8)

        if not account_live(driver):
            log.warning("signup incomplete, url=%s", driver.current_url)
            sms.cancel(order_id)
            return None

        sms.finish(order_id)
        rec = {"username": username, "password": password, "phone": phone,
               "device": device["model"], "created_at": datetime.now().isoformat()}
        with open(CREATED_CSV, "a", newline="") as fh:
            csv.writer(fh).writerow([username, password, phone, device["model"]])
        log.info("CREATED %s / %s", username, password)
        return rec
    except Exception as e:
        log.exception("worker: %s", e)
        return None
    finally:
        if driver:
            try: driver.quit()
            except Exception: pass

# ── runner ────────────────────────────────────────────────────────────────
def run(n=1, country=SMS_COUNTRY):
    made = []
    for i in range(1, n + 1):
        device = gen_device()
        proxy = proxies.get()
        log.info("[%d/%d] %s via %s", i, n, device["model"], proxy)
        rec = create_one(device, proxy, country)
        if rec:
            made.append(rec)
            time.sleep(random.uniform(15, 30))
        else:
            proxies.mark_dead(proxy)
            time.sleep(random.uniform(10, 20))
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump({"total": n, "success": len(made), "accounts": made},
                  fh, indent=2, ensure_ascii=False)
    log.info("done: %d/%d → %s", len(made), n, OUT_JSON)
    return made

# ── telegram ──────────────────────────────────────────────────────────────
def start_telegram():
    if not BOT_TOKEN:
        log.info("no BOT_TOKEN — CLI mode")
        return False
    from telegram.ext import Application, CommandHandler
    async def cmd_start(update, ctx):
        await update.message.reply_text("IG creator ready.\n/create [n]\n/status")
    async def cmd_create(update, ctx):
        n = int(ctx.args[0]) if ctx.args else 1
        n = min(n, 10)
        msg = await update.message.reply_text(f"running {n}...")
        made = run(n)
        await msg.edit_text(f"done: {len(made)}/{n}\nsee {OUT_JSON}")
    async def cmd_status(update, ctx):
        await update.message.reply_text(
            f"proxies: {len(proxies.res)+len(proxies.dc)-len(proxies.dead)}\n"
            f"captchas solved: {captcha.count}")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("create", cmd_create))
    app.add_handler(CommandHandler("status", cmd_status))
    log.info("telegram polling")
    app.run_polling(drop_pending_updates=True)
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        run(int(sys.argv[1]))
    else:
        if not start_telegram():
            run(1)
