import chromadb

from embedding_service import create_embedding


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


def search_chunks(
    question: str,
    top_k: int = 3,
    max_distance: float = 20.0,
    metadata_filter: dict | None = None
):
    """
    جستجوی معنایی در بین Chunkها.

    در صورت وجود metadata_filter،
    ابتدا محدوده جستجو بر اساس Metadata
    محدود می‌شود.
    """

    if not question:
        return []

    # -----------------------------------
    # ساخت Embedding سؤال
    # -----------------------------------

    query_vector = create_embedding(
        question
    )

    # -----------------------------------
    # ساخت پارامترهای Query
    # -----------------------------------

    query_parameters = {
        "query_embeddings": [
            query_vector.tolist()
        ],

        "n_results": top_k
    }

    # -----------------------------------
    # اضافه کردن Metadata Filter
    # -----------------------------------

    if metadata_filter:

        query_parameters[
            "where"
        ] = metadata_filter

    # -----------------------------------
    # جستجو در ChromaDB
    # -----------------------------------

    results = collection.query(
        **query_parameters
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    ids = results.get(
        "ids",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    # -----------------------------------
    # اعمال Distance Filter
    # -----------------------------------

    filtered_results = []

    for i in range(
        len(documents)
    ):

        if distances[i] <= max_distance:

            filtered_results.append(
                {
                    "id": ids[i],
                    "distance": distances[i],
                    "metadata": metadatas[i],
                    "document": documents[i]
                }
            )
            
    return filtered_results


if __name__ == "__main__":

    print(
        "Retrieval Service Test..."
    )

    # -----------------------------------
    # سؤال آزمایشی
    # -----------------------------------

    question = input(
        "\nEnter your question: "
    )

    # -----------------------------------
    # فیلتر Metadata
    # -----------------------------------

    metadata_filter = {
        "type": "task"
    }

    # -----------------------------------
    # جستجو
    # -----------------------------------

    results = search_chunks(
        question=question,
        top_k=3,
        max_distance=20.0,
        metadata_filter=metadata_filter
    )

    print(
        "\n===== SEARCH RESULTS ====="
    )

    if not results:

        print(
            "No relevant information found."
        )

    else:

        for i, result in enumerate(
            results,
            start=1
        ):

            print(
                f"\n--- Result {i} ---"
            )

            print(
                f"ID: {result['id']}"
            )

            print(
                f"Distance: "
                f"{result['distance']:.4f}"
            )

            print(
                f"Metadata: "
                f"{result['metadata']}"
            )

            print(
                f"Document: "
                f"{result['document']}"
            )