import logging
from os import environ

import click
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pocketbase import PocketBase, utils
from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

START_MSG = (
    "Здравствуйте, дорогой гость!\n"
    + "Этот бот создан студентами РУТ (МИИТ) для помощи посетителям музея. "
    + "Чтобы самостоятельно ознакомиться с экспозицией, обратите внимание на пронумерованные экспонаты. "
    + "Просто отправьте сюда номер интересующего вас экспоната и получите в ответ текстовый и аудиофайл с его описанием, "
    + "а также дополнительные материалы."
    + "\nКроме того, в описании к боту вы найдёте форму обратной связи, "
    + "через которую сможете оставить отзыв о работе нашего аудиогида и свои пожелания"
)

supported_tags = [
    "b",
    "strong",
    "i",
    "em",
    "u",
    "ins",
    "s",
    "strike",
    "del",
    "span",
    "tg-spoiler",
    "a",
    "tg-emoji",
    "code",
    "pre",
    "blockquote",
]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv()


def remove_unsupported_tags(html, supported_tags):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(True):
        if tag.name not in supported_tags:
            tag.unwrap()

    return str(soup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=START_MSG)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE, client: PocketBase):
    try:
        post = client.collection("posts").get_first_list_item(
            f"num={str(update.message.text)}"
        )

        post_title = post.title
        post_body = post.body
        post_media = post.media
        media_caption = post.caption
        post_audio = post.audio

        logging.info(
            f"{post}\n{post_title}\n{post_body}\n{post_media}\n{media_caption}\n{post_audio}"
        )

        post_body = remove_unsupported_tags(post_body, supported_tags)
        media_caption = remove_unsupported_tags(media_caption, supported_tags)
    except utils.ClientResponseError:
        post_body = "Похоже, зааписи с таким номером нет. Попробуйте другой номер😅"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="<b>" + post_title + "</b>",
        parse_mode=constants.ParseMode.HTML,
    )

    if post_media:
        for index, media in enumerate(post_media):
            photo = client.get_file_url(post, media, {})
            if index == 0 and media_caption:
                caption = media_caption
            else:
                caption = ""
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=caption,
                parse_mode=constants.ParseMode.HTML,
            )

    if post_audio:
        audio = client.get_file_url(post, post_audio, {})
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=audio)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=post_body,
        parse_mode=constants.ParseMode.HTML,
    )


@click.command()
@click.version_option()
@click.option(
    "--token",
    prompt=False,
    default=lambda: environ.get("TOKEN", ""),  # Токен из среды или .env
)
@click.option(
    "--api", prompt=False, default=lambda: environ.get("API", "http://127.0.0.1:8090")
)
def main(token: str, api: str) -> None:
    client = PocketBase(api)

    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler("start", start)
    echo_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND),
        lambda update, context: echo(update, context, client),
    )

    application.add_handler(start_handler)
    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
