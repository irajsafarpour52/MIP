"""
MIP - Vocabulary Normalizer

وظیفه این ماژول:
    دریافت متن خام و استفاده از Domain Vocabulary
    برای تبدیل Aliasهایی که normalize=True دارند
    به canonical term.

مثال:

    ام وی پی
        ↓
    MVP

    فست ای پی
        ↓
    FastAPI

    ویس پر
        ↓
    Whisper

نکته مهم:
    این ماژول فعلاً فقط Normalization انجام می‌دهد.

    به Whisper، text_cleaner، GapGPT یا Pipeline اصلی
    متصل نیست.

این جداسازی عمدی است تا ابتدا رفتار Normalizer را
به صورت مستقل تست کنیم.
"""

import json
import re
from pathlib import Path


# ============================================================
# مسیر Vocabulary
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

VOCABULARY_PATH = (
    PROJECT_ROOT
    / "dictionary"
    / "software_product_management.json"
)


# ============================================================
# Vocabulary Normalizer
# ============================================================

class VocabularyNormalizer:
    """
    مسئول Normalization متن بر اساس Domain Vocabulary.

    در زمان ساخت شیء، Vocabulary از فایل JSON خوانده می‌شود
    و Aliasهایی که normalize=True هستند در یک Lookup آماده
    قرار می‌گیرند.
    """

    def __init__(self, vocabulary_path=None):
        """
        ایجاد Normalizer.

        Args:
            vocabulary_path:
                مسیر فایل Vocabulary.
                اگر مشخص نشود، مسیر پیش‌فرض پروژه استفاده می‌شود.
        """

        if vocabulary_path is None:
            vocabulary_path = VOCABULARY_PATH

        self.vocabulary_path = Path(vocabulary_path)

        self.vocabulary = self._load_vocabulary()

        # Lookup نهایی:
        #
        # {
        #     "ام وی پی": "MVP",
        #     "فست ای پی": "FastAPI",
        #     "ویس پر": "Whisper"
        # }
        #
        self.normalization_map = {}

        self._build_normalization_map()


    # ========================================================
    # بارگذاری Vocabulary
    # ========================================================

    def _load_vocabulary(self):
        """
        فایل JSON Vocabulary را می‌خواند.
        """

        if not self.vocabulary_path.exists():

            raise FileNotFoundError(
                f"Vocabulary پیدا نشد:\n"
                f"{self.vocabulary_path}"
            )

        with open(
            self.vocabulary_path,
            "r",
            encoding="utf-8"
        ) as file:

            vocabulary = json.load(file)

        if "terms" not in vocabulary:

            raise ValueError(
                "ساختار Vocabulary معتبر نیست: "
                "'terms' پیدا نشد."
            )

        return vocabulary


    # ========================================================
    # ساخت Lookup مربوط به Normalization
    # ========================================================

    def _build_normalization_map(self):
        """
        تمام Aliasهایی را که normalize=True هستند
        پیدا کرده و به canonical term متصل می‌کند.

        مثال:

            فیچر → Feature
            ام وی پی → MVP
            فست ای پی → FastAPI
        """

        for term in self.vocabulary["terms"]:

            canonical = term["canonical"]

            for alias in term["aliases"]:

                value = alias["value"]

                normalize = alias["normalize"]

                if normalize:

                    # جلوگیری از ثبت Alias خالی
                    if not value.strip():
                        continue

                    self.normalization_map[value] = canonical


    # ========================================================
    # Normalization یک متن
    # ========================================================

    def normalize(self, text):
        """
        متن را بر اساس Vocabulary نرمال می‌کند.

        فقط Aliasهایی تغییر می‌کنند که:

            normalize == True

        باشند.

        Aliasهایی که normalize=False هستند
        عمداً بدون تغییر باقی می‌مانند.

        Args:
            text:
                متن ورودی.

        Returns:
            str:
                متن نرمال‌شده.
        """

        if not isinstance(text, str):

            raise TypeError(
                "text باید از نوع str باشد."
            )

        normalized_text = text

        # Aliasهای طولانی‌تر را اول بررسی می‌کنیم.
        #
        # مثال:
        #
        # "فست ای پی"
        #
        # باید قبل از Aliasهای کوتاه‌تر بررسی شود.
        #
        aliases = sorted(
            self.normalization_map.keys(),
            key=len,
            reverse=True
        )

        for alias in aliases:

            canonical = self.normalization_map[alias]

            normalized_text = self._replace_term(
                normalized_text,
                alias,
                canonical
            )

        return normalized_text


    # ========================================================
    # جایگزینی امن اصطلاح
    # ========================================================

    @staticmethod
    def _replace_term(text, source, target):
        """
        یک اصطلاح را در متن جایگزین می‌کند.

        از جایگزینی ساده substring استفاده نمی‌کنیم،
        چون ممکن است بخشی از یک کلمه را اشتباهاً تغییر دهد.

        برای فارسی و انگلیسی، مرزهای متنی ساده را در نظر
        می‌گیریم.
        """

        pattern = re.escape(source)

        return re.sub(
            pattern,
            target,
            text
        )


# ============================================================
# تابع ساده برای استفاده مستقیم
# ============================================================

def normalize_text(text):
    """
    تابع کمکی برای Normalization مستقیم.

    مثال:

        result = normalize_text(
            "ام وی پی با فست ای پی ساخته شد"
        )
    """

    normalizer = VocabularyNormalizer()

    return normalizer.normalize(text)


# ============================================================
# تست دستی
# ============================================================

if __name__ == "__main__":

    print("===================================")
    print(" MIP Vocabulary Normalizer")
    print("===================================")

    normalizer = VocabularyNormalizer()

    print(
        f"Vocabulary loaded: "
        f"{normalizer.vocabulary_path}"
    )

    print(
        f"Normalization terms: "
        f"{len(normalizer.normalization_map)}"
    )

    print()

    examples = [
        "ام وی پی باید آماده شود.",
        "این قابلیت در فست ای پی پیاده سازی می‌شود.",
        "ویس پر برای تبدیل صوت استفاده می‌شود.",
        "فیچر جدید محصول آماده شد.",
        "قابلیت جدید محصول بررسی شد."
    ]

    for text in examples:

        result = normalizer.normalize(text)

        print(f"Input : {text}")
        print(f"Output: {result}")
        print("-" * 50)