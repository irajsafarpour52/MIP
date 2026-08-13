import chromadb


# مسیر ذخیره Vector Database
DB_PATH = r"D:\MIP\data\chroma"


# اتصال به ChromaDB
client = chromadb.PersistentClient(
    path=DB_PATH
)


# دریافت Collection
collection = client.get_or_create_collection(
    name="mip_meetings"
)


def test_vector_store():
    """
    نمایش اطلاعات ذخیره‌شده در ChromaDB.
    """

    result = collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    ids = result.get(
        "ids",
        []
    )

    documents = result.get(
        "documents",
        []
    )

    metadatas = result.get(
        "metadatas",
        []
    )

    print(
        f"\nChunks stored: {len(ids)}"
    )

    for index in range(
        len(ids)
    ):

        print(
            "\n=============================="
        )

        print(
            f"CHUNK {index + 1}"
        )

        print(
            "=============================="
        )

        print(
            f"ID: {ids[index]}"
        )

        print(
            "\nMETADATA:"
        )

        print(
            metadatas[index]
        )

        print(
            "\nDOCUMENT:"
        )

        print(
            documents[index]
        )


def delete_test_chunks():
    """
    حذف Chunkهای آزمایشی قبلی.
    """

    test_ids = [
        "meeting_20260809_task_01",
        "meeting_20260809_task_02"
    ]

    collection.delete(
        ids=test_ids
    )

    print(
        "\nTest chunks deleted."
    )

if __name__ == "__main__":
  
    print(
        "Vector Store Cleanup Test..."
    )

    delete_test_chunks()

    print(
        "\n===== CLEANUP COMPLETED ====="
    )

    print(
        "Vector Store Verification Test..."
    )

    test_vector_store()

    print(
        "\n===== TEST COMPLETED ====="
    )