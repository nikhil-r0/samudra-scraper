import asyncio
from playwright.async_api import async_playwright
import sys

# --- CONFIGURATION ---
IG_AUTH_FILE = "ig_auth_state.json"
X_AUTH_FILE = "x_auth_state.json"

async def auth_instagram():
    """
    Logs into Instagram once and saves the authentication state.
    Later scrapers can reuse this state to appear as a logged-in user.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("\n--- Instagram Authentication Setup ---")
        print("A browser window will open now.")
        print("1. Please log in to your Instagram account (a bot/fake account is recommended).")
        print("2. Solve any CAPTCHAs or verification steps.")
        print("3. Once logged in and your feed is visible, CLOSE the browser window.")

        await page.goto("https://www.instagram.com/accounts/login/")

        print("\nWaiting for you to log in and close the browser... (No timeout)")
        await page.wait_for_event("close", timeout=0)

        await context.storage_state(path=IG_AUTH_FILE)
        print(f"\n✅ Instagram authentication state saved successfully to '{IG_AUTH_FILE}'!")
        await browser.close()

async def auth_x():
    """
    Logs into X.com (Twitter) once and saves the authentication state.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("\n--- X.com (Twitter) Authentication Setup ---")
        print("A browser window will open now.")
        print("1. Please log in to your X.com account (a bot/fake account is recommended).")
        print("2. Solve any CAPTCHAs or verification steps.")
        print("3. Once logged in and your feed is visible, CLOSE the browser window.")

        await page.goto("https://x.com/login")

        print("\nWaiting for you to log in and close the browser... (No timeout)")
        await page.wait_for_event("close", timeout=0)

        await context.storage_state(path=X_AUTH_FILE)
        print(f"\n✅ X.com authentication state saved successfully to '{X_AUTH_FILE}'!")
        await browser.close()

async def main():
    """
    Main entry point to ask user which service to authenticate.
    """
    print("Which platform do you want to authenticate?")
    print("1. Instagram")
    print("2. X.com (Twitter)")
    
    choice = ""
    while choice not in ["1", "2"]:
        choice = input("Enter (1 or 2): ").strip()

    if choice == "1":
        await auth_instagram()
    elif choice == "2":
        await auth_x()

if __name__ == "__main__":
    asyncio.run(main())