__title__ = "audioguide-bot"
__description__ = "Телеграм бот для аудиогида."
__version__ = "0.1.0"

import click
from os import environ
from click.termui import prompt
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


@click.command()
@click.version_option()
@click.option(
    "--token", prompt=True, default=lambda: environ.get("TOKEN", "")
)
def main(token: str) -> None:
    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()


if __name__ == "__main__":
    load_dotenv()
    main()
