import os

from openai import OpenAI
from dotenv import load_dotenv


# Load .env
load_dotenv()

print("Service file loaded...")
print("API KEY FOUND:", bool(os.getenv("GAPGPT_API_KEY")))


BASE_URL = "https://api.gapgpt.app/v1"
API_KEY = os.getenv("GAPGPT_API_KEY")
MODEL = "gpt-4o"


client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)


def generate_text(prompt: str) -> str:
    """
    ارسال Prompt به GapGPT و دریافت پاسخ متنی
    """

    if not prompt:
        return ""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    print("GapGPT service test...")

    result = generate_text(
        "سلام. این یک تست برای پروژه MIP است. فقط بگو: اتصال موفق است."
    )

    print("\n===== GAPGPT RESPONSE =====")
    print(result)