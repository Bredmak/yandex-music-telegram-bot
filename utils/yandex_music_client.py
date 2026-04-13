from __future__ import annotations

from dataclasses import dataclass
import logging

from yandex_music import ClientAsync


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrackInfo:
    track_id: int
    title: str
    artists: str
    duration_ms: int | None
    album: str | None
    year: int | None
    url: str


class YandexMusicService:
    def __init__(self, ym_token: str | None):
        self._token = ym_token
        self._client: ClientAsync | None = None

    async def init(self) -> None:
        if self._client is not None:
            return
        self._client = ClientAsync(self._token)
        await self._client.init()
        logger.info("Yandex Music client initialized (token=%s).", "yes" if self._token else "no")

    async def get_track_info(self, track_id: int) -> TrackInfo:
        if self._client is None:
            raise RuntimeError("YandexMusicService not initialized. Call init() first.")

        tracks = await self._client.tracks(track_id)
        if not tracks:
            raise LookupError("Трек не найден или недоступен.")

        t = tracks[0]
        title = (t.title or "").strip() or f"Track {track_id}"
        artists = ", ".join([a.name for a in (t.artists or []) if a and a.name]) or "—"
        duration_ms = getattr(t, "duration_ms", None)

        album_title = None
        year = None
        albums = getattr(t, "albums", None) or []
        if albums:
            a0 = albums[0]
            album_title = (getattr(a0, "title", None) or "").strip() or None
            year = getattr(a0, "year", None)

        url = f"https://music.yandex.ru/track/{track_id}"

        return TrackInfo(
            track_id=track_id,
            title=title,
            artists=artists,
            duration_ms=duration_ms,
            album=album_title,
            year=year,
            url=url,
        )
