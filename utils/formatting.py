from __future__ import annotations

from html import escape

from utils.parse_yandex_music import format_mm_ss
from utils.yandex_music_client import TrackInfo


def render_track_html(info: TrackInfo) -> str:
    title = escape(info.title)
    artists = escape(info.artists)
    duration = escape(format_mm_ss(info.duration_ms))
    album = escape(info.album) if info.album else "—"
    year = str(info.year) if info.year else "—"
    url = escape(info.url)

    return (
        f"<b>{title}</b>\n"
        f"<i>{artists}</i>\n\n"
        f"<b>Длительность:</b> {duration}\n"
        f"<b>Альбом:</b> {album}\n"
        f"<b>Год:</b> {year}\n"
        f"<b>Ссылка:</b> <a href=\"{url}\">{url}</a>"
    )

