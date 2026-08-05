import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from whisper_service import transcribe
from ollama_service import summarize_meeting
from writers.markdown_writer import write_markdown
from text_cleaner import  clean_text


def process_meeting(audio_file: str):

    print("Step 1 : Transcribing audio...")

    transcript = transcribe(audio_file)

    print("Raw transcript:")
    print(transcript)

    transcript = clean_text(transcript)

    print("\nClean transcript:")
    print(transcript)


    print("Step 2 : Analyzing with Ollama...")

    result = summarize_meeting(transcript)
    write_markdown(result,"meeting_report.md")

    return result


if __name__ == "__main__":

    audio = r"D:\MIP\data\meeting.oga"

    meeting = process_meeting(audio)

    print("\n===== FINAL RESULT =====\n")

    print(meeting)