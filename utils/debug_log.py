from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


_LOG_PATH = Path("debug-684663.log")


def dbg(hypothesis_id: str, location: str, message: str, data: dict[str, Any] | None = None, run_id: str = "pre-fix") -> None:
    """
    NDJSON debug logger for Cursor DEBUG MODE.
    Никогда не логируем секреты (BOT_TOKEN/YM_TOKEN и т.п.).
    """
    payload = {
        "sessionId": "684663",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time() * 1000),
    }
    try:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # Never break app due to debug logging
        pass

