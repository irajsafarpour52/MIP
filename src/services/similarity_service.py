from embedding_service import create_embedding
import numpy as np


def calculate_similarity(text1: str, text2: str) -> float:
    """
    محاسبه شباهت معنایی بین دو متن با استفاده از
    Cosine Similarity روی Embeddingها.
    """

    if not text1 or not text2:
        return 0.0

    vector1 = create_embedding(text1)
    vector2 = create_embedding(text2)

    vector1 = np.array(vector1)
    vector2 = np.array(vector2)
    # شباهت کسینوسی
    similarity = np.dot(vector1, vector2) / (
        np.linalg.norm(vector1) * np.linalg.norm(vector2)
    )

    return float(similarity)


if __name__ == "__main__":

    print("Semantic Similarity Test...")

    text1 = "بررسی کیفیت خروجی Whisper"

    text2 = "ارزیابی دقت متن تولیدشده توسط Whisper"

    text3 = "خرید مواد اولیه کارخانه"

    similarity_1_2 = calculate_similarity(
        text1,
        text2
    )

    similarity_1_3 = calculate_similarity(
        text1,
        text3
    )

    print("\n===== SIMILARITY RESULTS =====")

    print(
        f"Text 1 <-> Text 2: {similarity_1_2:.4f}"
    )

    print(
        f"Text 1 <-> Text 3: {similarity_1_3:.4f}"
    )