import json
import os


BASE_DIR = os.path.dirname(__file__)

PHRASE_FILE = os.path.join(
    BASE_DIR,
    "dictionaries",
    "phrases.json"
)


def load_phrases():
    """
    Load phrase correction dictionary
    """

    if not os.path.exists(PHRASE_FILE):
        return {}

    with open(
        PHRASE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# Dictionary loaded once
PHRASES = load_phrases()

print (PHRASES)
def correct_phrases(text: str) -> str:
    """
    اصلاح عبارت‌های چندکلمه‌ای خروجی Whisper
    """

    if not text:
        return text


    # اول عبارت‌های طولانی‌تر اصلاح شوند
    sorted_phrases = sorted(
        PHRASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )


    for wrong, correct in sorted_phrases:

        text = text.replace(
            wrong,
            correct
        )


    return text



if __name__ == "__main__":

    sample_text = """
    جلسه درباره ام وی پی و ای پی آی اولاما بود.
    تیم گیت هاب را بررسی کرد.
    """


    result = correct_phrases(sample_text)


    print("Original:")
    print(sample_text)

    print("\nCorrected:")
    print(result)