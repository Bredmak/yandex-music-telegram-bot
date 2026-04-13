from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from config import load_config
from handlers import start_router, music_router
from utils.debug_log import dbg
from utils.yandex_music_client import YandexMusicService


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


async def main() -> None:
    setup_logging()
    cfg = load_config()

    # #region agent log
    dbg(
        "H3",
        "main.py:startup",
        "Python/venv/proxy diagnostics",
        data={
            "sys_executable": sys.executable,
            "sys_version": sys.version.split()[0],
            "proxy_set": bool(cfg.proxy_url),
            "proxy_scheme": (cfg.proxy_url.split(":", 1)[0].lower() if cfg.proxy_url else None),
        },
    )
    # #endregion

    if cfg.proxy_url:
        try:
            import aiohttp_socks  # noqa: F401
            # #region agent log
            dbg("H4", "main.py:proxy", "aiohttp_socks import OK")
            # #endregion
        except Exception as e:
            # #region agent log
            dbg("H4", "main.py:proxy", "aiohttp_socks import FAILED", data={"exc_type": type(e).__name__})
            # #endregion
            raise RuntimeError(
                "У тебя задан PROXY_URL, но не установлен пакет aiohttp-socks в ЭТОМ Python.\n"
                "Установи зависимости строго в venv так:\n"
                "  .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt\n"
            ) from e

    def build_bot(proxy_url: str | None) -> Bot:
        session = AiohttpSession(proxy=proxy_url) if proxy_url else AiohttpSession()
        return Bot(
            token=cfg.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            session=session,
        )

    bot = build_bot(cfg.proxy_url)
    dp = Dispatcher()

    ym = YandexMusicService(cfg.ym_token)
    await ym.init()

    dp["ym"] = ym  # dependency injection for handlers

    dp.include_router(start_router)
    dp.include_router(music_router)

    logger = logging.getLogger(__name__)

    async def run(bot_to_run: Bot) -> None:
        await bot_to_run.set_my_commands([BotCommand(command="start", description="Запуск и инструкция")])
        logger.info("Bot started.")
        await dp.start_polling(bot_to_run)

    try:
        try:
            await run(bot)
        except Exception as e:
            # Частая ситуация: PROXY_URL задан, но локальный прокси не запущен/не доступен.
            err_text = str(e)
            looks_like_proxy_issue = (
                cfg.proxy_url is not None
                and (
                    "Couldn't connect to proxy" in err_text
                    or "ProxyConnectionError" in type(e).__name__
                    or "aiohttp_socks" in err_text
                )
            )

            # #region agent log
            dbg(
                "H5",
                "main.py:run",
                "Run failed",
                data={
                    "exc_type": type(e).__name__,
                    "proxy_set": bool(cfg.proxy_url),
                    "looks_like_proxy_issue": looks_like_proxy_issue,
                },
            )
            # #endregion

            if looks_like_proxy_issue:
                logger.error("Proxy connection failed (%s). Trying without proxy...", type(e).__name__)
                await bot.session.close()
                bot = build_bot(proxy_url=None)
                try:
                    await run(bot)
                    return
                except Exception as e2:
                    # Не получилось и без прокси — отдадим понятную подсказку.
                    raise RuntimeError(
                        "Прокси из PROXY_URL недоступен (соединение отклонено), а без прокси подключиться тоже не удалось.\n"
                        "Решение:\n"
                        "- либо запусти прокси, который указан в PROXY_URL\n"
                        "- либо удали/закомментируй PROXY_URL в .env и запусти снова\n"
                        "- либо укажи рабочий PROXY_URL (HTTP/SOCKS5)\n"
                    ) from e2
            raise
    except (OSError, TelegramNetworkError) as e:
        logger.exception("Network error while starting bot: %s", e)
        raise RuntimeError(
            "Не удалось подключиться к Telegram API (сетевой таймаут/блокировка).\n"
            "Если Telegram заблокирован в сети — добавь прокси в .env:\n"
            "PROXY_URL=socks5://user:pass@host:port  (или http://host:port)\n"
        ) from e
    finally:
        # Чтобы не оставлять незакрытые aiohttp-сессии при любых исключениях
        try:
            await bot.session.close()
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())

