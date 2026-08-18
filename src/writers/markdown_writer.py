from datetime import datetime


def write_markdown(
    meeting_data: dict,
    output_file: str
):
    """
    تبدیل نتیجه تحلیل جلسه به فایل Markdown.

    خروجی شامل:

        - خلاصه جلسه
        - Tags
        - تصمیمات
        - وظایف

    Tags از Tag Suggestion Service دریافت می‌شوند.
    """

    # ========================================================
    # ساخت محتوای اصلی گزارش جلسه
    # ========================================================

    content = f"""
# گزارش جلسه MIP

تاریخ: {datetime.now().strftime("%Y-%m-%d")}


## خلاصه جلسه

{meeting_data.get("summary", "")}


## برچسب‌ها

"""

    # ========================================================
    # نوشتن Tags
    # ========================================================

    tags = meeting_data.get(
        "tags",
        []
    )

    if tags:

        for tag in tags:

            # ساختار استاندارد Tag:
            #
            # {
            #     "tag": "MVP",
            #     "category": "product",
            #     "score": 2
            # }

            if isinstance(
                tag,
                dict
            ):

                tag_name = tag.get(
                    "tag",
                    ""
                )

            else:

                tag_name = str(tag)


            if tag_name:

                content += (
                    f"- {tag_name}\n"
                )

    else:

        content += (
            "- برچسبی شناسایی نشد.\n"
        )


    # ========================================================
    # تصمیمات
    # ========================================================

    content += """

## تصمیمات

"""

    decisions = meeting_data.get(
        "decisions",
        []
    )

    if decisions:

        for item in decisions:

            content += (
                f"- {item}\n"
            )

    else:

        content += (
            "- تصمیمی ثبت نشده است.\n"
        )


    # ========================================================
    # وظایف
    # ========================================================

    content += """

## وظایف

"""

    tasks = meeting_data.get(
        "tasks",
        []
    )

    if tasks:

        for task in tasks:

            if isinstance(
                task,
                dict
            ):

                task_text = task.get(
                    "task",
                    ""
                )

                assignee = task.get(
                    "assignee"
                )

                deadline = task.get(
                    "deadline"
                )

                content += (
                    f"- {task_text}\n"
                )

                if assignee:

                    content += (
                        f"  - مسئول: {assignee}\n"
                    )

                if deadline:

                    content += (
                        f"  - مهلت: {deadline}\n"
                    )

            else:

                content += (
                    f"- {task}\n"
                )


    else:

        content += (
            "- وظیفه‌ای ثبت نشده است.\n"
        )


    # ========================================================
    # ذخیره گزارش در فایل Markdown
    # ========================================================

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            content
        )


# ============================================================
# تست مستقیم فایل
# ============================================================

if __name__ == "__main__":

    print(
        "Markdown writer service"
    )