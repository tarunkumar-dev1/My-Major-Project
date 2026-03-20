import asyncio
from playwright.async_api import async_playwright
import traceback

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Capture console messages
        page.on("console", lambda msg: print(f"Browser Console ({msg.type}): {msg.text}"))
        page.on("pageerror", lambda err: print(f"Browser Error: {err}"))
        
        try:
            print("Navigating to login...")
            await page.goto("http://localhost:8080/index.html")
            await page.fill("#email", "ultimate@example.com")
            await page.fill("#password", "password123")
            await page.click("button[type='submit']")
            
            await page.wait_for_url("**/dashboard.html", timeout=5000)
            print("Successfully logged in.")
            
            # Now navigate to profile
            print("Navigating to profile.html...")
            await page.goto("http://localhost:8080/profile.html")
            await page.wait_for_selector("#profileName", timeout=5000)
            
            name_text = await page.locator("#profileName").inner_text()
            print(f"Profile Loaded Name: {name_text}")
            
            print("Clicking Edit Profile...")
            await page.click("#editProfileBtn")
            
            print("Changing Name...")
            await page.fill("#editName", "Verified Ultimate")
            
            print("Clicking Save Profile...")
            await page.click("#saveProfileBtn")
            
            # wait for update
            await page.wait_for_timeout(2000)
            
            new_name = await page.locator("#profileName").inner_text()
            print(f"Updated Profile Name: {new_name}")
            
        except Exception as e:
            print("Script Error:")
            traceback.print_exc()
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
