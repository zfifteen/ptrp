"""S5 live fetch path: HTML POST /jobs then POST /worker/stop while running.

Prior PR 5 tests called stop from inside a fetch mock on the same thread as
drain. Live QA used HTML Run incremental books, caught stored running, then
POST /worker/stop confirm=1. The live worker thread continued and stored
succeeded. CR-QA-1: a switch that only paints not available is a fail.
"""

from __future__ import annotations

import socket
import threading
import time

import httpx
import uvicorn

from tests.conftest import book_item
from tests.test_spec_v7 import _seed


def test_html_stop_during_running_fetch_cannot_store_succeeded(env):
    """HTML POST /jobs incremental (books) then POST /worker/stop confirm=1
    while stored status is running.

    Even if _work continues and would finish all writes after stop, stored
    status MUST be failed with error worker_lost. It MUST NOT later become
    succeeded. After stop, that job id writes no further clean (S6.4).
    Banner present; pill not available; no running row. Start worker: pill
    available, banner gone, that worker_lost id is NOT resumed.
    """
    e, c = env.engine, env.client
    _seed(e)
    started = threading.Event()
    release = threading.Event()
    items = [
        book_item(locator=f"s5-live-{i}", text=f"Signed chapter {i} of a book.")
        for i in range(5)
    ]
    inner = e.fetch

    class LiveFetch:
        def fetch(self, source, job_type, params):
            started.set()
            release.wait(timeout=12)
            return list(items)

    e.fetch = LiveFetch()

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    app = c.app
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

    base = f"http://127.0.0.1:{port}"
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
    # If Stop cannot apply S5 until _work finishes (blocked event loop),
    # release fetch so _work would write all items and store succeeded.
    time.sleep(0.3)
    if not stop_returned.is_set():
        release.set()
    stop_t.join(timeout=15)
    release.set()
    jobs_t.join(timeout=15)

    try:
        j = e.get_job(jid)
        assert j["status"] == "failed", j
        assert j["error"] == "worker_lost", j
        assert j["status"] != "succeeded"
        assert not any(x["status"] == "running" for x in e.list_jobs())

        html = httpx.get(f"{base}/", timeout=10.0).text
        assert "not available" in html
        assert "Worker not available. New jobs sit queued. Nothing is executing." in html
        for path in ("/", "/control", "/records", "/quarantine"):
            page = httpx.get(f"{base}{path}", timeout=10.0).text
            assert "Worker not available. New jobs sit queued. Nothing is executing." in page
            assert "not available" in page

        q = [x for x in e.list_quarantine() if x.get("open") and x["failed_rule"] == "job_stopped"]
        qlocs = {x["locator"] for x in q}
        for i in range(5):
            loc = f"s5-live-{i}"
            rec = e.get_record(loc)
            if rec is None:
                assert loc in qlocs
            else:
                # S6: clean already written under this job id stay; no further
                # clean writes after the job left running.
                assert rec["job_id"] == jid

        httpx.post(f"{base}/worker/start", timeout=10.0)
        html = httpx.get(f"{base}/", timeout=10.0).text
        assert "available" in html
        assert "Worker not available. New jobs sit queued. Nothing is executing." not in html
        still = e.get_job(jid)
        assert still["status"] == "failed"
        assert still["error"] == "worker_lost"
        e.drain()
        still = e.get_job(jid)
        assert still["status"] == "failed"
        assert still["error"] == "worker_lost"
        assert still["status"] not in ("running", "succeeded", "succeeded_empty")
    finally:
        e.fetch = inner
        server.should_exit = True
        try:
            httpx.get(f"{base}/", timeout=1.0)
        except Exception:
            pass
        serve_t.join(timeout=5)
