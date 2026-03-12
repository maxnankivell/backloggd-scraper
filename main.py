import json
import os
import sys
import threading

import requests
from bs4 import BeautifulSoup
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

BASE_URL = "https://backloggd.com/u/{username}/games"
_OUTPUT_DIR = os.path.dirname(
    os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__)
)
OUTPUT_FILE = os.path.join(_OUTPUT_DIR, "backloggd-games.json")
REQUEST_TIMEOUT = 10

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
}


def extract_games_from_html(
    html: str, only_rated: bool = False
) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    selector = "div.game-cover.user-rating" if only_rated else "div.game-cover"
    cards = soup.select(selector)
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


def scrape_user_games(username: str, only_rated: bool = False) -> list[dict[str, str]]:
    session = requests.Session()
    session.headers.update(HEADERS)

    all_games: list[dict[str, str]] = []
    previous_titles: list[str] | None = None
    page = 1

    while True:
        url = f"{BASE_URL.format(username=username)}?page={page}"
        print(f"Fetching page {page}: {url}")

        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}", file=sys.stderr)
            break

        if response.status_code != 200:
            print(
                f"Error: received status {response.status_code} for page {page}",
                file=sys.stderr,
            )
            if page == 1:
                print(
                    "Could not access the profile. Check the username and "
                    "ensure backloggd.com is accessible.",
                    file=sys.stderr,
                )
            break

        page_games = extract_games_from_html(response.text, only_rated=only_rated)

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

    return all_games


class ScraperWindow(QWidget):
    _scrape_finished = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Backloggd Scraper Tool")
        self.setFixedSize(380, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Backloggd Scraper Tool")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        input_row = QHBoxLayout()
        label = QLabel("Username:")
        label.setStyleSheet("font-size: 14px;")
        input_row.addWidget(label)
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("font-size: 14px;")
        self.username_input.returnPressed.connect(self._on_submit)
        input_row.addWidget(self.username_input)
        layout.addLayout(input_row)

        self.only_rated_checkbox = QCheckBox("Only Rated Games")
        self.only_rated_checkbox.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.only_rated_checkbox)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet("font-size: 14px;")
        self.submit_btn.clicked.connect(self._on_submit)
        layout.addWidget(self.submit_btn)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self._scrape_finished.connect(self._on_scrape_done)

    def _on_submit(self) -> None:
        username = self.username_input.text().strip()
        if not username:
            self._set_status("Please enter a username.", "red")
            return

        self.submit_btn.setEnabled(False)
        self._set_status("Scraping...", "black")

        only_rated = self.only_rated_checkbox.isChecked()

        def run_scrape() -> None:
            games = scrape_user_games(username, only_rated=only_rated)
            if not games:
                self._scrape_finished.emit(
                    "No games found. Check the username.",
                    "red",
                )
            else:
                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(games, f, indent=2, ensure_ascii=False)
                self._scrape_finished.emit(
                    f"Saved {len(games)} games to {OUTPUT_FILE}",
                    "green",
                )

        threading.Thread(target=run_scrape, daemon=True).start()

    def _on_scrape_done(self, message: str, color: str) -> None:
        self._set_status(message, color)
        self.submit_btn.setEnabled(True)

    def _set_status(self, text: str, color: str) -> None:
        self.status_label.setStyleSheet(f"font-size: 13px; color: {color};")
        self.status_label.setText(text)


def main() -> None:
    app = QApplication(sys.argv)
    window = ScraperWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
