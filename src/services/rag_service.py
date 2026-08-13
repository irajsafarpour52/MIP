from retrieval_service import search_chunks
from context_builder import build_context
from gapgpt_services import generate_text


def ask_rag(question: str) -> dict:
    """
    دریافت سؤال و تولید پاسخ RAG
    به همراه بهترین Evidence از Vector Database.
    """

    if not question:
        return {
            "answer": "",
            "evidence": None
        }

    # -----------------------------------
    # مرحله 1: جستجوی معنایی
    # -----------------------------------

    results = search_chunks(
        question,
        top_k=3
    )

    if not results:

        return {
            "answer": "اطلاعات مرتبطی در جلسات پیدا نشد.",
            "evidence": None
        }

    # -----------------------------------
    # مرحله 2: ساخت Context
    # -----------------------------------

    context = build_context(
        results
    )

    # -----------------------------------
    # مرحله 3: ساخت Prompt برای LLM
    # -----------------------------------

    prompt = f"""
تو دستیار هوشمند مدیریت جلسات MIP هستی.

فقط بر اساس اطلاعات موجود در Context پاسخ بده.

اگر پاسخ سؤال در Context وجود ندارد،
صریحاً بگو که اطلاعات کافی در جلسات پیدا نشد.

اطلاعات Context:
--------------------

{context}

--------------------

سؤال کاربر:
{question}

پاسخ:
"""

    # -----------------------------------
    # مرحله 4: ارسال Context و سؤال به LLM
    # -----------------------------------

    response = generate_text(
        prompt
    )

    # -----------------------------------
    # مرحله 5: انتخاب بهترین Evidence
    # -----------------------------------

    best_result = min(
        results,
        key=lambda item: item.get(
            "distance",
            float("inf")
        )
    )

    evidence = {
        "chunk_id": best_result.get(
            "id",
            ""
        ),

        "distance": best_result.get(
            "distance",
            None
        ),

        "metadata": best_result.get(
            "metadata",
            {}
        ),

        "document": best_result.get(
            "document",
            ""
        )
    }

    # -----------------------------------
    # خروجی نهایی
    # -----------------------------------

    return {
        "answer": response.strip(),
        "evidence": evidence
    }


# ---------------------------------------
# Test
# ---------------------------------------

if __name__ == "__main__":

    print(
        "RAG Service Test..."
    )

    question = input(
        "\nEnter your question: "
    )

    result = ask_rag(
        question
    )

    # -----------------------------------
    # نمایش پاسخ
    # -----------------------------------

    print(
        "\n===== RAG ANSWER ====="
    )

    print(
        result["answer"]
    )

    # -----------------------------------
    # نمایش Evidence
    # -----------------------------------

    print(
        "\n===== EVIDENCE ====="
    )

    evidence = result["evidence"]

    if not evidence:

        print(
            "No evidence found."
        )

    else:

        print(
            "\n--- Evidence ---"
        )

        print(
            f"Chunk ID: "
            f"{evidence['chunk_id']}"
        )

        print(
            f"Distance: "
            f"{evidence['distance']:.4f}"
        )

        metadata = evidence["metadata"]

        print(
            f"Meeting: "
            f"{metadata.get('meeting_title', 'unknown')}"
        )

        print(
            f"Date: "
            f"{metadata.get('meeting_date', 'unknown')}"
        )

        print(
            f"Type: "
            f"{metadata.get('type', 'unknown')}"
        )

        print(
            "\nSource:"
        )

        print(
            evidence["document"]
        )