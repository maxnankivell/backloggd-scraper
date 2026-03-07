import prettyprinter


def main() -> None:
    prettyprinter.install_extras(include=["dataclasses"])

    sample_data = {
        "project": "backloggd-scraper",
        "status": "setup complete",
        "tools": ["ruff", "ty", "prettyprinter"],
        "python_version": "3.12",
    }
    prettyprinter.cpprint(sample_data)


if __name__ == "__main__":
    main()
