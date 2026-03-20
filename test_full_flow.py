import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("1. Opening Application...")
            await page.goto("http://localhost:8080/index.html")
            
            print("2. Attempting Login...")
            await page.fill("#email", "ultimate@example.com")
            await page.fill("#password", "password123")
            await page.click("button[type='submit']")
            await page.wait_for_url("**/dashboard.html", timeout=5000)
            
            print("3. Navigating to Analyze Skills...")
            await page.goto("http://localhost:8080/analyze.html")
            await page.wait_for_selector("#targetCareer", timeout=5000)
            
            print("4. Attempting to add skills and generate roadmap...")
            # We select Data Scientist
            await page.select_option("#targetCareer", value="Data Scientist")
            
            # Type a skill
            await page.fill("#skillInput", "Machine Learning")
            await page.press("#skillInput", "Enter")
            await page.fill("#skillInput", "Statistics")
            await page.press("#skillInput", "Enter")
            
            # Submit form
            await page.click("button[type='submit']")
            
            # Wait for alert prompt and handle it
            page.on("dialog", lambda dialog: dialog.accept())
            
            print("5. Waiting for Progress page navigation...")
            await page.wait_for_url("**/progress.html", timeout=8000)
            
            print("\n✅ SUCCESS: The full application flow is connected and functioning flawlessly!")
            
        except Exception as e:
            print(f"\n❌ FAILED: {str(e)}")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
