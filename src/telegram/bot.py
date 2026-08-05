from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)


TOKEN = "8878782975:AAGhg8z86YR5bauiSK0sKGVoZxGVc_84-mI"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\n"
        "من دستیار هوشمند جلسات MIP هستم."
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    await update.message.reply_text(
        f"دریافت شد:\n{text}"
    )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT,
            echo
        )
    )

    print("Bot started...")

    app.run_polling()


if __name__ == "__main__":
    main()