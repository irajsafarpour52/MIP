from datetime import datetime


def write_markdown(meeting_data: dict, output_file: str):

    content = f"""
# گزارش جلسه MIP

تاریخ: {datetime.now().strftime("%Y-%m-%d")}


## خلاصه جلسه

{meeting_data.get("summary", "")}


## تصمیمات

"""

    decisions = meeting_data.get("decisions", [])

    if decisions:
        for item in decisions:
            content += f"- {item}\n"
    else:
        content += "- تصمیمی ثبت نشده است.\n"


    content += """

## وظایف

"""

    tasks = meeting_data.get("tasks", [])

    if tasks:
        for task in tasks:
            if isinstance(task, dict):
                content += f"- {task.get('task_name','')} : {task.get('description','')}\n"
            else:
                content += f"- {task}\n"
    else:
        content += "- وظیفه‌ای ثبت نشده است.\n"


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(content)


if __name__ == "__main__":
    print("Markdown writer service")