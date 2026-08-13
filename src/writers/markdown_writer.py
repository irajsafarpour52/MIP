from datetime import datetime


def write_markdown(meeting_data: dict, output_file: str):

    # ساخت محتوای اصلی گزارش جلسه
    content = f"""
# گزارش جلسه MIP

تاریخ: {datetime.now().strftime("%Y-%m-%d")}


## خلاصه جلسه

{meeting_data.get("summary", "")}


## تصمیمات

"""

    # نوشتن تصمیمات جلسه
    decisions = meeting_data.get("decisions", [])

    if decisions:
        for item in decisions:
            content += f"- {item}\n"
    else:
        content += "- تصمیمی ثبت نشده است.\n"


    # نوشتن وظایف جلسه
    content += """

## وظایف

"""

    tasks = meeting_data.get("tasks", [])

    if tasks:
        for task in tasks:

            if isinstance(task, dict):

                task_text = task.get("task", "")
                assignee = task.get("assignee")
                deadline = task.get("deadline")

                content += f"- {task_text}\n"

                if assignee:
                    content += f"  - مسئول: {assignee}\n"

                if deadline:
                    content += f"  - مهلت: {deadline}\n"

            else:
                content += f"- {task}\n"

    else:
        content += "- وظیفه‌ای ثبت نشده است.\n"


    # ذخیره گزارش در فایل Markdown
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(content)


# فقط برای تست مستقیم فایل
if __name__ == "__main__":

    print("Markdown writer service")