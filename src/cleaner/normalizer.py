import re


def normalize_text(text: str) -> str:
    """
    نرمال سازی متن خروجی Whisper
    """

    # 1- تبدیل حروف عربی به فارسی
    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)


    # 2- حذف فاصله‌های اضافی
    text = re.sub(
        r"\s+",
        " ",
        text
    )


    # 3- حذف فاصله قبل از علائم
    text = re.sub(
        r"\s+([،؛؟.!])",
        r"\1",
        text
    )


    # 4- اصلاح فاصله‌های رایج
    fixes = {
        "ام روز": "امروز",
        "می شود": "می‌شود",
        "نمی شود": "نمی‌شود",
        "به  روز": "به‌روز"
    }

    for wrong, correct in fixes.items():
        text = text.replace(
            wrong,
            correct
        )


    # 5- حذف فاصله ابتدا و انتها
    text = text.strip()


    return text


if __name__ == "__main__":

    sample = """
    سلام  ام روز جلسه  بررسی پروژه  می شود
    """

    result = normalize_text(sample)

    print(result)