from document_loader import load_markdown


def chunk_markdown(markdown_text: str) -> list[dict]:
    """
    تقسیم گزارش جلسه به Chunkهای منطقی.

    ساختار Chunkها:

    document
    summary
    decision
    task

    اطلاعات زیرمجموعه Task مثل مسئول
    داخل همان Chunk مربوط به Task باقی می‌مانند.

    Metadata جلسه نیز به تمام Chunkها اضافه می‌شود.
    """

    if not markdown_text:
        return []

    lines = markdown_text.splitlines()

    chunks = []

    # -----------------------------------
    # استخراج Metadata جلسه
    # -----------------------------------

    meeting_metadata = {
        "meeting_date": "",
        "meeting_title": "",
        "project": "",
        "participants": ""
    }

    for raw_line in lines:

        line = raw_line.strip()

        if line.startswith("تاریخ:"):
            meeting_metadata["meeting_date"] = (
                line.split(":", 1)[1].strip()
            )

        elif line.startswith("عنوان:"):
            meeting_metadata["meeting_title"] = (
                line.split(":", 1)[1].strip()
            )

        elif line.startswith("پروژه:"):
            meeting_metadata["project"] = (
                line.split(":", 1)[1].strip()
            )

        elif line.startswith("شرکت‌کنندگان:"):
            meeting_metadata["participants"] = (
                line.split(":", 1)[1].strip()
            )

    # -----------------------------------
    # ساخت Chunk
    # -----------------------------------

    current_section = None
    current_content = []

    def add_chunk(
        chunk_type: str,
        content: list[str]
    ):
        text = "\n".join(content).strip()

        if text:

            chunks.append(
                {
                    "type": chunk_type,
                    "content": text,
                    "metadata": meeting_metadata.copy()
                }
            )

    for raw_line in lines:

        # فاصله‌های انتهای خط را حذف می‌کنیم
        # ولی تورفتگی ابتدای خط را حفظ می‌کنیم.
        line = raw_line.rstrip()

        # خط بدون فاصله برای تشخیص عنوان
        clean_line = line.strip()

        # -----------------------------------
        # عنوان اصلی
        # -----------------------------------

        if clean_line.startswith("# ") and not clean_line.startswith("## "):

            if current_content:

                add_chunk(
                    current_section or "document",
                    current_content
                )

                current_content = []

            current_section = "document"

            current_content.append(
                clean_line
            )

        # -----------------------------------
        # خلاصه جلسه
        # -----------------------------------

        elif clean_line == "## خلاصه جلسه":

            if current_content:

                add_chunk(
                    current_section or "document",
                    current_content
                )

                current_content = []

            current_section = "summary"

            current_content.append(
                clean_line
            )

        # -----------------------------------
        # تصمیمات
        # -----------------------------------

        elif clean_line == "## تصمیمات":

            if current_content:

                add_chunk(
                    current_section or "document",
                    current_content
                )

                current_content = []

            current_section = "decision"

        # -----------------------------------
        # وظایف
        # -----------------------------------

        elif clean_line == "## وظایف":

            if current_content:

                add_chunk(
                    current_section or "document",
                    current_content
                )

                current_content = []

            current_section = "task"

        # -----------------------------------
        # تصمیم جدید
        # -----------------------------------
        elif (
            current_section == "decision"
            and line.startswith("- ")
        ):

            if current_content:

                add_chunk(
                    "decision",
                    current_content
                )

            current_content = [
                line.strip()
            ]

        # -----------------------------------
        # Task جدید
        # -----------------------------------

        elif (
            current_section == "task"
            and line.startswith("- ")
        ):

            if current_content:

                add_chunk(
                    "task",
                    current_content
                )

            current_content = [
                line.strip()
            ]

        # -----------------------------------
        # اطلاعات زیرمجموعه Task
        # -----------------------------------

        elif (
            current_section == "task"
            and line.startswith("  - ")
        ):

            current_content.append(
                line.strip()
            )

        # -----------------------------------
        # سایر خطوط
        # -----------------------------------

        elif clean_line:

            current_content.append(
                clean_line
            )

    # -----------------------------------
    # آخرین Chunk
    # -----------------------------------

    if current_content:

        add_chunk(
            current_section or "document",
            current_content
        )

    return chunks


# ---------------------------------------
# Test
# ---------------------------------------

if __name__ == "__main__":

    print("Markdown Chunker Test...")

    file_path = (
        r"D:\MIP\data\meetings\2026"
        r"\meeting_20260809.md"
    )

    markdown_text = load_markdown(
        file_path
    )

    chunks = chunk_markdown(
        markdown_text
    )

    print(
        f"\nChunks found: {len(chunks)}"
    )

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"\n===== CHUNK {index} ====="
        )

        print(
            f"TYPE: {chunk['type']}"
        )

        print(
            "METADATA:"
        )

        print(
            f"  meeting_date: "
            f"{chunk['metadata']['meeting_date']}"
        )

        print(
            f"  meeting_title: "
            f"{chunk['metadata']['meeting_title']}"
        )

        print(
            f"  project: "
            f"{chunk['metadata']['project']}"
        )

        print(
            f"  participants: "
            f"{chunk['metadata']['participants']}"
        )

        print(
            "\nCONTENT:"
        )

        print(
            chunk["content"]
        )