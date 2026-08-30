"""Shared fixtures. Tests never hit the live network."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

ET = ZoneInfo("America/New_York")

SOURCES = [
    "whitehouse_remarks",
    "whitehouse_actions",
    "app",
    "factbase",
    "federal_register",
    "truth_social",
    "x_personal",
    "campaign",
    "books",
    "interviews",
    "legal",
]


class FetchError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass
class FetchedItem:
    locator: str
    text: str
    kind: str
    channel: str
    title: str = ""
    event_time: datetime | None = None
    published_time: datetime | None = None
    url: str = ""
    attributed: bool = True
    completeness: str = "full_transcript"
    outlet: str | None = None
    author_handle: str | None = None
    named_party: str | None = None
    topics: list[str] = field(default_factory=list)
    occasion: str | None = None
    act_type: str | None = None
    direction: str | None = None
    status: str | None = None
    related_remarks: list[str] = field(default_factory=list)
    people: list[str] = field(default_factory=list)
    phrases: list[str] = field(default_factory=list)
    audience: str | None = None
    delivery: str | None = None
    term: str | None = None
    fetch_failed: bool = False
    fetch_error: str | None = None


class ScriptedFetch:
    """Injectable fetch port. Tests never open sockets."""

    def __init__(self):
        self._map: dict = {}
        self.calls: list = []

    def script(self, source: str, items):
        self._map[source] = list(items)

    def script_error(self, source: str, message: str):
        self._map[source] = FetchError(message)

    def fetch(self, source: str, job_type: str, params: dict):
        self.calls.append({"source": source, "job_type": job_type, "params": dict(params or {})})
        v = self._map.get(source, [])
        if isinstance(v, FetchError):
            raise v
        return list(v)


def et(y, m, d, hh=9, mm=0):
    return datetime(y, m, d, hh, mm, tzinfo=ET)


def utc(*args):
    if len(args) == 1 and isinstance(args[0], datetime):
        dt = args[0]
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return datetime(*args, tzinfo=timezone.utc)


def spoken_remark(**kw) -> FetchedItem:
    defaults = dict(
        locator="wh-r-1",
        text="Thank you. We will build it.",
        kind="remark",
        channel="spoken",
        title="Remarks",
        event_time=datetime(2025, 3, 15, 16, 0, tzinfo=timezone.utc),
        url="https://www.whitehouse.gov/remarks/r1",
        completeness="full_transcript",
        attributed=True,
        topics=["trade"],
        occasion="press_conference",
        term="2025_present",
    )
    defaults.update(kw)
    return FetchedItem(**defaults)


def social_post(**kw) -> FetchedItem:
    defaults = dict(
        locator="ts-1",
        text="A post from the official account.",
        kind="social",
        channel="written_social",
        title="Post",
        published_time=datetime(2025, 3, 15, 18, 0, tzinfo=timezone.utc),
        url="https://truthsocial.com/@realDonaldTrump/1",
        author_handle="realDonaldTrump",
        completeness="full_transcript",
        attributed=True,
        topics=["trade"],
        term="2025_present",
    )
    defaults.update(kw)
    return FetchedItem(**defaults)


def book_item(**kw) -> FetchedItem:
    defaults = dict(
        locator="book-1",
        text="Chapter one of a signed book.",
        kind="writing",
        channel="other",
        title="A Book",
        event_time=datetime(2023, 6, 1, 12, 0, tzinfo=timezone.utc),
        url="https://example.com/book",
        completeness="excerpt",
        attributed=True,
        topics=["trade"],
        term="2021_2024",
    )
    defaults.update(kw)
    return FetchedItem(**defaults)


def decision_item(**kw) -> FetchedItem:
    defaults = dict(
        locator="eo-1",
        text="An executive order.",
        kind="decision",
        channel="written_official",
        title="EO",
        event_time=datetime(2025, 1, 21, 15, 0, tzinfo=timezone.utc),
        url="https://www.federalregister.gov/eo/1",
        completeness="full_transcript",
        attributed=True,
        act_type="executive_order",
        direction="restrict",
        status="signed",
        topics=["trade"],
        term="2025_present",
    )
    defaults.update(kw)
    return FetchedItem(**defaults)


@pytest.fixture
def clock():
    box = SimpleNamespace(now=datetime(2026, 8, 26, 15, 0, tzinfo=ET))  # Wed after 09:00

    def now():
        n = box.now
        if n.tzinfo is None:
            n = n.replace(tzinfo=ET)
        return n.astimezone(timezone.utc)

    now.box = box
    return now


@pytest.fixture
def fetch():
    return ScriptedFetch()


@pytest.fixture
def engine(tmp_path, fetch, clock):
    from ptrp.engine import Engine

    eng = Engine(db_path=tmp_path / "ptrp.sqlite", fetch=fetch, clock=clock)
    eng.boot()
    return eng


@pytest.fixture
def client(engine):
    from ptrp.app import create_app

    app = create_app(engine)
    return TestClient(app)


@pytest.fixture
def env(engine, client, fetch, clock, tmp_path):
    return SimpleNamespace(
        engine=engine,
        client=client,
        fetch=fetch,
        clock=clock,
        db=tmp_path / "ptrp.sqlite",
        tmp=tmp_path,
    )
