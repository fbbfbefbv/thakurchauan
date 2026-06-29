import asyncio
from playwright.async_api import async_playwright
import os
import base64
import json
import time
import random
import requests
import hashlib # Naya import add kiya hai unique ID ke liye

TARGET_URL = os.environ.get("TARGET_URL")
CHAT_ID = os.environ.get("CHAT_ID")
TG_TOKEN = os.environ.get("TG_TOKEN") 
COOKIE_B64 = os.environ.get("COOKIE") 

COMMENTS_LIST = ["🔥 Ek number bhai!", "Bhai kya baat hai! 😍", "Superb video bro 🚀", "Gajab editing 👏"]
DEVICE_MAP_FILE = "amrat_device_map.json"

async def send_screenshot(image_path, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
    def _upload():
        try:
            with open(image_path, 'rb') as photo:
                requests.post(url, data={'chat_id': CHAT_ID, 'caption': text}, files={'photo': photo}, timeout=20)
        except: pass
    await asyncio.to_thread(_upload)

def get_or_assign_device(cookie_id, p):
    device_map = {}
    if os.path.exists(DEVICE_MAP_FILE):
        try:
            with open(DEVICE_MAP_FILE, 'r') as f:
                device_map = json.load(f)
        except: pass

    if cookie_id in device_map:
        assigned_device = device_map[cookie_id]
        if assigned_device in p.devices and 'landscape' not in assigned_device.lower() and 'tablet' not in assigned_device.lower():
            return assigned_device

    all_devices = list(p.devices.keys())
    valid_devices = [d for d in all_devices 
                     if any(k in d for k in ['iPhone', 'Pixel', 'Samsung', 'Galaxy']) 
                     and 'landscape' not in d.lower() 
                     and 'tablet' not in d.lower()
                     and 'fold' not in d.lower()]
    
    time.sleep(random.uniform(0.5, 3.0)) 
    
    assigned_device = random.choice(valid_devices) if valid_devices else "iPhone 13"
    
    device_map[cookie_id] = assigned_device
    with open(DEVICE_MAP_FILE, 'w') as f:
        json.dump(device_map, f, indent=4)
        
    print(f"✨ New valid mobile device: {assigned_device}")
    return assigned_device

async def process_account(browser, cookie_b64, p):
    if not cookie_b64: return
    
    # FIX 1: Base64 ke starting chars ki jagah MD5 hash banaya hai taaki har cookie ka unique id bane
    cookie_unique_id = hashlib.md5(cookie_b64.encode('utf-8')).hexdigest()
    
    device_name = get_or_assign_device(cookie_unique_id, p)
    device_profile = p.devices[device_name]
    
    context = await browser.new_context(**device_profile)
    
    cookie_str = base64.b64decode(cookie_b64).decode()
    cookies = json.loads(cookie_str)
    cleaned_cookies = []
    for c in cookies:
        if 'sameSite' in c and c['sameSite'] not in ['Strict', 'Lax', 'None']: c['sameSite'] = 'Lax'
        if 'id' in c: del c['id']
        cleaned_cookies.append(c)
    await context.add_cookies(cleaned_cookies)
    
    page = await context.new_page()

    try:
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(7)
        await page.keyboard.press("Escape")
        await asyncio.sleep(1) 
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        start_time = time.time()
        
        await asyncio.sleep(random.randint(15, 45))
        current_comment = random.choice(COMMENTS_LIST)
        
        async def do_action(label):
            await page.evaluate(f"(() => {{ let s = document.querySelectorAll('svg[aria-label=\"{label}\"]'); if(s.length>0) s[0].closest('div[role=\"button\"]')?.click(); }})();")
            await asyncio.sleep(1)

        actions = [lambda: do_action("Like"), lambda: do_action("Save"), lambda: do_action("Comment")]
        random.shuffle(actions)
        for act in actions: 
            await act()
            await asyncio.sleep(random.uniform(1, 3))

        elapsed = time.time() - start_time
        if elapsed < 75: await asyncio.sleep(75 - elapsed)
        
        await page.screenshot(path="proof.png")
        await send_screenshot("proof.png", f"✅ Done!\nDevice: {device_name}")
        
    finally:
        await context.close()

async def main():
    async with async_playwright() as p:
        # FIX 2: "--start-maximized" ko hara diya gaya hai taaki mobile view landscape na bane
        browser = await p.chromium.launch(
            channel="chrome", 
            headless=True, 
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        if COOKIE_B64: await process_account(browser, COOKIE_B64, p)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
