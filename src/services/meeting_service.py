from whisper_service import transcribe
from ollama_service import summarize_meeting


def process_meeting(audio_file: str):

    print("Step 1 : Transcribing audio...")

    transcript = transcribe(audio_file)

    print("Transcript completed.\n")

    print("Step 2 : Analyzing with Ollama...")

    result = summarize_meeting(transcript)

    return result


if __name__ == "__main__":

    audio = r"D:\MIP\data\meeting.oga"

    meeting = process_meeting(audio)

    print("\n===== FINAL RESULT =====\n")

    print(meeting)