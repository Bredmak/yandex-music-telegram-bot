from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class ParsedTrack:
    track_id: int
    source_url: str


_URL_RE = re.compile(r"(https?://[^\s<>]+)", re.IGNORECASE)


def _normalize_url(url: str) -> str:
    return url.strip().strip("()[]<>.,!?:;\"'")


def _extract_track_id_from_path(path: str) -> int | None:
    # Examples:
    # /track/123
    # /album/456/track/123
    m = re.search(r"/track/(\d+)(?:/|$)", path)
    if m:
        return int(m.group(1))
    return None


def extract_track_ids_from_text(text: str) -> list[ParsedTrack]:
    """
    Находит ВСЕ ссылки в тексте и вытаскивает ID треков из ссылок Яндекс.Музыки.
    """
    found: list[ParsedTrack] = []
    for raw in _URL_RE.findall(text or ""):
        url = _normalize_url(raw)
        try:
            u = urlparse(url)
        except Exception:
            continue

        host = (u.netloc or "").lower()
        if "music.yandex." not in host:
            continue

        track_id = _extract_track_id_from_path(u.path or "")
        if track_id is None:
            continue

        found.append(ParsedTrack(track_id=track_id, source_url=url))

    # Уникализация с сохранением порядка
    uniq: dict[int, ParsedTrack] = {}
    for item in found:
        uniq.setdefault(item.track_id, item)
    return list(uniq.values())


def format_mm_ss(duration_ms: int | None) -> str:
    if not duration_ms or duration_ms < 0:
        return "—"
    total_seconds = duration_ms // 1000
    mm = total_seconds // 60
    ss = total_seconds % 60
    return f"{mm:02d}:{ss:02d}"
