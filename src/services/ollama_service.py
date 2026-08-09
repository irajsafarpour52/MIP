import json
import os
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


PROMPT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "prompts",
    "meeting_analyzer_prompt.txt"
)


def load_prompt() -> str:
    with open(
        PROMPT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def generate_text(prompt: str) -> str:

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

    return result["response"]


def summarize_meeting(transcript: str) -> dict:
    """
    تحلیل متن جلسه و تولید خروجی ساختاریافته
    """

    if not transcript:
        return {
            "summary": "",
            "decisions": [],
            "tasks": [],
            "next_meeting": None
        }

    prompt_template = load_prompt()

    prompt = prompt_template.replace(
        "{{TRANSCRIPT}}",
        transcript
    )

    response_text = generate_text(prompt)

    try:
        return json.loads(response_text)

    except json.JSONDecodeError:

        print("===== RAW RESPONSE FROM OLLAMA =====")
        print(response_text)

        raise Exception(
            "Ollama did not return valid JSON."
        )


if __name__ == "__main__":

    print("Ollama service test")

    test_text = """
    سلام امروز تصمیم گرفتیم نسخه MVP تا دو هفته آینده آماده شود.
    """

    result = summarize_meeting(test_text)

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    )