from retrieval_service import search_chunks
from context_builder import build_context
from gapgpt_services import generate_text


def ask_rag(question: str) -> str:
    """
    دریافت سؤال و تولید پاسخ با استفاده از
    اطلاعات بازیابی‌شده از Vector Database.
    """

    if not question:
        return ""

    # مرحله 1: جستجوی معنایی
    results = search_chunks(
        question,
        top_k=3
    )

    if not results:
        return "اطلاعات مرتبطی در جلسات پیدا نشد."

    # مرحله 2: ساخت Context
    context = build_context(
        results
    )

    # مرحله 3: ساخت Prompt برای LLM
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

    # مرحله 4: ارسال Context و سؤال به GapGPT
    response = generate_text(
        prompt
    )

    return response.strip()


if __name__ == "__main__":

    print("RAG Service Test...")

    question = input(
        "\nEnter your question: "
    )

    answer = ask_rag(
        question
    )

    print("\n===== RAG ANSWER =====")
    print(answer)