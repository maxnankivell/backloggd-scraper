# Backloggd Scraper

A scraper for [Backloggd](https://www.backloggd.com/).

## Prerequisites

- [Python 3.12+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/)

## Setup

Clone the repository, then run:

```bash
cd backloggd-scraper
uv sync
```

## Usage

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
