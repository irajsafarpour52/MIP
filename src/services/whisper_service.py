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
        
        # کمک به تشخیص واژه‌ها و اصطلاحات تخصصی جلسات
        initial_prompt="جلسه کاری، پروژه نرم‌افزاری، MVP، توسعه محصول",
        task="transcribe",

     
        # حفظ ارتباط معنایی بین بخش‌های متوالی جلسه
        condition_on_previous_text=True,

        # ابتدا با دمای صفر؛ در صورت مشکل امکان تلاش مجدد
        temperature=(0.0, 0.2, 0.4),

        # جلوگیری از تولید متن برای بخش‌های بدون گفتار
        no_speech_threshold=0.6,

        # جلوگیری از تکرارهای غیرطبیعی
        compression_ratio_threshold=2.4,

        # تشخیص خودکار سکوت‌ها و تقسیم مناسب‌تر صوت
        #vad_filter=True
      #  vad_parameters=True,
        
        # حداقل اطمینان قابل قبول برای تشخیص متن
        log_prob_threshold=-1.0

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