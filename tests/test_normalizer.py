"""
MIP - Normalizer Tests

هدف:
    تست مستقل رفتار Normalizer قبل از اتصال آن
    به Pipeline اصلی MIP.

اصل مهم:
    فقط Aliasهایی که normalize=True دارند
    باید در متن تغییر کنند.

Aliasهایی که normalize=False هستند،
نباید متن را تغییر دهند.
"""

from pathlib import Path
import sys


# ============================================================
# آماده‌سازی مسیر پروژه
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# اضافه کردن ریشه پروژه به Python Path
# تا بتوانیم normalizer را مستقیماً import کنیم.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.services.normalizer import VocabularyNormalizer


# ============================================================
# ایجاد Normalizer
# ============================================================

def create_normalizer():
    """
    یک نمونه از VocabularyNormalizer ایجاد می‌کند.

    تمام تست‌ها از همین Vocabulary استفاده می‌کنند.
    """

    return VocabularyNormalizer()


# ============================================================
# تست MVP
# ============================================================

def test_mvp_normalization():
    """
    ام وی پی باید به MVP تبدیل شود.
    """

    normalizer = create_normalizer()

    text = "ام وی پی باید آماده شود."

    result = normalizer.normalize(text)

    assert result == "MVP باید آماده شود."


# ============================================================
# تست شکل دیگر MVP
# ============================================================

def test_mvp_half_space_normalization():
    """
    ام‌وی‌پی نیز باید به MVP تبدیل شود.
    """

    normalizer = create_normalizer()

    text = "ام‌وی‌پی اولیه آماده شد."

    result = normalizer.normalize(text)

    assert result == "MVP اولیه آماده شد."


# ============================================================
# تست FastAPI
# ============================================================

def test_fastapi_normalization():
    """
    فست ای پی باید به FastAPI تبدیل شود.
    """

    normalizer = create_normalizer()

    text = "این سرویس با فست ای پی ساخته شده است."

    result = normalizer.normalize(text)

    assert result == "این سرویس با FastAPI ساخته شده است."


# ============================================================
# تست Whisper
# ============================================================

def test_whisper_normalization():
    """
    شکل گفتاری ویس پر باید به Whisper تبدیل شود.
    """

    normalizer = create_normalizer()

    text = "ویس پر برای تبدیل صوت استفاده می‌شود."

    result = normalizer.normalize(text)

    assert result == "Whisper برای تبدیل صوت استفاده می‌شود."


# ============================================================
# تست Feature
# ============================================================

def test_feature_normalization():
    """
    فیچر باید به Feature تبدیل شود.
    """

    normalizer = create_normalizer()

    text = "فیچر جدید محصول بررسی شد."

    result = normalizer.normalize(text)

    assert result == "Feature جدید محصول بررسی شد."


# ============================================================
# تست Aliasهایی که نباید Normalize شوند
# ============================================================

def test_non_normalized_alias():
    """
    قابلیت و ویژگی فعلاً فقط Aliasهای قابل جستجو هستند
    و نباید در متن به Feature تبدیل شوند.
    """

    normalizer = create_normalizer()

    text = "قابلیت و ویژگی جدید محصول بررسی شد."

    result = normalizer.normalize(text)

    assert result == text


# ============================================================
# تست چند اصطلاح در یک جمله
# ============================================================

def test_multiple_terms():
    """
    چند اصطلاح تخصصی در یک جمله باید همزمان Normalize شوند.
    """

    normalizer = create_normalizer()

    text = (
        "ام وی پی با فست ای پی ساخته شد "
        "و ویس پر برای تبدیل صوت استفاده شد."
    )

    result = normalizer.normalize(text)

    expected = (
        "MVP با FastAPI ساخته شد "
        "و Whisper برای تبدیل صوت استفاده شد."
    )

    assert result == expected


# ============================================================
# تست چند خطی
# ============================================================

def test_multiline_text():
    """
    Normalizer باید روی متن چندخطی نیز درست عمل کند.
    """

    normalizer = create_normalizer()

    text = """جلسه درباره ام وی پی بود.
فیچر جدید بررسی شد.
فست ای پی برای Backend انتخاب شد."""

    result = normalizer.normalize(text)

    expected = """جلسه درباره MVP بود.
Feature جدید بررسی شد.
FastAPI برای Backend انتخاب شد."""

    assert result == expected


# ============================================================
# تست متن معمولی
# ============================================================

def test_normal_text_remains_unchanged():
    """
    اگر متن شامل Alias قابل Normalization نباشد،
    نباید تغییری کند.
    """

    normalizer = create_normalizer()

    text = (
        "امروز درباره برنامه جلسه آینده و "
        "وظایف تیم صحبت کردیم."
    )

    result = normalizer.normalize(text)

    assert result == text


# ============================================================
# تست رشته خالی
# ============================================================

def test_empty_text():
    """
    رشته خالی باید بدون خطا همان رشته خالی باقی بماند.
    """

    normalizer = create_normalizer()

    result = normalizer.normalize("")

    assert result == ""


# ============================================================
# تست نوع ورودی
# ============================================================

def test_invalid_input_type():
    """
    ورودی غیرمتنی باید TypeError ایجاد کند.
    """

    normalizer = create_normalizer()

    try:

        normalizer.normalize(None)

        # اگر به اینجا رسیدیم یعنی خطا ایجاد نشده.
        assert False, "Expected TypeError"

    except TypeError:

        # رفتار مورد انتظار
        assert True


# ============================================================
# اجرای مستقیم تست‌ها
# ============================================================

if __name__ == "__main__":

    print("===================================")
    print(" MIP Normalizer Test")
    print("===================================")

    try:

        test_mvp_normalization()
        print("✓ MVP normalization: OK")

        test_mvp_half_space_normalization()
        print("✓ MVP half-space normalization: OK")

        test_fastapi_normalization()
        print("✓ FastAPI normalization: OK")

        test_whisper_normalization()
        print("✓ Whisper normalization: OK")

        test_feature_normalization()
        print("✓ Feature normalization: OK")

        test_non_normalized_alias()
        print("✓ Non-normalized aliases: OK")

        test_multiple_terms()
        print("✓ Multiple terms: OK")

        test_multiline_text()
        print("✓ Multiline text: OK")

        test_normal_text_remains_unchanged()
        print("✓ Normal text preservation: OK")

        test_empty_text()
        print("✓ Empty text: OK")

        test_invalid_input_type()
        print("✓ Invalid input handling: OK")

        print()
        print("===================================")
        print(" ALL NORMALIZER TESTS PASSED")
        print("===================================")

    except Exception as error:

        print()
        print("===================================")
        print(" TEST FAILED")
        print("===================================")

        print(f"Error type: {type(error).__name__}")
        print(f"Error: {error}")

        raise