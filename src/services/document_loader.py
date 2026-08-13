from pathlib import Path


def load_markdown(file_path: str) -> str:
    """
    خواندن محتوای یک فایل Markdown و برگرداندن آن به صورت متن.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Markdown file not found: {file_path}"
        )

    return path.read_text(
        encoding="utf-8"
    )


if __name__ == "__main__":

    print("Markdown Document Loader Test...")

    file_path = r"D:\MIP\data\meetings\2026\meeting_20260809.md"

    content = load_markdown(file_path)

    print("\n===== MARKDOWN CONTENT =====")
    print(content)