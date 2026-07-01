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
C1_B64 = os.environ.get("COOKIE_1")
C2_B64 = os.environ.get("COOKIE_2")

COMMENTS_LIST = [
    "Bhai itna motivate kar diya ki ab seedha parso subah jaldi uthunga.",
    "Reel scroll karte karte achanak aukaat yaad dila di, shukriya bhai.",
    "Josh ekdum high hai, ab jaa raha hu wapas sone.",
    "Bhai teri video dekh ke padhne baitha tha, fir book dekh ke wapas aa gaya.",
    "Tu aese hi video banata reh, ek din main pakka ameer ban jaunga.",
    "Motivation itni mili ki ab deewar tod ke padosi ke ghar ghus jaunga.",
    "Sach bata bhai, script likhte time tu bhi roya tha na.",
    "Bhai aapki baten sidha dil pe lagti hain, par dimaag sunne ko taiyar nahi hai.",
    "Kal se gym pakka, agar kal barish nahi hui to.",
    "Aag laga di bhai, bas paani ki balti paas me rakhna.",
    "Itna sach bhi nahi bolna tha bhai, dukh hota hai.",
    "Aapki baatein sun ke laga ki ab duniya jeet lunga, fir yaad aaya mummy ne dhaniya mangwaya hai.",
    "Video mast hai, ab jaldi se ek motivational gaana background me laga le.",
    "Bhai tu cm ban ja, mera vote tere ko hi jayega.",
    "Itna lamba video dekh liya, yahi mere liye sabse bada motivation hai aaj ka.",
    "Bhai aise sach face pe mat mara kar, hum weak heart wale hain.",
    "Gyaan to sahi diya hai, apply karne ki koshish kal se karunga.",
    "Aapke logic me koi flaw nahi hai, bas meri kismat me hai.",
    "Bhai itni mehnat karke video banayi hai, ek like to banta hai meri taraf se.",
    "Motivation sun ke rongte khade ho gaye, ya shayad thand lag rahi hai.",
    "Sahi disha me jaa raha hai launde, rukna mat ab.",
    "Bhai ka content aaj kal aag ugal raha hai.",
    "Ye hui na mardon wali baat, chalo ab bartan dho leta hu.",
    "Pehle laga bore karega, par bhai ne to dho daala.",
    "Aisa content roj dalo, thoda guilty feel karna jaruri hai life me.",
    "Kya line boli hai guru, dil garden garden ho gaya.",
    "Bhai tu toh deep chala gaya ekdum, badiya tha.",
    "Maan gaye ustad, aisi baatein dimag ke taar khol deti hain.",
    "Tere words direct hit karte hain, badiya kaam kar raha hai.",
    "Baat me dum hai, aur bande me bhi.",
    "Bhai ye soch kaha se lata hai, hume bhi thodi udhar de de.",
    "Tu bolta hai to lagta hai ki haan kuch to gadbad chal rahi hai meri life me.",
    "Pura reality check de diya bhai ek hi minute me.",
    "Bhai tu motivate kam karta hai, bezzati jyada feel hoti hai. good job.",
    "Aise truth bombs roz mat gira bhai, pachtane ke liye bhi time chahiye.",
    "Kaafi hard guru, machate raho aise hi.",
    "Bhai ki awaaz me alag hi dard aur motivation dono mix hai.",
    "Sahi khel gaye is topic pe, ekdum relatable tha.",
    "Meri tarah jo log comments padhne aaye hain, bhai video me sach bol raha hai.",
    "Bhai ka level alag hi chal raha hai aajkal, pakadna mushkil hai.",
    "Motivation le li hai maine, ab kal bataunga kaam kaisa chal raha hai.",
    "Bhai tu sach me bahut aage jayega, agar aalasi logo se dur rahega to.",
    "Aapke gyaan ki ganga me aaj dubki laga hi li maine.",
    "Ye video share kar raha hu apne un doston ko jo kabhi sudhrenge nahi.",
    "Bhai tu itna sach bolta hai, log tujhe marte nahi kya.",
    "Mera aalas aapki motivation se lad raha hai, dekhte hain kaun jitega.",
    "Bhai bas aisi 10-15 videos aur dekh lu, fir pakka success mil jayegi.",
    "Kya script likhi hai, jaise mere hi baare me baat ho rahi ho.",
    "Bhai ne aukaat dikha di meri, wo bhi itne pyar se.",
    "Ye hui na asali baat, baki sab to hawabaazi hai.",
    "Motivation ka dose complete hua, ab me web series continue kar sakta hu.",
    "Bhai tu hi bacha sakta hai is generation ko, lage raho.",
    "Bade bhai wali feeling aati hai teri baatein sun kar.",
    "Ek dum kadi baat bol di, bina kisi sugar coating ke.",
    "Ye video mere syllabus me kyu nahi tha pehle.",
    "Bhai ki baat sunkar laga UPSC nikal lunga, fir yaad aaya maine form hi nahi bhara.",
    "Itni motivation aa gayi ki lag raha hai ab pahaad tod du.",
    "Tere jaisa dost sabko mile to aadhe log aese hi ameer ban jaye.",
    "Baatein to badi badi ho gayi, ab practically karke dekhta hu.",
    "Bhai tera content real hai, artificial flavor nahi hai isme.",
    "Acha laga sun kar, lagta hai meri life abhi puri tarah barbaad nahi hui hai.",
    "Ye jo end me aapne bola na, dil pe ja ke laga sidha.",
    "Bhai ne soye hue sher ko jaga diya hai, ab sher thodi der tv dekhega.",
    "Sirf sunne me acha lagta hai ya asliyat me bhi kaam karta hai? try karta hu kal se.",
    "Main chala apna time table banane, jo kal pakka follow nahi hoga.",
    "Bhai ye sab baatein mere papa mujhe bachpan se bol rahe hain, par aapne alag swag me bola.",
    "Video me itni energy kahan se laate ho bhai, bournvita pite ho kya.",
    "Gyan chodne wale bohot hain, par tu gyan apply karvata hai bhai.",
    "Sahi pakde hain, yahi to problem chal rahi hai life me aaj kal.",
    "Bhai ki video pe aake roz reality check leta hu.",
    "Aisa lag raha hai bhai ne chupke se meri life par research kari hai.",
    "Motivation ki factory hai bhai tu.",
    "Jo 3 ghante ki film nahi sikha paati, bhai ne 1 minute me samjha diya.",
    "Bhai thoda dheere bol, meri kismat dar jayegi itne sach se.",
    "Aur yaha main soch raha tha ki sab kismat ka khel hai.",
    "Ekdum kadak video, ab isko status pe laga ke duniya ko gyan dunga.",
    "Bhai sach bata tu ye sab experiences ke baad bol raha hai na.",
    "Tumhara content dekh ke lagta hai abhi umeed baaki hai hum jasio ke liye.",
    "Kasam se rula diya bhai ne, par andar se thoda jagaya bhi.",
    "Yehi wo video hai jiska mujhe saalon se intezaar tha.",
    "Bhai aapki baten kadvii hain par sach much asardar hain.",
    "Video save kar liya hai, jab bhi down feel karunga dekh lunga.",
    "Tu chamkega bhai ek din, aur hum bolenge ki ye apna dost hai.",
    "Kaam ki baat hamesha point to point samajhata hai tu.",
    "Baat to sahi boli, ab dekhte hain aalas chhod pata hu ya nahi.",
    "Sirf ek word bolunga bhai, lajawab.",
    "Jab tak bhai ki video nahi aati mera din theek se shuru nahi hota.",
    "Bhai aapki vajah se maine 10 baje uthna band kar diya, ab 11 baje uthta hu.",
    "Tumhare bolne ka style ekdum natural hai, koi dikhawa nahi.",
    "Sahi line pakdi hai boss, ise hamesha yaad rakhunga.",
    "Ek video ne itna josh bhar diya, soch raha hu election lad lu.",
    "Bhai ko support karo yar, asli content yahi bana raha hai aaj kal.",
    "Bhai teri video dekh ke padhne ka man karne lagta hai, par fir main reel swipe kar deta hu.",
    "Jitna sach bhai ne aaj bola hai, utna toh aaj tak maine khud se nahi bola.",
    "Kya josh hai bhai teri aawaz me, neend ud gayi meri.",
    "Tu badhega aage, aur sath me hum sab ko ghasit ke le jayega.",
    "Words to live by, seriously man. keep the fire burning.",
    "Bhai itna heavy dose mat diya kar subah subah, chakkar aa jate hain.",
    "Gajab ka nazariya hai bhai tera chizo ko dekhne ka, man gaye.",
    "Video khatam ho gaya par bhai ki awaz abhi bhi dimag me gunj rahi hai."
]
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

async def process_account(browser, cookie_b64, account_num):
    if not cookie_b64: 
        print(f"⚠️ Account {account_num} ki cookie nahi mili!")
        return
    
    print(f"\n=========================================")
    print(f"🟢 Starting Account {account_num}...")
    print(f"=========================================")
    
    cookie_str = base64.b64decode(cookie_b64).decode()
    cookies = json.loads(cookie_str)
    
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
        
        print(f"⏳ Account {account_num}: Waiting exactly 7 seconds for popups to appear...")
        await asyncio.sleep(7)
        print(f"⌨️ Account {account_num}: Pressing 'Escape' to close any notifications/popups...")
        await page.keyboard.press("Escape")
        await asyncio.sleep(1) 

        print(f"🎯 Account {account_num}: Going to Target URL: {TARGET_URL}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")
        start_time = time.time()
        
        # --- RANDOM ACTION START TIME (15s to 45s) ---
        action_start_delay = random.randint(15, 45)
        print(f"⏳ Account {account_num}: Bot ab {action_start_delay} seconds wait karega actions shuru karne se pehle...")
        await asyncio.sleep(action_start_delay)
        
        current_comment = random.choice(COMMENTS_LIST)
        
        # 🟢 Action Functions
        async def do_like():
            try:
                print(f"❤️ Account {account_num}: Trying to Like...")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Like\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
                await asyncio.sleep(1)
            except Exception as e: print(f"Like Error Acc {account_num}:", e)

        async def do_save():
            try:
                print(f"🔖 Account {account_num}: Trying to Save...")
                await page.evaluate("(() => { let s = document.querySelectorAll('svg[aria-label=\"Save\"], svg[aria-label=\"Bookmark\"]'); if(s.length>0) { let b = s[0].closest('div[role=\"button\"]'); if(b) b.click(); } })();")
                await asyncio.sleep(1)
            except Exception as e: print(f"Save Error Acc {account_num}:", e)

        async def do_repost():
            try:
                print(f"🔁 Account {account_num}: Trying to Repost (Share)...")
                clicked = await page.evaluate("""(() => {
                    let s = document.querySelectorAll('svg[aria-label="Share Post"], svg[aria-label="Share"], svg[aria-label="Repost"]');
                    if(s.length>0) { 
                        let b = s[0].closest('div[role="button"], button, a'); 
                        if(b) { b.click(); return true; }
                    }
                    return false;
                })();""")
                
                if clicked:
                    await asyncio.sleep(2) 
                    await page.evaluate("""(() => {
                        let elements = document.querySelectorAll('div[role="button"], span, div');
                        for(let el of elements) {
                            if(el.textContent && el.textContent.trim() === 'Repost') {
                                let btn = el.closest('div[role="button"]') || el;
                                btn.click();
                                break;
                            }
                        }
                    })();""")
                    print(f"✅ Account {account_num}: Repost done via JS!")

                    # Popup Close Karne Ke Liye
                    await asyncio.sleep(2)
                    await page.evaluate("""(() => {
                        let closeBtns = document.querySelectorAll('svg[aria-label="Close"]');
                        if(closeBtns.length > 0) {
                            let btn = closeBtns[closeBtns.length - 1].closest('div[role="button"], button');
                            if(btn) { btn.click(); }
                        }
                    })();""")
                    print(f"✅ Account {account_num}: Repost Popup successfully closed!")
                    
                await asyncio.sleep(1)
            except Exception as e: 
                print(f"❌ Account {account_num} Repost Error: {e}")

        async def do_comment():
            try:
                print(f"💬 Account {account_num}: Trying to Comment...")
                icon_clicked = await page.evaluate("""(() => {
                    let s = document.querySelectorAll('svg[aria-label="Comment"]');
                    if(s.length>0) { 
                        let b = s[0].closest('div[role="button"], button, a'); 
                        if(b) { b.click(); return true; }
                    }
                    return false;
                })();""")
                
                if not icon_clicked:
                    print(f"⚠️ Account {account_num}: Comment icon nahi mila.")
                    return

                await asyncio.sleep(3) 
                
                box_focused = await page.evaluate("""(() => {
                    let box = document.querySelector('textarea[aria-label*="comment" i], div[role="textbox"], input[placeholder*="comment" i], textarea[placeholder*="comment" i]');
                    if(box) { 
                        box.focus(); 
                        box.click(); 
                        return true; 
                    }
                    return false;
                })();""")
                
                if box_focused:
                    await asyncio.sleep(1)
                    await page.keyboard.type(current_comment, delay=150)
                    await asyncio.sleep(1)
                    
                    # 🚀 NAYA 100% CONFIRM INSPECT ELEMENT LOGIC 
                    posted_via_js = await page.evaluate("""(() => {
                        let elements = document.querySelectorAll('div[role="button"]');
                        for(let el of elements) {
                            if(el.textContent && el.textContent.trim() === 'Post') {
                                el.click();
                                return true;
                            }
                        }
                        return false;
                    })();""")
                    
                    if posted_via_js:
                        print(f"✅ Account {account_num}: 'Post' button clicked successfully via EXACT element logic!")
                    else:
                        print(f"⚠️ Account {account_num}: JS fail hua, Playwright Native Click try kar raha hu...")
                        try:
                            # Exact match locator based on your inspect element
                            post_locator = page.locator('div[role="button"]:text-is("Post")')
                            if await post_locator.count() > 0:
                                await post_locator.last.click(timeout=3000)
                                print(f"✅ Account {account_num}: Posted via Playwright Native Click!")
                        except Exception as inner_e:
                            print(f"❌ Account {account_num} dono method se Post button click nahi hua.")
                        
                else:
                    print(f"⚠️ Account {account_num}: Comment box detect nahi hua.")
                    
                await asyncio.sleep(4)
            except Exception as e: 
                print(f"❌ Account {account_num} Comment fail hua: {e}")

        # --- RANDOMIZE WORKFLOW ORDER ---
        actions = [
            ("Like", do_like),
            ("Save", do_save),
            ("Repost", do_repost),
            ("Comment", do_comment)
        ]
        random.shuffle(actions) 
        
        print(f"🎲 Account {account_num} Random Action Order:", [a[0] for a in actions])
        for name, action in actions:
            await action()
            await asyncio.sleep(random.uniform(1, 3)) 

        print(f"✅ Account {account_num}: Saare Actions Done!")

        # --- EXACT 75th SECOND SCREENSHOT LOGIC ---
        elapsed = time.time() - start_time
        wait_for_75 = 75 - elapsed
        if wait_for_75 > 0:
            print(f"⏳ Account {account_num}: 75s mark tak pahunchne ke liye {int(wait_for_75)}s aur ruk raha hu...")
            await asyncio.sleep(wait_for_75)
            
        screenshot_path = f"proof_{account_num}.png"
        await page.screenshot(path=screenshot_path)
        print(f"📸 Account {account_num}: 75th Second par Screenshot liya! Telegram par bhej raha hu...")
        await send_screenshot(screenshot_path, f"✅ Account {account_num} ka kaam aur 75s ka proof!\n📝 Comment: {current_comment}")

        # --- RANDOM EXIT BETWEEN 80 to 90 SECONDS ---
        exit_time_target = random.randint(80, 90)
        elapsed_now = time.time() - start_time
        wait_for_exit = exit_time_target - elapsed_now
        
        if wait_for_exit > 0: 
            print(f"⏳ Account {account_num}: Final Random Exit ke liye {int(wait_for_exit)} seconds bache hain...")
            await asyncio.sleep(wait_for_exit)
            
    except Exception as e: print(f"Error in Account {account_num}:", e)
    finally:
        total_time_spent = int(time.time() - start_time) if 'start_time' in locals() else 0
        print(f"🏁 Account {account_num} session closed after ~{total_time_spent} seconds.")
        await context.close()

async def main():
    async with async_playwright() as p:
        # Browser launch ek hi baar hoga
        browser = await p.chromium.launch(channel="chrome", headless=True, args=["--start-maximized"])
        
        print("\n🚀 Accounts ko ab EK SATH (Paralell) start kar rahe hain...\n")
        
        tasks = [] # Dono tasks ko ek list me daalenge
        
        if C1_B64:
            tasks.append(process_account(browser, C1_B64, 1))
            
        if C2_B64:
            tasks.append(process_account(browser, C2_B64, 2))
            
        if not tasks:
            print("⚠️ Koi cookie provide nahi ki gayi hai!")
        else:
            # ⚡ asyncio.gather saare tasks ko aage-piche nahi, balki EXACT ek time par fire karta hai
            await asyncio.gather(*tasks)
            
        print("\n🏆 SAARE ACCOUNTS KA KAAM SUCCESSFULLY COMPLETE HO GAYA!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
