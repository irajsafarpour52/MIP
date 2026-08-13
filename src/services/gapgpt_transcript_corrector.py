import os

from gapgpt_services import generate_text


# سرویس قبلی Ollama — فعلاً غیرفعال است و حذف نمی‌شود
# from ollama_service import generate_text


PROMPT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "prompts",
    "transcript_corrector_prompt.txt"
)


def load_prompt() -> str:
    """خواندن Prompt اصلاح Transcript از فایل TXT."""

    with open(
        PROMPT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def correct_transcript(transcript: str) -> str:
    """
    اصلاح Transcript خام Whisper.
    """

    if not transcript:
        return ""

    system_prompt = load_prompt()

    prompt = f"""
{system_prompt}

RAW TRANSCRIPT:
--------------------

{transcript}

--------------------

CORRECTED TRANSCRIPT:
"""

    return generate_text(prompt)


if __name__ == "__main__":

    print("Transcript Corrector Test...")

    test_text = """
سلام، امرو جلسه براریسی پورجی MVP رو شروع می کنیم.
حدفه ما آمد سازی نوزخه MVP تر موتد دو هفته آینده است.
بذیفه تیم توسه اتسال اولاما رو براریسی کنه.
"""

    print("\n===== RAW TRANSCRIPT =====")
    print(test_text)

    result = correct_transcript(test_text)

    print("\n===== CORRECTED TRANSCRIPT =====")
    print(result)