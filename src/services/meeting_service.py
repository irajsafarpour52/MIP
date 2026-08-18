"""
MIP - Meeting Service

مسئولیت این ماژول:
    اجرای Pipeline اصلی پردازش جلسه:

    Audio
      ↓
    Whisper
      ↓
    Vocabulary Normalizer
      ↓
    Text Cleaner
      ↓
    GapGPT Transcript Corrector
      ↓
    Tag Suggestion
      ↓
    GapGPT Meeting Analyzer
      ↓
    Markdown

نکته:
    Normalizer برای استانداردسازی اصطلاحات تخصصی استفاده می‌شود.

    Tag Suggestion فقط اصطلاحاتی را پیشنهاد می‌دهد
    که در Vocabulary دارای taggable=true باشند.

    Tag Suggestion بدون LLM کار می‌کند.
"""


import sys
import os
import json


# ============================================================
# تنظیم مسیر پروژه
# ============================================================

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# ============================================================
# سرویس‌های MIP
# ============================================================

# تبدیل صوت به متن
from .whisper_service import transcribe

# استانداردسازی اصطلاحات تخصصی
from .normalizer import VocabularyNormalizer

# پاک‌سازی اولیه متن
from .text_cleaner import clean_text

# اصلاح خطاهای متن Whisper توسط GapGPT
from .gapgpt_transcript_corrector import correct_transcript

# سرویس پیشنهاد Tag
from .tag_suggestion_service import suggest_tags

# سرویس تولید متن توسط GapGPT
from .gapgpt_services import generate_text

# ساخت فایل Markdown
from writers.markdown_writer import write_markdown


# ============================================================
# مسیر ریشه پروژه
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# ============================================================
# مسیر فایل خروجی Markdown
# ============================================================

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "meeting_report.md"
)


# ============================================================
# مسیر Prompt تحلیل جلسه
# ============================================================

PROMPT_FILE = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    "prompts",
    "meeting_analyzer_prompt.txt"
)


# ============================================================
# بارگذاری Prompt
# ============================================================

def load_prompt() -> str:
    """
    Prompt تحلیل جلسه را از فایل TXT می‌خواند.
    """

    with open(
        PROMPT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ============================================================
# تحلیل جلسه توسط GapGPT
# ============================================================

def summarize_meeting(
    transcript: str
):
    """
    متن اصلاح‌شده جلسه را به GapGPT ارسال می‌کند
    و نتیجه تحلیل را به صورت JSON برمی‌گرداند.
    """

    # --------------------------------------------------------
    # خواندن Prompt
    # --------------------------------------------------------

    system_prompt = load_prompt()


    # --------------------------------------------------------
    # ساخت Prompt نهایی
    # --------------------------------------------------------

    prompt = f"""
{system_prompt}

متن جلسه:

--------------------

{transcript}

--------------------
"""


    # --------------------------------------------------------
    # ارسال به GapGPT
    # --------------------------------------------------------

    response = generate_text(
        prompt
    )


    # --------------------------------------------------------
    # Debug
    # --------------------------------------------------------

    print(
        "\n===== RAW GAPGPT RESPONSE ====="
    )

    print(
        response
    )


    # --------------------------------------------------------
    # پاک‌سازی پاسخ
    # --------------------------------------------------------

    response = response.strip()


    # --------------------------------------------------------
    # پیدا کردن JSON
    # --------------------------------------------------------

    start = response.find("{")
    end = response.rfind("}")


    if start == -1 or end == -1:

        print(
            "\n===== INVALID GAPGPT RESPONSE ====="
        )

        print(
            response
        )

        raise ValueError(
            "GapGPT response does not contain valid JSON."
        )


    # --------------------------------------------------------
    # استخراج JSON
    # --------------------------------------------------------

    response = response[
        start:end + 1
    ]


    # --------------------------------------------------------
    # تبدیل به Dictionary
    # --------------------------------------------------------

    return json.loads(
        response
    )


# ============================================================
# پردازش کامل جلسه
# ============================================================

def process_meeting(
    audio_file: str
):
    """
    Pipeline کامل پردازش جلسه.

    مراحل:

        1. Whisper
        2. Vocabulary Normalization
        3. Text Cleaning
        4. Transcript Correction
        5. Tag Suggestion
        6. Meeting Analysis
        7. Markdown Generation
    """


    # ========================================================
    # Step 1 - Transcription
    # ========================================================

    print(
        "Step 1: Transcribing audio..."
    )


    transcript = transcribe(
        audio_file
    )


    print(
        "Raw transcript:"
    )


    # ========================================================
    # Step 1.5 - Vocabulary Normalization
    # ========================================================

    print(
        "\nStep 1.5: Normalizing vocabulary..."
    )


    normalizer = (
        VocabularyNormalizer()
    )


    transcript = normalizer.normalize(
        transcript
    )


    print(
        "Vocabulary normalization completed."
    )


    # ========================================================
    # Step 1.6 - Text Cleaning
    # ========================================================

    print(
        "\nStep 1.6: Cleaning transcript..."
    )


    transcript = clean_text(
        transcript
    )


    print(
        "\nClean transcript:"
    )


    # ========================================================
    # Step 2 - Transcript Correction
    # ========================================================

    print(
        "\nStep 2: Correcting transcript..."
    )


    transcript = correct_transcript(
        transcript
    )


    print(
        "\nCorrected transcript:"
    )


    # ========================================================
    # Step 2.5 - Tag Suggestion
    # ========================================================

    print(
        "\nStep 2.5: Suggesting meeting tags..."
    )


    tags = suggest_tags(
        transcript
    )


    print(
        "\nSuggested Tags:"
    )


    if tags:

        for item in tags:

            print(
                f"- {item['tag']} "
                f"(category={item['category']}, "
                f"score={item['score']})"
            )

    else:

        print(
            "- No tags found."
        )


    print(
        "Tag suggestion completed."
    )


    # ========================================================
    # Step 3 - Meeting Analysis
    # ========================================================

    print(
        "\nStep 3: Analyzing meeting with GapGPT..."
    )


    result = summarize_meeting(
        transcript
    )


    # ========================================================
    # اضافه کردن Tags به نتیجه نهایی
    # ========================================================

    result["tags"] = tags


    # ========================================================
    # Step 4 - Markdown Generation
    # ========================================================

    print(
        "\nStep 4: Writing Markdown report..."
    )


    write_markdown(
        result,
        OUTPUT_FILE
    )


    print(
        f"Markdown report saved to: {OUTPUT_FILE}"
    )


    # --------------------------------------------------------
    # بازگرداندن نتیجه نهایی
    # --------------------------------------------------------

    return result


# ============================================================
# اجرای مستقیم فایل برای تست
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # فایل صوتی تست
    # --------------------------------------------------------

    audio = r"D:\MIP\data\meeting.oga"


    # --------------------------------------------------------
    # اجرای Pipeline
    # --------------------------------------------------------

    meeting = process_meeting(
        audio
    )


    # --------------------------------------------------------
    # نمایش نتیجه نهایی
    # --------------------------------------------------------

    print(
        "\n===== FINAL RESULT =====\n"
    )


    print(
        meeting
    )