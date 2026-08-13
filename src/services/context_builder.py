def build_context(results: list) -> str:
    """
    ساخت Context متنی از نتایج Retrieval.

    این سرویس فقط نتایج پیدا شده را
    به یک متن منظم تبدیل می‌کند.
    """

    if not results:
        return ""

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):

        document = result.get(
            "document",
            ""
        )

        metadata = result.get(
            "metadata",
            {}
        )

        chunk_type = metadata.get(
            "type",
            "unknown"
        )

        meeting_date = metadata.get(
            "meeting_date",
            "unknown"
        )

        context_parts.append(
            f"""
[Context {index}]
Type: {chunk_type}
Meeting Date: {meeting_date}

{document}
""".strip()
        )

    return "\n\n".join(
        context_parts
    )


if __name__ == "__main__":

    print("Context Builder Test...")

    test_results = [
        {
            "id": "meeting_20260809_task_01",
            "distance": 17.2226,
            "metadata": {
                "type": "task",
                "meeting_date": "2026-08-09"
            },
            "document": """
بررسی کیفیت خروجی Whisper
- مسئول: من
"""
        }
    ]

    context = build_context(
        test_results
    )

    print("\n===== GENERATED CONTEXT =====")
    print(context)