from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.types import Message

from utils.formatting import render_track_html
from utils.parse_yandex_music import extract_track_ids_from_text
from utils.yandex_music_client import YandexMusicService
from handlers.ui import main_reply_kb


logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text.in_({"Ещё трек", "Помощь"}))
async def helper_buttons(message: Message) -> None:
    if message.text == "Ещё трек":
        await message.answer("Пришли ссылку на трек Яндекс.Музыки.", reply_markup=main_reply_kb())
        return
    await message.answer(
        "Отправь ссылку(и) на Яндекс.Музыку — я вытащу информацию о треке(ах).",
        reply_markup=main_reply_kb(),
    )


@router.message(F.text)
async def handle_text(message: Message, ym: YandexMusicService) -> None:
    text = message.text or ""
    parsed = extract_track_ids_from_text(text)
    if not parsed:
        await message.answer(
            "Не вижу ссылку на трек Яндекс.Музыки.\n"
            "Пример: <code>https://music.yandex.ru/track/123456</code>",
            reply_markup=main_reply_kb(),
        )
        return

    # Если ссылок много — не блокируем UX: отвечаем по мере обработки
    for item in parsed:
        try:
            info = await ym.get_track_info(item.track_id)
        except LookupError:
            await message.answer(
                f"Трек <code>{item.track_id}</code> не найден или недоступен.",
                reply_markup=main_reply_kb(),
            )
            continue
        except Exception:
            logger.exception("Failed to fetch track info: track_id=%s url=%s", item.track_id, item.source_url)
            await message.answer(
                "Не получилось получить данные о треке. Попробуй позже или пришли другую ссылку.",
                reply_markup=main_reply_kb(),
            )
            continue

        await message.answer(render_track_html(info), disable_web_page_preview=True, reply_markup=main_reply_kb())

