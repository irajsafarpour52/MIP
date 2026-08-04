from faster_whisper import WhisperModel

print("Loading Whisper model...")

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

print("Whisper model loaded successfully")


def transcribe(audio_file: str) -> str:
    """
    دریافت مسیر فایل صوتی و برگرداندن متن جلسه
    """

    segments, info = model.transcribe(
        audio_file,
        language="fa",
        vad_filter=True,
        beam_size=5,
        initial_prompt="جلسه کاری، پروژه نرم‌افزاری، MVP، توسعه محصول"
    )

    transcript = ""

    for segment in segments:
        transcript += segment.text + " "

    return transcript.strip()


# فقط برای تست مستقیم فایل
if __name__ == "__main__":

    audio_file = r"D:\MIP\data\meeting.oga"

    text = transcribe(audio_file)

    print("\n--- Transcript ---")
    print(text)