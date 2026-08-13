from sentence_transformers import SentenceTransformer


print("Loading embedding model...")

model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)

print("Embedding model loaded successfully")


def create_embedding(text: str):

    if not text:
        return []

    vector = model.encode(text)

    return vector


if __name__ == "__main__":

    print("Embedding Service Test...")

    test_text = """
    بررسی کیفیت خروجی Whisper
    مسئول: من
    """

    vector = create_embedding(test_text)

    print("\n===== EMBEDDING RESULT =====")
    print(f"Vector dimensions: {len(vector)}")

    print("\nFirst 10 values:")
    print(vector[:10])