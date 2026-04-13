from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from handlers.ui import main_reply_kb


router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    text = (
        "<b>Привет!</b>\n\n"
        "Пришли мне ссылку на трек из <b>Яндекс.Музыки</b>, например:\n"
        "<code>https://music.yandex.ru/track/123456</code>\n"
        "или альбомную ссылку вида:\n"
        "<code>https://music.yandex.ru/album/111/track/222</code>\n\n"
        "Можно отправить <b>несколько ссылок</b> в одном сообщении — обработаю каждую."
    )
    await message.answer(text, reply_markup=main_reply_kb())

