from pathlib import Path
from datetime import datetime
import json

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.services.meeting_service import process_meeting
from src.services.tag_suggestion_service import suggest_tags


# =========================================================
# برنامه اصلی FastAPI
# =========================================================

app = FastAPI(
    title="MIP",
    description="Meeting Intelligent Platform",
    version="1.0"
)


# =========================================================
# مسیرهای پروژه
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

WEB_PATH = BASE_DIR / "src" / "web"

AUDIO_PATH = BASE_DIR / "data" / "audio"

AUDIO_PATH.mkdir(
    parents=True,
    exist_ok=True
)

# فایل اصلی صورتجلسه MIP
MEETING_REPORT_FILE = BASE_DIR / "meeting_report.md"


# =========================================================
# فایل‌های استاتیک
# =========================================================

app.mount(
    "/web",
    StaticFiles(
        directory=WEB_PATH
    ),
    name="web"
)


# =========================================================
# نمایش صفحه اصلی
# =========================================================

@app.get("/")
def home():
    """
    نمایش صفحه اصلی برنامه MIP.
    """

    return FileResponse(
        WEB_PATH / "index.html"
    )


# =========================================================
# مدل دریافت Markdown
# =========================================================

class MeetingSaveRequest(BaseModel):
    """
    اطلاعات مورد نیاز برای ذخیره صورتجلسه.
    """

    content: str


# =========================================================
# ذخیره فایل صوتی
# =========================================================

async def save_audio_file(
    file: UploadFile
) -> Path:
    """
    فایل صوتی دریافتی را با تاریخ و ساعت
    در پوشه data/audio ذخیره می‌کند.
    """

    now = datetime.now()

    timestamp = now.strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    suffix = Path(
        file.filename or ""
    ).suffix.lower()

    if not suffix:
        suffix = ".webm"

    filename = (
        f"{timestamp}{suffix}"
    )

    destination = AUDIO_PATH / filename

    content = await file.read()

    with open(
        destination,
        "wb"
    ) as audio_file:

        audio_file.write(content)

    return destination


# =========================================================
# دریافت فایل صوتی و ذخیره آن
# =========================================================

@app.post("/api/audio/upload")
async def upload_audio(
    file: UploadFile = File(...)
):
    """
    فایل صوتی را دریافت و در data/audio ذخیره می‌کند.
    """

    try:

        destination = await save_audio_file(
            file
        )

        return {
            "success": True,
            "message": "فایل صوتی با موفقیت ذخیره شد.",
            "filename": destination.name,
            "path": str(destination)
        }

    except Exception as error:

        print(
            f"Upload error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# =========================================================
# تبدیل نتیجه جلسه به متن قابل جستجوی Tag
# =========================================================

def _prepare_text_for_tag_suggestion(
    result
) -> str:
    """
    خروجی process_meeting را به متنی تبدیل می‌کند
    که Tag Suggestion Service بتواند آن را بررسی کند.

    process_meeting ممکن است:
        - String
        - Dictionary
        - سایر ساختارهای JSON

    برگرداند.

    در صورت Dictionary یا List،
    ساختار به JSON متنی تبدیل می‌شود.
    """

    if result is None:

        return ""


    if isinstance(
        result,
        str
    ):

        return result


    try:

        return json.dumps(
            result,
            ensure_ascii=False
        )

    except Exception:

        return str(result)


# =========================================================
# افزودن Tagهای پیشنهادی به نتیجه جلسه
# =========================================================

def _add_suggested_tags(
    result
):
    """
    Tagهای پیشنهادی را بر اساس Vocabulary
    به خروجی process_meeting اضافه می‌کند.

    نکته:

    این تابع هیچ تغییری در متن اصلی جلسه ایجاد نمی‌کند.

    فقط فیلد:

        tags

    را ایجاد یا به‌روزرسانی می‌کند.
    """

    searchable_text = (
        _prepare_text_for_tag_suggestion(
            result
        )
    )


    if not searchable_text.strip():

        return result


    tags = suggest_tags(
        searchable_text
    )


    # -----------------------------------------------------
    # اگر نتیجه اصلی Dictionary باشد
    # -----------------------------------------------------

    if isinstance(
        result,
        dict
    ):

        result["tags"] = tags

        return result


    # -----------------------------------------------------
    # اگر نتیجه String باشد
    # -----------------------------------------------------

    return {
        "content": result,
        "tags": tags
    }


# =========================================================
# پردازش کامل جلسه
# =========================================================

@app.post("/api/audio/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):
    """
    پردازش کامل جلسه:

    Audio
        ↓
    Whisper
        ↓
    Text Cleaning
        ↓
    Transcript Correction
        ↓
    GapGPT Analysis
        ↓
    Markdown / Result
        ↓
    Tag Suggestion
        ↓
    API Response
    """

    try:

        # -------------------------------------------------
        # ذخیره فایل صوتی
        # -------------------------------------------------

        audio_path = await save_audio_file(
            file
        )

        print(
            f"\nProcessing meeting: {audio_path}"
        )


        # -------------------------------------------------
        # اجرای Pipeline کامل جلسه
        # -------------------------------------------------

        result = process_meeting(
            str(audio_path)
        )


        print(
            "\nMeeting processing completed."
        )


        # -------------------------------------------------
        # پیشنهاد Tag بر اساس Vocabulary
        # -------------------------------------------------

        try:

            result = _add_suggested_tags(
                result
            )

            print(
                "\nTag suggestion completed."
            )

            if isinstance(
                result,
                dict
            ):

                print(
                    "Suggested tags:",
                    result.get(
                        "tags",
                        []
                    )
                )


        except Exception as tag_error:

            # ------------------------------------------------
            # خطای Tag نباید کل Pipeline جلسه را خراب کند.
            # ------------------------------------------------

            print(
                f"\nTag suggestion error: {tag_error}"
            )

            if isinstance(
                result,
                dict
            ):

                result["tags"] = []


        # -------------------------------------------------
        # پاسخ API
        # -------------------------------------------------

        return {
            "success": True,
            "filename": audio_path.name,
            "result": result
        }


    except Exception as error:

        print(
            f"Meeting processing error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# =========================================================
# ذخیره تغییرات صورتجلسه
# =========================================================

@app.post("/api/meeting/save")
async def save_meeting(
    request: MeetingSaveRequest
):
    """
    ذخیره نسخه ویرایش‌شده صورتجلسه.

    Frontend
        ↓
    POST /api/meeting/save
        ↓
    meeting_report.md
    """

    try:

        content = request.content


        # -------------------------------------------------
        # بررسی محتوای ارسالی
        # -------------------------------------------------

        if not content or not content.strip():

            raise HTTPException(
                status_code=400,
                detail="محتوای صورتجلسه خالی است."
            )


        # -------------------------------------------------
        # ذخیره واقعی فایل Markdown
        # -------------------------------------------------

        with open(
            MEETING_REPORT_FILE,
            "w",
            encoding="utf-8"
        ) as markdown_file:

            markdown_file.write(
                content
            )


        print(
            f"\nMeeting report saved: {MEETING_REPORT_FILE}"
        )


        # -------------------------------------------------
        # پاسخ موفق
        # -------------------------------------------------

        return {
            "success": True,
            "message": "تغییرات صورتجلسه با موفقیت ذخیره شد.",
            "filename": MEETING_REPORT_FILE.name
        }


    except HTTPException:
        raise


    except Exception as error:

        print(
            f"Meeting save error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )