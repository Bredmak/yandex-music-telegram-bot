from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_reply_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ещё трек")],
            [KeyboardButton(text="Помощь")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Вставь ссылку на Яндекс.Музыку…",
    )

