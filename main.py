import argparse
import json
import sys

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

BASE_URL = "https://backloggd.com/u/{username}/games"
OUTPUT_FILE = "backloggd-games.json"


def extract_games_from_html(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.game-cover")
    games: list[dict[str, str]] = []

    for card in cards:
        title_div = card.find("div", class_="game-text-centered")
        title = title_div.get_text(strip=True) if title_div else None

        img_tag = card.find("img")
        image = None
        if img_tag:
            image = img_tag.get("src") or img_tag.get("data-src")

        if title:
            games.append({"title": title, "image": image or ""})

    return games


def scrape_user_games(username: str) -> list[dict[str, str]]:
    all_games: list[dict[str, str]] = []
    previous_titles: list[str] | None = None
    page = 1

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        browser_page = browser.new_page()

        while True:
            url = f"{BASE_URL.format(username=username)}?page={page}"
            print(f"Fetching page {page}: {url}")

            try:
                browser_page.goto(url, wait_until="networkidle")
            except Exception as e:
                print(f"Error navigating to page {page}: {e}", file=sys.stderr)
                break

            html = browser_page.content()

            if "403 Forbidden" in browser_page.title():
                print(
                    "Error: received 403 Forbidden. The site may be "
                    "blocking automated access.",
                    file=sys.stderr,
                )
                break

            page_games = extract_games_from_html(html)

            if page == 1 and not page_games:
                print(
                    "No games found on the first page. The username may be "
                    "incorrect or the site structure may have changed.",
                    file=sys.stderr,
                )
                break

            current_titles = [g["title"] for g in page_games]
            if current_titles == previous_titles:
                break

            all_games.extend(page_games)
            previous_titles = current_titles
            page += 1

        browser.close()

    return all_games


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape a Backloggd user's game collection."
    )
    parser.add_argument("username", help="Backloggd username to scrape")
    args = parser.parse_args()

    print(f"Scraping games for user: {args.username}")
    games = scrape_user_games(args.username)

    if not games:
        print("No games were scraped.", file=sys.stderr)
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(games, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(games)} games to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
