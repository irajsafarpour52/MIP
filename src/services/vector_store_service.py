import chromadb

from embedding_service import create_embedding


# مسیر ذخیره Vector Database
DB_PATH = r"D:\MIP\data\chroma"


# اتصال به ChromaDB
client = chromadb.PersistentClient(
    path=DB_PATH
)


# دریافت یا ایجاد Collection
collection = client.get_or_create_collection(
    name="mip_meetings"
)


def add_chunk(chunk_id: str, chunk: dict):
    """
    ذخیره یک Chunk به همراه:
    - متن
    - Embedding
    - Metadata

    در ChromaDB
    """

    text = chunk.get(
        "content",
        ""
    )

    metadata = chunk.get(
        "metadata",
        {}
    ).copy()

    chunk_type = chunk.get(
        "type",
        "unknown"
    )

    # نوع Chunk را نیز به Metadata اضافه می‌کنیم.
    metadata["type"] = chunk_type

    if not text:
        return

    # ساخت Embedding فقط از متن Chunk
    vector = create_embedding(
        text
    )

    # ذخیره در ChromaDB
    collection.add(
        ids=[chunk_id],

        embeddings=[
            vector.tolist()
        ],

        documents=[
            text
        ],

        metadatas=[
            metadata
        ]
    )


def get_chunk(chunk_id: str):
    """
    دریافت یک Chunk بر اساس ID.
    """

    result = collection.get(
        ids=[chunk_id]
    )

    return result


if __name__ == "__main__":

    print(
        "Vector Store Service Test..."
    )

    # یک Chunk واقعی مشابه خروجی Chunker
    test_chunk = {
        "type": "task",

        "content": """
- بررسی کیفیت خروجی Whisper
- مسئول: من
""",

        "metadata": {
            "meeting_date": "2026-08-09",
            "meeting_title": "بررسی پروژه MIP",
            "project": "MIP",
            "participants": "من، علی، رضا"
        }
    }

    add_chunk(
        chunk_id="meeting_20260809_task_02",
        chunk=test_chunk
    )

    print(
        "\nChunk stored successfully."
    )

    result = get_chunk(
        "meeting_20260809_task_02"
    )

    print(
        "\n===== STORED CHUNK ====="
    )

    print(result)