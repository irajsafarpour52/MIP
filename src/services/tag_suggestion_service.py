"""
MIP - Tag Suggestion Service

وظیفه این سرویس:
    استخراج برچسب‌های پیشنهادی از متن جلسه
    بر اساس Domain Vocabulary پروژه.

جریان:

    Meeting Markdown / Text
            ↓
    Vocabulary
            ↓
    بررسی taggable
            ↓
    بررسی canonical + aliases
            ↓
    محاسبه تعداد تطابق
            ↓
    مرتب‌سازی
            ↓
    پیشنهاد Tag ها

نکته مهم:
    این سرویس فعلاً هوشمند نیست و از LLM استفاده نمی‌کند.

    فقط Termهایی که در Vocabulary دارای:
        "taggable": true

    باشند، می‌توانند به عنوان Tag پیشنهاد شوند.
"""

import json
import re
from pathlib import Path
from typing import Any


# ============================================================
# مسیر Vocabulary
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

VOCABULARY_FILE = (
    PROJECT_ROOT
    / "dictionary"
    / "software_product_management.json"
)


# ============================================================
# تنظیمات سرویس
# ============================================================

DEFAULT_MAX_TAGS = 8


class TagSuggestionService:
    """
    سرویس پیشنهاد برچسب برای صورتجلسه.

    Vocabulary از فایل JSON خوانده می‌شود و
    فقط Termهایی که taggable=True دارند
    برای پیشنهاد Tag بررسی می‌شوند.
    """

    def __init__(
        self,
        vocabulary_file: Path | str = VOCABULARY_FILE,
        max_tags: int = DEFAULT_MAX_TAGS,
    ):
        """
        ایجاد سرویس پیشنهاد Tag.

        Args:
            vocabulary_file:
                مسیر فایل Vocabulary.

            max_tags:
                حداکثر تعداد Tag پیشنهادی.
        """

        self.vocabulary_file = Path(
            vocabulary_file
        )

        self.max_tags = max_tags

        # ----------------------------------------------------
        # بارگذاری Vocabulary
        # ----------------------------------------------------

        self.vocabulary = (
            self._load_vocabulary()
        )

        # ----------------------------------------------------
        # آماده‌سازی Terms قابل Tag
        # ----------------------------------------------------

        self.terms = (
            self._prepare_terms()
        )


    # ========================================================
    # بارگذاری Vocabulary
    # ========================================================

    def _load_vocabulary(
        self,
    ) -> dict[str, Any]:
        """
        فایل Vocabulary را از JSON می‌خواند.
        """

        if not self.vocabulary_file.exists():

            raise FileNotFoundError(
                "Vocabulary file not found: "
                f"{self.vocabulary_file}"
            )


        with open(
            self.vocabulary_file,
            "r",
            encoding="utf-8",
        ) as file:

            vocabulary = json.load(file)


        # ----------------------------------------------------
        # بررسی ساختار اصلی
        # ----------------------------------------------------

        if not isinstance(
            vocabulary,
            dict,
        ):

            raise ValueError(
                "Vocabulary must be a JSON object."
            )


        if "terms" not in vocabulary:

            raise ValueError(
                "Vocabulary must contain 'terms'."
            )


        if not isinstance(
            vocabulary["terms"],
            list,
        ):

            raise ValueError(
                "'terms' must be a list."
            )


        return vocabulary


    # ========================================================
    # آماده‌سازی Terms
    # ========================================================

    def _prepare_terms(
        self,
    ) -> list[dict[str, Any]]:
        """
        Terms موجود در Vocabulary را برای جستجو آماده می‌کند.

        فقط Termهایی که:

            "taggable": true

        دارند وارد ساختار جستجو می‌شوند.

        توجه:
            اگر taggable وجود نداشته باشد،
            مقدار پیش‌فرض False در نظر گرفته می‌شود.

        این رفتار عمداً محافظه‌کارانه است.
        """

        prepared_terms = []


        for term in self.vocabulary["terms"]:

            # ------------------------------------------------
            # فقط Terms قابل Tag
            # ------------------------------------------------

            if not term.get(
                "taggable",
                False,
            ):

                continue


            # ------------------------------------------------
            # Canonical
            # ------------------------------------------------

            canonical = str(
                term.get(
                    "canonical",
                    "",
                )
            ).strip()


            if not canonical:

                continue


            # ------------------------------------------------
            # Category
            # ------------------------------------------------

            category = term.get(
                "category",
                "general",
            )


            # ------------------------------------------------
            # Aliasها
            # ------------------------------------------------

            aliases = term.get(
                "aliases",
                [],
            )


            searchable_aliases = []


            for alias in aliases:

                # --------------------------------------------
                # ساختار استاندارد Alias
                # --------------------------------------------

                if isinstance(
                    alias,
                    dict,
                ):

                    value = str(
                        alias.get(
                            "value",
                            "",
                        )
                    ).strip()


                    searchable = alias.get(
                        "searchable",
                        True,
                    )


                # --------------------------------------------
                # پشتیبانی از ساختار ساده قدیمی
                # --------------------------------------------

                else:

                    value = str(
                        alias
                    ).strip()

                    searchable = True


                if (
                    value
                    and searchable
                ):

                    searchable_aliases.append(
                        value
                    )


            # ------------------------------------------------
            # ذخیره Term آماده
            # ------------------------------------------------

            prepared_terms.append(
                {
                    "canonical": canonical,
                    "aliases": searchable_aliases,
                    "category": category,
                }
            )


        return prepared_terms


    # ========================================================
    # نرمال‌سازی متن برای جستجو
    # ========================================================

    @staticmethod
    def _normalize_for_search(
        text: str,
    ) -> str:
        """
        متن را فقط برای جستجوی Tag نرمال می‌کند.

        متن اصلی جلسه تغییر نمی‌کند.

        مواردی که مدیریت می‌شوند:

            نیم‌فاصله
            فاصله‌های اضافی
            حروف بزرگ/کوچک انگلیسی
        """

        # ----------------------------------------------------
        # تبدیل نیم‌فاصله به فاصله
        # ----------------------------------------------------

        text = text.replace(
            "\u200c",
            " ",
        )


        # ----------------------------------------------------
        # یکسان‌سازی فاصله‌ها
        # ----------------------------------------------------

        text = re.sub(
            r"\s+",
            " ",
            text,
        )


        # ----------------------------------------------------
        # casefold برای متن انگلیسی
        # ----------------------------------------------------

        return text.strip().casefold()


    # ========================================================
    # تشخیص اصطلاح لاتین
    # ========================================================

    @staticmethod
    def _is_latin_term(
        term: str,
    ) -> bool:
        """
        بررسی می‌کند که آیا اصطلاح شامل
        حروف لاتین است یا خیر.

        مثال:

            MVP
            Whisper
            Ollama
            FastAPI
            User Story

        """

        return bool(
            re.search(
                r"[a-zA-Z]",
                term,
            )
        )


    # ========================================================
    # ساخت Pattern جستجو
    # ========================================================

    @classmethod
    def _build_search_pattern(
        cls,
        candidate: str,
    ) -> str:
        """
        Pattern مناسب برای جستجوی candidate ایجاد می‌کند.

        برای اصطلاحات لاتین:
            از boundary سفارشی استفاده می‌شود
            تا substring اشتباه match نشود.

        مثال:

            Sprint

        نباید در:

            Sprinting
            Sprints

        match شود.

        برای اصطلاحات فارسی:
            matching مستقیم انجام می‌شود.
        """

        escaped = re.escape(
            candidate
        )


        if cls._is_latin_term(
            candidate
        ):

            return (
                rf"(?<![A-Za-z0-9_])"
                rf"{escaped}"
                rf"(?![A-Za-z0-9_])"
            )


        return escaped


    # ========================================================
    # شمارش تطابق
    # ========================================================

    def _count_matches(
        self,
        text: str,
        term: dict[str, Any],
    ) -> int:
        """
        تعداد دفعات دیده شدن یک Term یا Alias
        در متن جلسه را محاسبه می‌کند.

        canonical و aliasها با هم بررسی می‌شوند.

        برای جلوگیری از شمردن چندباره یک مفهوم،
        بیشترین تعداد تطابق بین canonical و aliasها
        به عنوان score انتخاب می‌شود.
        """

        canonical = term[
            "canonical"
        ]


        candidates = [
            canonical,
            *term["aliases"],
        ]


        best_count = 0


        for candidate in candidates:

            # ------------------------------------------------
            # نرمال‌سازی Candidate
            # ------------------------------------------------

            candidate = (
                self._normalize_for_search(
                    candidate
                )
            )


            if not candidate:

                continue


            # ------------------------------------------------
            # ساخت Pattern
            # ------------------------------------------------

            pattern = (
                self._build_search_pattern(
                    candidate
                )
            )


            # ------------------------------------------------
            # شمارش تطابق
            # ------------------------------------------------

            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            )


            count = len(matches)


            if count > best_count:

                best_count = count


        return best_count


    # ========================================================
    # پیشنهاد Tag
    # ========================================================

    def suggest_tags(
        self,
        text: str,
        max_tags: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        بر اساس متن جلسه، Tagهای پیشنهادی را تولید می‌کند.

        فقط Termهای taggable=True بررسی می‌شوند.
        """

        # ----------------------------------------------------
        # بررسی نوع ورودی
        # ----------------------------------------------------

        if not isinstance(
            text,
            str,
        ):

            raise TypeError(
                "text must be a string."
            )


        # ----------------------------------------------------
        # متن خالی
        # ----------------------------------------------------

        if not text.strip():

            return []


        # ----------------------------------------------------
        # نرمال‌سازی متن
        # ----------------------------------------------------

        normalized_text = (
            self._normalize_for_search(
                text
            )
        )


        results = []


        # ----------------------------------------------------
        # بررسی Terms قابل Tag
        # ----------------------------------------------------

        for term in self.terms:

            score = (
                self._count_matches(
                    normalized_text,
                    term,
                )
            )


            # ------------------------------------------------
            # فقط Terms موجود در متن
            # ------------------------------------------------

            if score > 0:

                results.append(
                    {
                        "tag": term[
                            "canonical"
                        ],

                        "category": term[
                            "category"
                        ],

                        "score": score,
                    }
                )


        # ----------------------------------------------------
        # مرتب‌سازی
        #
        # اول:
        #   score بیشتر
        #
        # سپس:
        #   نام Tag
        # ----------------------------------------------------

        results.sort(
            key=lambda item: (
                -item["score"],
                item["tag"].casefold(),
            )
        )


        # ----------------------------------------------------
        # تعیین max_tags
        # ----------------------------------------------------

        if max_tags is None:

            max_tags = self.max_tags


        # ----------------------------------------------------
        # خروجی نهایی
        # ----------------------------------------------------

        return results[
            :max_tags
        ]


# ============================================================
# Cache سرویس
# ============================================================

_service_cache: dict[
    tuple[str, int],
    TagSuggestionService,
] = {}


def _get_cached_service(
    vocabulary_file: Path | str = VOCABULARY_FILE,
    max_tags: int = DEFAULT_MAX_TAGS,
) -> TagSuggestionService:
    """
    یک instance از TagSuggestionService را cache می‌کند.

    بنابراین Vocabulary برای هر درخواست
    دوباره از فایل JSON خوانده نمی‌شود.
    """

    vocabulary_path = str(
        Path(
            vocabulary_file
        ).resolve()
    )


    cache_key = (
        vocabulary_path,
        max_tags,
    )


    service = _service_cache.get(
        cache_key
    )


    if service is None:

        service = TagSuggestionService(
            vocabulary_file=vocabulary_path,
            max_tags=max_tags,
        )


        _service_cache[
            cache_key
        ] = service


    return service


# ============================================================
# تابع عمومی سرویس
# ============================================================

def suggest_tags(
    text: str,
    max_tags: int = DEFAULT_MAX_TAGS,
) -> list[dict[str, Any]]:
    """
    تابع ساده برای پیشنهاد Tag.

    سایر بخش‌های MIP می‌توانند مستقیماً
    از این تابع استفاده کنند.

    مثال:

        tags = suggest_tags(
            meeting_text
        )
    """

    service = _get_cached_service(
        max_tags=max_tags,
    )


    return service.suggest_tags(
        text
    )


# ============================================================
# تست مستقیم سرویس
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "==================================="
    )
    print(
        " MIP Tag Suggestion Service"
    )
    print(
        "==================================="
    )


    # --------------------------------------------------------
    # متن آزمایشی
    # --------------------------------------------------------

    test_text = """
    در جلسه امروز درباره وضعیت پروژه MIP صحبت شد.

    نسخه MVP در حال آماده‌سازی است.

    تیم توسعه باید Feature جدید را بررسی کند.

    قرار شد Backlog اصلاح شود و
    سه User Story برای Sprint بعدی آماده شود.

    همچنین Roadmap فصل آینده بررسی شد.

    برای تبدیل صوت از Whisper استفاده می‌کنیم
    و API با FastAPI پیاده‌سازی شده است.

    داده‌ها در ChromaDB ذخیره می‌شوند
    و در ادامه RAG به سیستم اضافه خواهد شد.

    همچنین Ollama برای اجرای مدل استفاده می‌شود.
    """


    # --------------------------------------------------------
    # ایجاد سرویس
    # --------------------------------------------------------

    service = TagSuggestionService()


    # --------------------------------------------------------
    # نمایش تعداد Terms قابل Tag
    # --------------------------------------------------------

    print()
    print(
        f"Taggable terms: {len(service.terms)}"
    )


    # --------------------------------------------------------
    # پیشنهاد Tag
    # --------------------------------------------------------

    tags = service.suggest_tags(
        test_text
    )


    # --------------------------------------------------------
    # نمایش نتیجه
    # --------------------------------------------------------

    print()
    print(
        "Suggested Tags:"
    )
    print()


    if not tags:

        print(
            "No tags found."
        )


    else:

        for item in tags:

            print(
                f"- {item['tag']} "
                f"(category={item['category']}, "
                f"score={item['score']})"
            )


    print()
    print(
        "==================================="
    )
    print(
        " Tag suggestion completed"
    )
    print(
        "==================================="
    )