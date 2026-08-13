import re


def clean_text(text: str) -> str:
    """
    پاکسازی اولیه متن خروجی Whisper
    """

    replacements = {
        "نوزخه": "نسخه",
        "ام روز": "امروز",
        "دو هفت": "دو هفته",
        "شبکت": "شبکه",
        "میتینگ": "جلسه",
        "پرگاهی": "پروژه",
        "دیتاویس": "دیتابیس" 
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    # حذف فاصله‌های اضافی
    text = re.sub(r"\s+", " ", text)

    return text.strip()