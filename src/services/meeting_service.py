import sys
import os
import json

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from gapgpt_transcript_corrector import correct_transcript
from whisper_service import transcribe

# سرویس Ollama فعلاً غیرفعال است و حذف نشده
# from ollama_service import summarize_meeting

from gapgpt_services import generate_text

from writers.markdown_writer import write_markdown
from text_cleaner import clean_text

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "meeting_report.md"
)



# مسیر فایل Prompt تحلیل جلسه
PROMPT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "prompts",
    "meeting_analyzer_prompt.txt"
)


def load_prompt() -> str:
    """
    خواندن Prompt تحلیل جلسه از فایل متنی
    """

    with open(
        PROMPT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def summarize_meeting(transcript: str):

    # خواندن Prompt از فایل TXT
    system_prompt = load_prompt()

    prompt = f"""
{system_prompt}

متن جلسه:

--------------------

{transcript}

--------------------
"""

    # ارسال متن و Prompt به GapGPT
    response = generate_text(prompt)

    print("\n===== RAW GAPGPT RESPONSE =====")
    print(response)

    response = response.strip()

    # پیدا کردن محدوده JSON در پاسخ مدل
    start = response.find("{")
    end = response.rfind("}")

    if start == -1 or end == -1:

        print("\n===== INVALID GAPGPT RESPONSE =====")
        print(response)

        raise ValueError(
            "GapGPT response does not contain valid JSON."
        )

    response = response[start:end + 1]

    return json.loads(response)


def process_meeting(audio_file: str):

    print("Step 1: Transcribing audio...")

    # تبدیل فایل صوتی به متن توسط Whisper
    transcript = transcribe(audio_file)

    print("Raw transcript:")
    # print(transcript)


    # پاک‌سازی اولیه متن
    transcript = clean_text(transcript)

    print("\nClean transcript:")
    # print(transcript)


    print("\nStep 2: Correcting transcript...")

    # اصلاح خطاهای Whisper توسط Transcript Corrector
    transcript = correct_transcript(transcript)

    print("\nCorrected transcript:")
    # print(transcript)


    print("\nStep 3: Analyzing meeting with GapGPT...")

    # تحلیل متن اصلاح‌شده جلسه
    result = summarize_meeting(transcript)


    # ساخت فایل گزارش Markdown
    write_markdown(
        result,
        OUTPUT_FILE
    )

    return result


if __name__ == "__main__":

    audio = r"D:\MIP\data\meeting.oga"

    meeting = process_meeting(audio)

    print("\n===== FINAL RESULT =====\n")

    print(meeting)