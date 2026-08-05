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

قوانین مهم:

1. فقط از متن جلسه استفاده کن.
2. هیچ اطلاعاتی از خودت اضافه نکن.
3. غلط‌های تشخیص گفتار Whisper را اصلاح کن.
4. اصطلاحات فنی را حفظ کن:
   MVP, AI, API, ERP, Git, Whisper, Ollama, Software
5. اگر کلمه‌ای نامشخص است، حدس قطعی نزن.
6. اگر تصمیمی در متن وجود ندارد، decisions را خالی بگذار.
7. اگر وظیفه مشخصی در متن وجود ندارد، tasks را خالی بگذار.
8. فقط JSON خروجی بده.
9. هیچ توضیحی قبل یا بعد از JSON ننویس.

متن خام جلسه:

{transcript}


فرمت خروجی:

{{
  "summary": "",
  "decisions": [],
  "tasks": []
 # "keywords": []
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
        timeout=900
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

    print("Ollama service test")

    test_text = """
    سلام امروز تصمیم گرفتیم نسخه MVP تا دو هفته آینده آماده شود.
    """

    result = summarize_meeting(test_text)

    print(json.dumps(
        result,
        ensure_ascii=False,
        indent=2
    ))