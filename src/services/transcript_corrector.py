import os

from ollama_service import generate_text


PROMPT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "prompts",
    "transcript_corrector_prompt.txt"
)


def load_prompt() -> str:
    with open(
        PROMPT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return file.read()


def correct_transcript(transcript: str) -> str:

    if not transcript:
        return transcript

    system_prompt = load_prompt()

    prompt = f"""
{system_prompt}

RAW TRANSCRIPT:
{transcript}
"""

    return generate_text(prompt)

if __name__ == "__main__":
    print("Transcript Corrector Test")

    test_text = """
    سلام، امرو جلسه براریسی پورجی MVP رو شروع می کنیم.
    حدفه ما آمد سازی نوزخه MVP تر موتد دو هفته آینده است.
    """

    print("Sending to Ollama...")

    result = correct_transcript(test_text)

    print("\n===== CORRECTED TRANSCRIPT =====")
    print(result)