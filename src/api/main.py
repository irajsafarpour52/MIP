from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


# -----------------------------------------
# FastAPI Application
# -----------------------------------------

app = FastAPI(
    title="MIP",
    description="Meeting Intelligent Platform",
    version="1.0"
)


# -----------------------------------------
# Project Paths
# -----------------------------------------

BASE_DIR = Path(
    __file__
).resolve().parent.parent.parent

WEB_PATH = BASE_DIR / "src" / "web"


# -----------------------------------------
# Static Files
# -----------------------------------------

app.mount(
    "/web",
    StaticFiles(
        directory=WEB_PATH
    ),
    name="web"
)


# -----------------------------------------
# Home Page
# -----------------------------------------

@app.get("/")
def home():

    return FileResponse(
        WEB_PATH / "index.html"
    )