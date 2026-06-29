import asyncio
from playwright.async_api import async_playwright
import os
import base64
import json
import time
import random
import requests

TARGET_URL = os.environ.get("TARGET_URL")
CHAT_ID = os.environ.get("CHAT_ID")
TG_TOKEN = os.environ.get("TG_TOKEN") 
COOKIE_B64 = os.environ.get("COOKIE") 

COMMENTS_LIST = ["🔥 Ek number bhai!", "Bhai kya baat hai! 😍", "Superb video bro 🚀", "Gajab editing 👏"]
DEVICE_MAP_FILE = "amrat_device_map.json"

# 🛡️ Safe Telegram Sender with Retry Logic
async def send_screenshot(image_path, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
    def _upload():
        max_retries = 3
        attempt = 0
        while attempt < max_retries:
            try:
                with open(image_path, 'rb') as photo:
                    res = requests.post(url, data={'chat_id': CHAT_ID, 'caption': text}, files={'photo': photo}, timeout=20)
                if res.status_code == 200: break
            except Exception as e:
                attempt += 1
                time.sleep(2)
    await asyncio.to_thread(_upload)

# 🗂️ Dynamic Device Selector (Strict Mobile Only)
def get_or_assign_device(cookie_id, p):
    if os.path.exists(DEVICE_MAP_FILE):
        try:
            with open(DEVICE_MAP_FILE, 'r') as f:
                device_map = json.load(f)
        except:
            device_map = {}
    else:
        device_map = {}

    if cookie_id in device_map:
        assigned_device = device_map[cookie_id]
        if assigned_device in p.devices:
            print(f"🔄 Purana fix device: {assigned_device}")
            return assigned_device

    # 💡 Strict Mobile Filtering Logic
    all_devices = list(p.devices.keys())
    forbidden = ['landscape', 'tablet', 'iPad', 'Nexus 10', 'Fold', 'Mini', 'TV', 'Desktop']
    allowed = ['iPhone', 'Pixel', 'Samsung', 'Galaxy', 'Moto']
    
    safe_mobiles = [d for d in all_devices 
                    if any(k in d for k in allowed) 
                    and not any(f in d for f in forbidden)]
    
    # ⚡ Staggering to prevent duplicate assignment
    time.sleep(random.uniform(0.5, 2.0)) 
    assigned_device = random.choice(safe_mobiles) if safe_mobiles else "iPhone 13"
    
    device_map[cookie_id] = assigned_device
    with open(DEVICE_MAP_FILE, 'w') as f:
        json.dump(device_map, f, indent=4)
        
    print(f"✨ Naya mobile device assign hua: {assigned_device}")
    return assigned_device

async def process_account(browser, cookie_b64, p):
    if not cookie_b64: 
        print(f"⚠️ Cookie nahi mili!")
        return
    
    print(f"\n=========================================")
    print(f"🟢 Starting Single Account Session...")
    print(f"=========================================")
    
    cookie_unique_id = cookie_b64[:30] 
    device_name = get_or_assign_device(cookie_unique_id, p)
    device_profile = p.devices[device_name]
    
    cookie_str = base64.b64decode(cookie_b64).decode()
    cookies = json.loads(cookie_str)
    
    # 🚨 FIX: Sirf **device_profile pass karo (User-Agent inside)
    context = await browser.new_context(**device_profile)
    
    cleaned_cookies = []
    for c in cookies:
        if 'sameSite' in c and c['sameSite'] not in ['Strict', 'Lax', 'None']: c['sameSite'] = 'Lax'
        if 'id' in c: del c['id']
        cleaned_cookies.append(c)
        
    await context.add_cookies(cleaned_cookies)
    page = await context.new_page()

    try:
        print(f"🏠 Warming up on Home Page...")
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(7)
        await page.keyboard.press("Escape")
        await asyncio.sleep(1) 

        print(f"🎯 Going to Target URL: {TARGET_URL}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        start_time = time.time()
        
        await asyncio.sleep(random.randint(15, 45))
        current_comment = random.choice(COMMENTS_LIST)
        
        # 🟢 Action Functions
        async def do_like():
            try:
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
                await asyncio.sleep(1)
            except Exception as e: print("Like Error:", e)

        async def do_save():
            try:
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Save\"], svg[aria-label=\"Bookmark\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
                await asyncio.sleep(1)
            except Exception as e: print("Save Error:", e)

        async def do_repost():
            try:
                clicked = await page.evaluate("""(() => {
                    let s = document.querySelectorAll('svg[aria-label="Share Post"], svg[aria-label="Share"], svg[aria-label="Repost"]');
                    if(s.length>0) { let b = s[0].closest('div[role="button"], button, a'); if(b) { b.click(); return true; } }
                    return false;
                })();""")
                if clicked:
                    await asyncio.sleep(2) 
                    await page.evaluate("""(() => {
                        let elements = document.querySelectorAll('div[role="button"], span, div');
                        for(let el of elements) { if(el.textContent && el.textContent.trim() === 'Repost') { el.closest('div[role="button"]')?.click(); break; } }
                    })();""")
                    await asyncio.sleep(2)
                    await page.evaluate("""(() => {
                        let closeBtns = document.querySelectorAll('svg[aria-label="Close"]');
                        if(closeBtns.length > 0) { closeBtns[closeBtns.length - 1].closest('div[role="button"], button')?.click(); }
                    })();""")
            except Exception as e: print("Repost Error:", e)

        async def do_comment():
            try:
                icon_clicked = await page.evaluate("""(() => {
                    let s = document.querySelectorAll('svg[aria-label="Comment"]');
                    if(s.length>0) { let b = s[0].closest('div[role="button"], button, a'); if(b) { b.click(); return true; } }
                    return false;
                })();""")
                if not icon_clicked: return

                await asyncio.sleep(3) 
                box_focused = await page.evaluate("""(() => {
                    let box = document.querySelector('textarea[aria-label*="comment" i], div[role="textbox"], input[placeholder*="comment" i], textarea[placeholder*="comment" i]');
                    if(box) { box.focus(); box.click(); return true; }
                    return false;
                })();""")
                
                if box_focused:
                    await asyncio.sleep(1)
                    for char in current_comment:
                        await page.keyboard.type(char)
                        await asyncio.sleep(random.uniform(0.05, 0.25))
                    await asyncio.sleep(1)
                    
                    posted = await page.evaluate("""(() => {
                        let elements = document.querySelectorAll('div[role="button"]');
                        for(let el of elements) { if(el.textContent && el.textContent.trim() === 'Post') { el.click(); return true; } }
                        return false;
                    })();""")
            except Exception as e: print("Comment Error:", e)

        actions = [("Like", do_like), ("Save", do_save), ("Repost", do_repost), ("Comment", do_comment)]
        random.shuffle(actions) 
        for name, action in actions:
            await action()
            await asyncio.sleep(random.uniform(1, 3)) 

        # 📸 Screenshot
        elapsed = time.time() - start_time
        wait_for_75 = 75 - elapsed
        if wait_for_75 > 0: await asyncio.sleep(wait_for_75)
            
        screenshot_path = "proof_single.png"
        await page.screenshot(path=screenshot_path)
        await send_screenshot(screenshot_path, f"✅ Done!\nDevice: {device_name}")

        wait_for_exit = random.randint(80, 90) - (time.time() - start_time)
        if wait_for_exit > 0: await asyncio.sleep(wait_for_exit)
            
    finally:
        await context.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome", 
            headless=True, 
            args=["--start-maximized", "--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        if COOKIE_B64: await process_account(browser, COOKIE_B64, p)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
