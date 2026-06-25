from collections.abc import Callable
import threading

from sqlalchemy.orm import Session

from .database import SessionLocal
from .github_trending import ingest_github_trending


trending_ingestion_lock = threading.Lock()


class TrendingIngestionScheduler:
    def __init__(
        self,
        session_factory: Callable[[], Session] = SessionLocal,
        ingest: Callable[[Session, str, str | None, int | None], object] = ingest_github_trending,
        interval_seconds: int = 24 * 60 * 60,
        period: str = "daily",
        language: str | None = None,
        limit: int | None = 20,
    ) -> None:
        self.session_factory = session_factory
        self.ingest = ingest
        self.interval_seconds = interval_seconds
        self.period = period
        self.language = language
        self.limit = limit
        self._running = False
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def run_once(self) -> bool:
        if self._running:
            return False
        if not trending_ingestion_lock.acquire(blocking=False):
            return False

        self._running = True
        db = self.session_factory()
        try:
            self.ingest(db, self.period, self.language, self.limit)
            return True
        finally:
            db.close()
            self._running = False
            trending_ingestion_lock.release()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _run_loop(self) -> None:
        while not self._stop_event.wait(self.interval_seconds):
            self.run_once()
