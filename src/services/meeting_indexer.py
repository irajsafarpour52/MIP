from pathlib import Path

from document_loader import load_markdown
from document_chunker import chunk_markdown
from vector_store_service import add_chunk


# مسیر پوشه جلسات
MEETINGS_PATH = Path(
    r"D:\MIP\data\meetings"
)


def index_meeting_file(file_path: Path):
    """
    خواندن، Chunk کردن و ذخیره
    یک فایل صورتجلسه در ChromaDB.
    """

    print(f"\nIndexing: {file_path.name}")

    # مرحله 1: خواندن Markdown
    markdown_text = load_markdown(
        str(file_path)
    )

    # مرحله 2: ساخت Chunk
    chunks = chunk_markdown(
        markdown_text
    )

    print(
        f"Chunks found: {len(chunks)}"
    )

    # شناسه پایه جلسه
    meeting_id = file_path.stem

    # مرحله 3: ذخیره هر Chunk
    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        chunk_type = chunk.get(
            "type",
            "unknown"
        )

        # ساخت ID یکتا
        chunk_id = (
            f"{meeting_id}_"
            f"{chunk_type}_"
            f"{index:02d}"
        )

        add_chunk(
            chunk_id=chunk_id,
            chunk=chunk
        )

        print(
            f"Stored: {chunk_id}"
        )


def index_all_meetings():
    """
    پیدا کردن تمام فایل‌های Markdown
    جلسات و Index کردن آنها.
    """

    if not MEETINGS_PATH.exists():
        raise FileNotFoundError(
            f"Meetings folder not found: "
            f"{MEETINGS_PATH}"
        )

    files = sorted(
        MEETINGS_PATH.rglob("*.md")
    )

    if not files:
        print(
            "No Markdown meeting files found."
        )
        return

    print(
        f"Found {len(files)} meeting file(s)."
    )

    for file_path in files:
        index_meeting_file(
            file_path
        )


if __name__ == "__main__":

    print(
        "MIP Meeting Indexer Test..."
    )

    index_all_meetings()

    print(
        "\n===== INDEXING COMPLETED ====="
    )