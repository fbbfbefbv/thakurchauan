import asyncio
from playwright.async_api import async_playwright
import os
import base64
import json
import time
import random
import requests
import google.generativeai as genai

# --- ENVIRONMENT VARIABLES (Coming from YAML Inputs & Secrets) ---
TARGET_URL = os.environ.get("TARGET_URL")
CHAT_ID = os.environ.get("CHAT_ID")
TG_TOKEN = os.environ.get("TG_TOKEN") 
C1_B64 = os.environ.get("COOKIE_1")
C2_B64 = os.environ.get("COOKIE_2")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- GEMINI AI SETUP ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# 🛡️ Safe Telegram Sender
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

# 🧠 Gemini AI Comment Generator (Updated to Gemini 3.5 Flash as per Screenshot)
async def get_gemini_comment(video_context):
    if not GEMINI_API_KEY:
        return random.choice(["Bhai kya baat hai! 🔥", "Superb video bro 🚀", "Gajab editing 👏", "Ek number bhai! 😍"])
        
    print(f"🧠 AI soch raha hai... Context: {video_context[:40]}...")
    def _generate():
        try:
            # Screenshot ke hisaab se Gemini 3.5 Flash use kar rahe hain
            model = genai.GenerativeModel('gemini-3.5-flash')
            prompt = f"""
            You are a normal Indian Instagram user. Write a short, natural, and highly engaging Instagram comment for a video about: '{video_context}'.
            Rules:
            - Language: Hinglish (Hindi written in English alphabet).
            - Keep it very short (1 sentence maximum).
            - Use 1 or 2 relevant emojis.
            - DO NOT use hashtags, quotes, or robotic words.
            """
            response = model.generate_content(prompt)
            return response.text.strip().replace('"', '')
        except Exception as e:
            print(f"⚠️ Gemini API Error: {e}")
            return random.choice(["Bhai maza aa gaya! 🚀", "Aag laga di! 🔥", "Ek number kaam 💯"])
            
    return await asyncio.to_thread(_generate)

# 🚀 Main Account Processing Logic
async def process_account(browser, cookie_b64, account_num):
    if not cookie_b64 or cookie_b64.strip() == "": 
        print(f"⚠️ Account {account_num} ki cookie nahi mili ya skip kar di gayi!")
        return
    
    print(f"\n=========================================")
    print(f"🟢 Starting Account {account_num}...")
    print(f"=========================================")
    
    try:
        cookie_str = base64.b64decode(cookie_b64).decode()
        cookies = json.loads(cookie_str)
    except Exception as e:
        print(f"❌ Account {account_num} ki Cookie decode nahi hui: {e}")
        return
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    cleaned_cookies = []
    for c in cookies:
        if 'sameSite' in c and c['sameSite'] not in ['Strict', 'Lax', 'None']: c['sameSite'] = 'Lax'
        if 'id' in c: del c['id']
        cleaned_cookies.append(c)
        
    await context.add_cookies(cleaned_cookies)
    page = await context.new_page()

    try:
        print(f"🏠 Account {account_num}: Warming up on Home Page...")
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(7)
        await page.keyboard.press("Escape")
        await asyncio.sleep(1) 

        print(f"🎯 Account {account_num}: Going to Target URL: {TARGET_URL}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        start_time = time.time()
        
        action_start_delay = random.randint(15, 45)
        print(f"⏳ Account {account_num}: Actions shuru hone me {action_start_delay}s lagenge...")
        await asyncio.sleep(action_start_delay)
        
        # --- Context nikal kar AI comment generate karo ---
        page_title = await page.title()
        current_comment = await get_gemini_comment(page_title)
        print(f"✅ Account {account_num} Final AI Comment: '{current_comment}'")
        
        # 🟢 Actions
        async def do_like():
            try:
                print(f"❤️ Account {account_num}: Trying to Like...")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
            except Exception: pass

        async def do_save():
            try:
                print(f"🔖 Account {account_num}: Trying to Save...")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Save\"], svg[aria-label=\"Bookmark\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
            except Exception: pass

        async def do_repost():
            try:
                print(f"🔁 Account {account_num}: Trying to Repost (Share)...")
                clicked = await page.evaluate("""(() => {
                    let s = document.querySelectorAll('svg[aria-label="Share Post"], svg[aria-label="Share"], svg[aria-label="Repost"]');
                    if(s.length>0) { let b = s[0].closest('div[role="button"], button, a'); if(b) { b.click(); return true; } } return false;
                })();""")
                if clicked:
                    await asyncio.sleep(2) 
                    await page.evaluate("""(() => { let elements = document.querySelectorAll('div[role="button"], span, div'); for(let el of elements) { if(el.textContent && el.textContent.trim() === 'Repost') { let btn = el.closest('div[role="button"]') || el; btn.click(); break; } } })();""")
                    await asyncio.sleep(2)
                    await page.evaluate("""(() => { let closeBtns = document.querySelectorAll('svg[aria-label="Close"]'); if(closeBtns.length > 0) { let btn = closeBtns[closeBtns.length - 1].closest('div[role="button"], button'); if(btn) { btn.click(); } } })();""")
            except Exception: pass

        async def do_comment():
            try:
                print(f"💬 Account {account_num}: Trying to Comment...")
                icon_clicked = await page.evaluate("""(() => { let s = document.querySelectorAll('svg[aria-label="Comment"]'); if(s.length>0) { let b = s[0].closest('div[role="button"], button, a'); if(b) { b.click(); return true; } } return false; })();""")
                if not icon_clicked: return

                await asyncio.sleep(3) 
                box_focused = await page.evaluate("""(() => { let box = document.querySelector('textarea[aria-label*="comment" i], div[role="textbox"], input[placeholder*="comment" i], textarea[placeholder*="comment" i]'); if(box) { box.focus(); box.click(); return true; } return false; })();""")
                
                if box_focused:
                    await asyncio.sleep(1)
                    await page.keyboard.type(current_comment, delay=150)
                    await asyncio.sleep(1)
                    posted_via_js = await page.evaluate("""(() => { let elements = document.querySelectorAll('div[role="button"]'); for(let el of elements) { if(el.textContent && el.textContent.trim() === 'Post') { el.click(); return true; } } return false; })();""")
                    if not posted_via_js:
                        post_locator = page.locator('div[role="button"]:text-is("Post")')
                        if await post_locator.count() > 0: await post_locator.last.click(timeout=3000)
            except Exception: pass

        actions = [("Like", do_like), ("Save", do_save), ("Repost", do_repost), ("Comment", do_comment)]
        random.shuffle(actions) 
        
        print(f"🎲 Account {account_num} Action Order: {[a[0] for a in actions]}")
        for name, action in actions:
            await action()
            await asyncio.sleep(random.uniform(1, 3)) 

        print(f"✅ Account {account_num}: Saare Actions Done!")

        # --- Screenshot at exact 75th sec ---
        elapsed = time.time() - start_time
        wait_for_75 = 75 - elapsed
        if wait_for_75 > 0: await asyncio.sleep(wait_for_75)
            
        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 Account {account_num}: Telegram par proof bhej raha hu...")
        await send_screenshot(screenshot_path, f"✅ Account {account_num} Kaam Done!\n📝 AI Comment: {current_comment}")

        # --- Random exit logic ---
        exit_time_target = random.randint(80, 90)
        wait_for_exit = exit_time_target - (time.time() - start_time)
        if wait_for_exit > 0: await asyncio.sleep(wait_for_exit)
            
    except Exception as e: print(f"❌ Error in Account {account_num}:", e)
    finally:
        await context.close()

async def main():
    async with async_playwright() as p:
        # 🚨 Asli Chrome launch kar rahe hain (channel="chrome")
        browser = await p.chromium.launch(channel="chrome", headless=True, args=["--start-maximized"])
        print("\n🚀 Accounts ko ab EK SATH (Parallel) start kar rahe hain...\n")
        
        tasks = []
        if C1_B64: tasks.append(process_account(browser, C1_B64, 1))
        if C2_B64: tasks.append(process_account(browser, C2_B64, 2))
            
        if not tasks:
            print("⚠️ Koi cookie provide nahi ki gayi hai!")
        else:
            await asyncio.gather(*tasks) # Parallel execution
            
        print("\n🏆 SAARE ACCOUNTS KA KAAM SUCCESSFULLY COMPLETE HO GAYA!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
