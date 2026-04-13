from __future__ import annotations

from dataclasses import dataclass

from dotenv import load_dotenv
import os
from pathlib import Path

from utils.debug_log import dbg


# #region agent log
dbg(
    "H1",
    "config.py:import",
    "Module import: about to load dotenv",
    data={
        "cwd": os.getcwd(),
        "has_dotenv_file_in_cwd": Path(".env").exists(),
        "has_env_example_in_cwd": Path(".env.example").exists(),
    },
)
# #endregion

_DOTENV_PATH = Path(__file__).resolve().with_name(".env")
load_dotenv(dotenv_path=_DOTENV_PATH, override=False)

# #region agent log
dbg(
    "H1",
    "config.py:load_dotenv",
    "Dotenv load attempted",
    data={
        "dotenv_path": str(_DOTENV_PATH),
        "dotenv_exists": _DOTENV_PATH.exists(),
        "bot_token_present": bool(os.getenv("BOT_TOKEN")),
        "ym_token_present": bool(os.getenv("YM_TOKEN")),
    },
)
# #endregion


@dataclass(frozen=True)
class Config:
    bot_token: str
    ym_token: str | None
    proxy_url: str | None


def load_config() -> Config:
    # #region agent log
    dbg(
        "H2",
        "config.py:load_config",
        "Reading env vars",
        data={
            "cwd": os.getcwd(),
            "dotenv_path": str(_DOTENV_PATH),
            "dotenv_exists": _DOTENV_PATH.exists(),
            "bot_token_present": bool(os.getenv("BOT_TOKEN")),
            "ym_token_present": bool(os.getenv("YM_TOKEN")),
        },
    )
    # #endregion

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("Не найден BOT_TOKEN в .env (или переменных окружения).")

    ym_token = os.getenv("YM_TOKEN")
    ym_token = ym_token.strip() if ym_token else None

    proxy_url = os.getenv("PROXY_URL")
    proxy_url = proxy_url.strip() if proxy_url else None

    return Config(bot_token=bot_token, ym_token=ym_token, proxy_url=proxy_url)
