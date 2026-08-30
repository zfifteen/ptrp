"""F32/A22/F35 leftover: in-flight on worker_lost must be job_stopped (S6/S9).

Live hole (QA-F32, QA-A22, QA-F35): HTML Run incremental books force_refetch,
POST /worker/stop confirm=1 while stored running. Job stored failed/worker_lost
(S5 holds) but fetched items not yet written under that job were not quarantined.
fetched=N written=0 quarantined=0 — S9 leftover, job_stopped n=0.

Prior clean locators from an earlier job stay (S6.5). They are still in-flight
for THIS job until written under this job id (S6.2). SHA f57422f is not a close.
"""

from __future__ import annotations

import socket
import threading
import time

import httpx
import uvicorn

from tests.conftest import book_item
from tests.test_spec_v7 import _seed


def _s9(j):
    return (
        int(j["fetched"] or 0)
        == int(j["written"] or 0)
        + int(j["updated"] or 0)
        + int(j["unchanged"] or 0)
        + int(j["quarantined"] or 0)
        + int(j["fetch_fail"] or 0)
    )


def _job_stopped_open(e, locators):
    want = set(locators)
    rows = [
        x
        for x in e.list_quarantine()
        if x.get("open") and x["failed_rule"] == "job_stopped" and x["locator"] in want
    ]
    return rows


def _serve(app):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    config = uvicorn.Config(
        app, host="127.0.0.1", port=port, log_level="error", lifespan="off"
    )
    server = uvicorn.Server(config)
    serve_t = threading.Thread(target=server.run, daemon=True)
    serve_t.start()
    deadline = time.time() + 5
    while time.time() < deadline and not getattr(server, "started", False):
        time.sleep(0.05)
    assert getattr(server, "started", False), "test uvicorn did not start"
    return server, serve_t, f"http://127.0.0.1:{port}"


def _shutdown(server, serve_t, base):
    server.should_exit = True
    try:
        httpx.get(f"{base}/", timeout=1.0)
    except Exception:
        pass
    serve_t.join(timeout=5)


def test_html_stop_during_running_force_refetch_inflight_are_job_stopped_s9(env):
    """HTML POST incremental books force_refetch, stop while stored running.

    Locators already clean from an earlier job (live books n=20). Fetch returns
    them; none written under this job id. Stop must store failed/worker_lost
    and quarantine those fetched-not-yet-clean items as field-fail job_stopped.
    S9: fetched = written+updated+unchanged+quarantined+fetch_fail. If none
    written clean, quarantined accounts for fetched. Accept disabled. Not a
    silent drop. Not a sixth uncounted bucket. Earlier clean records stay.
    """
    e, c = env.engine, env.client
    _seed(e)
    n = 5
    locs = [f"s9-book-{i}" for i in range(n)]
    items = [
        book_item(locator=loc, text=f"Signed chapter {i} of a book.")
        for i, loc in enumerate(locs)
    ]
    e.fetch.script("books", items)
    prior = e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    prior_j = e.get_job(prior.job["id"])
    assert prior_j["status"] == "succeeded"
    for loc in locs:
        rec = e.get_record(loc)
        assert rec is not None
        assert rec["job_id"] == prior.job["id"]

    started = threading.Event()
    release = threading.Event()
    inner = e.fetch

    class LiveFetch:
        def fetch(self, source, job_type, params):
            started.set()
            release.wait(timeout=12)
            return list(items)

    e.fetch = LiveFetch()
    server = serve_t = base = None
    try:
        server, serve_t, base = _serve(c.app)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        def post_jobs():
            httpx.post(
                f"{base}/jobs",
                data={"type": "incremental", "source": "books", "force_refetch": "on"},
                headers=headers,
                timeout=20.0,
            )

        jobs_t = threading.Thread(target=post_jobs)
        jobs_t.start()
        assert started.wait(timeout=8), "fetch did not start; job never reached running fetch"
        jid = None
        deadline = time.time() + 5
        while time.time() < deadline:
            running = [j for j in e.list_jobs() if j["status"] == "running"]
            if running:
                jid = running[0]["id"]
                break
            time.sleep(0.05)
        assert jid, "stored status was not running during HTML POST /jobs fetch"
        assert jid != prior.job["id"]

        stop_returned = threading.Event()

        def post_stop():
            httpx.post(
                f"{base}/worker/stop",
                data={"confirm": "1"},
                headers=headers,
                timeout=20.0,
            )
            stop_returned.set()

        stop_t = threading.Thread(target=post_stop)
        stop_t.start()
        time.sleep(0.3)
        if not stop_returned.is_set():
            release.set()
        stop_t.join(timeout=15)
        release.set()
        jobs_t.join(timeout=15)

        j = e.get_job(jid)
        assert j["status"] == "failed", j
        assert j["error"] == "worker_lost", j
        assert not any(x["status"] == "running" for x in e.list_jobs())

        html = httpx.get(f"{base}/", timeout=10.0).text
        assert "not available" in html
        assert "Worker not available. New jobs sit queued. Nothing is executing." in html

        assert int(j["written"] or 0) == 0
        assert int(j["updated"] or 0) == 0
        assert int(j["unchanged"] or 0) == 0
        assert int(j["fetched"] or 0) == n
        assert _s9(j), j
        assert int(j["quarantined"] or 0) == n

        q = _job_stopped_open(e, locs)
        qlocs = {x["locator"] for x in q}
        assert qlocs == set(locs)
        for item in q:
            assert item["reason"] == "field-fail"
            acc = e.accept_quarantine(item["id"], confirm=True)
            assert not acc.ok

        for loc in locs:
            rec = e.get_record(loc)
            assert rec is not None
            assert rec["job_id"] == prior.job["id"]

        httpx.post(f"{base}/worker/start", timeout=10.0)
        still = e.get_job(jid)
        assert still["status"] == "failed"
        assert still["error"] == "worker_lost"
        e.drain()
        still = e.get_job(jid)
        assert still["status"] == "failed"
        assert still["error"] == "worker_lost"
        assert still["status"] not in ("running", "succeeded", "succeeded_empty")
        assert _s9(still)
    finally:
        e.fetch = inner
        if server is not None:
            _shutdown(server, serve_t, base)


def test_html_stop_after_stayed_clean_remaining_inflight_job_stopped_s9(env):
    """Some clean already written under this job id stay (S6.1). Remaining
    fetched-not-yet-clean items — including locators already clean from an
    earlier job — are field-fail job_stopped. S9 holds. worker_lost (S5).
    """
    e, c = env.engine, env.client
    _seed(e)
    prior_items = [
        book_item(locator="s6-prior-2", text="Prior clean two"),
        book_item(locator="s6-prior-3", text="Prior clean three"),
    ]
    e.fetch.script("books", prior_items)
    prior = e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    assert e.get_record("s6-prior-2")["job_id"] == prior.job["id"]
    assert e.get_record("s6-prior-3")["job_id"] == prior.job["id"]

    items = [
        book_item(locator="s6-stay-1", text="Stayed clean under this job"),
        book_item(locator="s6-prior-2", text="Prior clean two"),
        book_item(locator="s6-prior-3", text="Prior clean three"),
    ]
    inner_fetch = e.fetch
    e.fetch.script("books", items)
    orig_process = e._process_item
    stop_after_stay = threading.Event()
    release_rest = threading.Event()

    def wrapped(j, it, force):
        orig_process(j, it, force)
        if it.get("locator") == "s6-stay-1" and e.worker_available:
            stop_after_stay.set()
            release_rest.wait(timeout=12)

    e._process_item = wrapped
    server = serve_t = base = None
    try:
        server, serve_t, base = _serve(c.app)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        def post_jobs():
            httpx.post(
                f"{base}/jobs",
                data={"type": "incremental", "source": "books", "force_refetch": "on"},
                headers=headers,
                timeout=20.0,
            )

        jobs_t = threading.Thread(target=post_jobs)
        jobs_t.start()
        assert stop_after_stay.wait(timeout=8), "first clean write did not happen"
        jid = None
        deadline = time.time() + 5
        while time.time() < deadline:
            running = [j for j in e.list_jobs() if j["status"] == "running"]
            if running:
                jid = running[0]["id"]
                break
            time.sleep(0.05)
        assert jid, "stored status was not running after stayed clean write"

        r_stop = httpx.post(
            f"{base}/worker/stop",
            data={"confirm": "1"},
            headers=headers,
            timeout=20.0,
        )
        assert r_stop.status_code != 500
        release_rest.set()
        jobs_t.join(timeout=15)

        j = e.get_job(jid)
        assert j["status"] == "failed", j
        assert j["error"] == "worker_lost", j
        stayed = e.get_record("s6-stay-1")
        assert stayed is not None
        assert stayed["job_id"] == jid
        prior2 = e.get_record("s6-prior-2")
        prior3 = e.get_record("s6-prior-3")
        assert prior2 is not None
        assert prior3 is not None
        assert prior2["job_id"] == prior.job["id"]
        assert prior3["job_id"] == prior.job["id"]

        q = _job_stopped_open(e, ("s6-prior-2", "s6-prior-3", "s6-stay-1"))
        qlocs = {x["locator"] for x in q}
        assert "s6-prior-2" in qlocs
        assert "s6-prior-3" in qlocs
        assert "s6-stay-1" not in qlocs
        for item in q:
            assert item["reason"] == "field-fail"
            acc = e.accept_quarantine(item["id"], confirm=True)
            assert not acc.ok

        assert _s9(j), j
        assert int(j["written"] or 0) + int(j["updated"] or 0) >= 1
        assert int(j["quarantined"] or 0) >= 2
        assert int(j["fetched"] or 0) == 3
    finally:
        e._process_item = orig_process
        e.fetch = inner_fetch
        release_rest.set()
        if server is not None:
            _shutdown(server, serve_t, base)
