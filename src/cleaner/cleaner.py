from normalizer import normalize_text
from phrase_corrector import correct_phrases


def clean_text(text: str) -> str:
    """
    موتور اصلی پاکسازی متن Whisper
    """

    if not text:
        return text

    print("Cleaner started...")

    # مرحله 1: نرمال سازی
    text = normalize_text(text)

    # مرحله 2: اصلاح عبارت‌ها
    text = correct_phrases(text)

    print("Cleaner completed.")

    return text


if __name__ == "__main__":

    sample_text = """
    سلام  ام روز جلسه درباره ام وی پی
    و ای پی آی اولاما بود.
    تیم گیت هاب را بررسی کرد.
    """

    result = clean_text(sample_text)

    print("\n===== CLEAN RESULT =====")
    print(result)