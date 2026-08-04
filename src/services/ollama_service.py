import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


def summarize_meeting(transcript: str) -> dict:
    """
    دریافت متن جلسه و برگرداندن خلاصه ساختاریافته
    """

    prompt = f"""
تو یک دستیار حرفه‌ای مدیریت جلسه هستی.

قوانین:

1. فقط از متن زیر استفاده کن.
2. هیچ اطلاعاتی از خودت اضافه نکن.
3. اگر تصمیمی وجود ندارد، decisions را خالی بگذار.
4. اگر وظیفه‌ای وجود ندارد، tasks را خالی بگذار.
5. فقط غلط‌های تشخیص گفتار را اصلاح کن.
6. فقط JSON برگردان.
7. هیچ توضیحی قبل یا بعد از JSON ننویس.

متن جلسه:

{transcript}

فرمت خروجی:

{{
  "summary": "",
  "decisions": [],
  "tasks": []
}}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "temperature": 0
        },
        timeout=300
    )

    response.raise_for_status()

    result = response.json()

    try:
        return json.loads(result["response"])

    except json.JSONDecodeError:
        print("===== RAW RESPONSE FROM OLLAMA =====")
        print(result["response"])
        raise Exception("Ollama did not return valid JSON.")


if __name__ == "__main__":
    print("This module is a service.")
    print("Run meeting_service.py instead.")