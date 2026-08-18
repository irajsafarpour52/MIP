"""
MIP - Vocabulary Tests

هدف:
    تست مستقل فرهنگ لغات تخصصی MIP قبل از اتصال
    آن به Pipeline اصلی پروژه.

در این مرحله:
    - JSON را بررسی می‌کنیم.
    - ساختار Vocabulary را بررسی می‌کنیم.
    - اصطلاحات اصلی را بررسی می‌کنیم.
    - Alias و قوانین normalize/searchable را بررسی می‌کنیم.

فعلاً هیچ ارتباطی با Whisper یا text_cleaner نداریم.
"""

import json
from pathlib import Path


# ============================================================
# مسیر پروژه
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

VOCABULARY_PATH = (
    PROJECT_ROOT
    / "dictionary"
    / "software_product_management.json"
)


# ============================================================
# بارگذاری Vocabulary
# ============================================================

def load_vocabulary():
    """
    فایل JSON فرهنگ لغات را می‌خواند و به Dictionary پایتون
    تبدیل می‌کند.
    """

    if not VOCABULARY_PATH.exists():
        raise FileNotFoundError(
            f"Vocabulary پیدا نشد:\n{VOCABULARY_PATH}"
        )

    with open(
        VOCABULARY_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# پیدا کردن یک اصطلاح
# ============================================================

def find_term(vocabulary, term_name):
    """
    یک اصطلاح را بر اساس مقدار term پیدا می‌کند.

    مثال:
        find_term(vocabulary, "MVP")
    """

    for term in vocabulary["terms"]:

        if term["term"] == term_name:
            return term

    return None


# ============================================================
# تست ساختار کلی Vocabulary
# ============================================================

def test_vocabulary_structure():
    """
    بررسی ساختار اصلی فایل Vocabulary.
    """

    vocabulary = load_vocabulary()

    assert "industry" in vocabulary
    assert "domain" in vocabulary
    assert "language" in vocabulary
    assert "version" in vocabulary
    assert "terms" in vocabulary

    assert isinstance(
        vocabulary["terms"],
        list
    )

    assert len(vocabulary["terms"]) > 0


# ============================================================
# تست ساختار Termها
# ============================================================

def test_terms_structure():
    """
    بررسی می‌کند که هر اصطلاح، فیلدهای ضروری را داشته باشد.
    """

    vocabulary = load_vocabulary()

    for term in vocabulary["terms"]:

        assert "term" in term
        assert "canonical" in term
        assert "aliases" in term
        assert "category" in term
        assert "related_terms" in term

        assert isinstance(term["term"], str)
        assert isinstance(term["canonical"], str)
        assert isinstance(term["aliases"], list)
        assert isinstance(term["category"], str)
        assert isinstance(term["related_terms"], list)

        # بررسی ساختار Aliasها
        for alias in term["aliases"]:

            assert "value" in alias
            assert "normalize" in alias
            assert "searchable" in alias

            assert isinstance(
                alias["value"],
                str
            )

            assert isinstance(
                alias["normalize"],
                bool
            )

            assert isinstance(
                alias["searchable"],
                bool
            )


# ============================================================
# تست MVP
# ============================================================

def test_mvp_term():
    """
    بررسی می‌کند که اصطلاح MVP وجود داشته باشد
    و canonical آن صحیح باشد.
    """

    vocabulary = load_vocabulary()

    term = find_term(
        vocabulary,
        "MVP"
    )

    assert term is not None

    assert term["canonical"] == "MVP"


# ============================================================
# تست Aliasهای MVP
# ============================================================

def test_mvp_aliases():
    """
    بررسی Aliasهای مربوط به MVP.

    این Aliasها باید قابلیت Normalization داشته باشند.
    """

    vocabulary = load_vocabulary()

    term = find_term(
        vocabulary,
        "MVP"
    )

    assert term is not None

    aliases = {
        alias["value"]: alias
        for alias in term["aliases"]
    }

    assert "ام وی پی" in aliases
    assert "ام‌وی‌پی" in aliases

    assert aliases["ام وی پی"]["normalize"] is True
    assert aliases["ام وی پی"]["searchable"] is True

    assert aliases["ام‌وی‌پی"]["normalize"] is True
    assert aliases["ام‌وی‌پی"]["searchable"] is True


# ============================================================
# تست Feature
# ============================================================

def test_feature_term():
    """
    بررسی اصطلاح Feature و Aliasهای آن.
    """

    vocabulary = load_vocabulary()

    term = find_term(
        vocabulary,
        "Feature"
    )

    assert term is not None

    assert term["canonical"] == "Feature"

    aliases = {
        alias["value"]: alias
        for alias in term["aliases"]
    }

    # فیچر باید قابل Normalization باشد.
    assert "فیچر" in aliases
    assert aliases["فیچر"]["normalize"] is True

    # قابلیت و ویژگی فعلاً فقط برای Search هستند
    # و نباید متن را مستقیماً تغییر دهند.
    assert "قابلیت" in aliases
    assert "ویژگی" in aliases

    assert aliases["قابلیت"]["normalize"] is False
    assert aliases["قابلیت"]["searchable"] is True

    assert aliases["ویژگی"]["normalize"] is False
    assert aliases["ویژگی"]["searchable"] is True


# ============================================================
# تست اصطلاحات مهم فناوری MIP
# ============================================================

def test_mip_technology_terms():
    """
    بررسی چند اصطلاح فناوری که در Pipeline خود MIP
    استفاده می‌شوند.
    """

    vocabulary = load_vocabulary()

    expected_terms = [
        "Whisper",
        "FastAPI",
        "ChromaDB",
        "Embedding",
        "RAG"
    ]

    for term_name in expected_terms:

        term = find_term(
            vocabulary,
            term_name
        )

        assert term is not None, (
            f"Term پیدا نشد: {term_name}"
        )

        assert term["canonical"] == term_name


# ============================================================
# اجرای تست‌ها
# ============================================================

if __name__ == "__main__":

    print("===================================")
    print(" MIP Vocabulary Test")
    print("===================================")

    try:

        load_vocabulary()

        print("✓ Vocabulary loaded")

        test_vocabulary_structure()
        print("✓ Vocabulary structure: OK")

        test_terms_structure()
        print("✓ Terms structure: OK")

        test_mvp_term()
        print("✓ MVP term: OK")

        test_mvp_aliases()
        print("✓ MVP aliases: OK")

        test_feature_term()
        print("✓ Feature term: OK")

        test_mip_technology_terms()
        print("✓ MIP technology terms: OK")

        print()
        print("===================================")
        print(" ALL TESTS PASSED")
        print("===================================")

    except Exception as error:

        print()
        print("===================================")
        print(" TEST FAILED")
        print("===================================")

        print(
            f"Error type: {type(error).__name__}"
        )

        print(
            f"Error: {error}"
        )

        raise