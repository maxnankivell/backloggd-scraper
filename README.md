# Backloggd Scraper

A scraper for [Backloggd](https://www.backloggd.com/).

## Install

Download the latest executable for your platform from the
[Releases](../../releases) page.

### macOS

```bash
chmod +x backloggd-scraper-macos
xattr -d com.apple.quarantine backloggd-scraper-macos
./backloggd-scraper-macos
```

The `xattr` command removes the quarantine flag that macOS applies to downloaded
files. Without it, Gatekeeper will block the unsigned binary. Alternatively, you
can go to **System Settings > Privacy & Security** after the first blocked
attempt and click **Allow Anyway**.

### Windows

Run `backloggd-scraper-windows.exe` directly — no extra steps needed.

If Windows Defender SmartScreen shows a warning, click **More info** then
**Run anyway**.

### Linux

```bash
chmod +x backloggd-scraper-linux
./backloggd-scraper-linux
```

## Building from source

### Prerequisites

- [Python 3.12+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/)

### Setup

Clone the repository, then run:

```bash
cd backloggd-scraper
uv sync
```

### Usage

```bash
uv run python main.py
```

## Development

### Linting

```bash
uv run ruff check .
uv run ruff check --fix .
```

### Formatting

```bash
uv run ruff format --check .
uv run ruff format .
```

### Type Checking

```bash
uv run ty check
```
