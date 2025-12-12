import os
import json
import asyncio
from playwright.async_api import async_playwright


INBOX_URL = "https://supplier.striive.com/inbox/all?searchTerm=data"

PROFILE_DIR = "striive_profile"  # already authenticated locally


async def scrape_vacancies(page):
    print("Scrolling job list…")

    vacancies = set()
    last_count = 0
    stable_rounds = 0

    for j in range(50):  # safety limit
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1200)

        rows = page.locator("app-job-request-list-item")
        count = await rows.count()

        for i in range(count):
            txt = (await rows.nth(i).inner_text()).strip()
            if txt:
                vacancies.add(txt)

        if len(vacancies) == last_count:
            stable_rounds += 1
        else:
            stable_rounds = 0

        last_count = len(vacancies)

        if stable_rounds >= 5:
            break

    return sorted(list(vacancies))


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=True,
            args=["--no-sandbox"]
        )

        page = await browser.new_page()
        await page.goto(INBOX_URL, wait_until="domcontentloaded")

        vacancies = await scrape_vacancies(page)

        with open("vacancies.json", "w") as f:
            json.dump(vacancies, f, indent=4)

        print(f"Scraped {len(vacancies)} vacancies.")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
