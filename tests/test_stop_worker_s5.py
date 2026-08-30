"""S5/S6 Stop worker during in-progress _work (CR-QA-1, A12/A25/F38/F39).

Existing A12/A25/F38 pause the worker then stop. Live QA caught a running
fetch job whose _work continued after confirm and stored succeeded. These
tests require Stop worker confirm to apply S5 immediately even when _work
is still inside fetch or the item loop.
"""

from __future__ import annotations

from tests.conftest import spoken_remark
from tests.test_spec_v7 import _form, _html, _seed


def _s9(j):
    return (
        int(j["fetched"] or 0)
        == int(j["written"] or 0)
        + int(j["updated"] or 0)
        + int(j["unchanged"] or 0)
        + int(j["quarantined"] or 0)
        + int(j["fetch_fail"] or 0)
    )


def test_stop_worker_confirm_during_in_progress_fetch_stores_failed_worker_lost(env):
    """Stop worker confirm while _work is in fetch: stored failed/worker_lost.

    Fetch returns items that would have been clean. They must not be written
    clean and must not finish as succeeded (the live QA hole).
    """
    e, c = env.engine, env.client
    _seed(e)
    items = [
        spoken_remark(locator="s5-a", text="Would have been clean A"),
        spoken_remark(locator="s5-b", text="Would have been clean B"),
    ]
    inner = e.fetch

    class StopThenReturn:
        def fetch(self, source, job_type, params):
            r = _form(c, "/worker/stop", confirm="1")
            assert r.status_code != 500
            return list(items)

    e.fetch = StopThenReturn()
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    jid = r.job["id"]
    e.drain()
    e.fetch = inner

    j = e.get_job(jid)
    assert j["status"] == "failed"
    assert j["error"] == "worker_lost"
    assert not any(x["status"] == "running" for x in e.list_jobs())
    html = _html(c, "/")
    assert "not available" in html
    assert "Worker not available. New jobs sit queued. Nothing is executing." in html
    for path in ("/", "/control", "/records", "/quarantine"):
        page = _html(c, path)
        assert "Worker not available. New jobs sit queued. Nothing is executing." in page
        assert "not available" in page

    clean = e.search()
    assert not any(rec["record_id"] in ("s5-a", "s5-b") for rec in clean)
    q = [x for x in e.list_quarantine() if x["failed_rule"] == "job_stopped" and x.get("open")]
    locs = {x["locator"] for x in q}
    assert locs >= {"s5-a", "s5-b"}
    for item in q:
        if item["locator"] in ("s5-a", "s5-b"):
            assert item["reason"] == "field-fail"
            acc = e.accept_quarantine(item["id"], confirm=True)
            assert not acc.ok
    assert _s9(j)
    assert int(j["quarantined"] or 0) >= 2
    assert int(j["fetched"] or 0) == int(j["written"] or 0) + int(j["updated"] or 0) + int(
        j["unchanged"] or 0
    ) + int(j["quarantined"] or 0) + int(j["fetch_fail"] or 0)


def test_stop_worker_s6_stayed_clean_in_flight_job_stopped_s9(env):
    """If some clean already written under that job id, those stay (S6).

    Remaining fetched-not-yet-clean items are field-fail job_stopped, not
    left as other-or-none and not left clean. S9 holds.
    """
    e, c = env.engine, env.client
    _seed(e)
    items = [
        spoken_remark(locator="stay-1", text="Stayed clean under this job"),
        spoken_remark(locator="inflight-2", text="Still in flight"),
        spoken_remark(locator="inflight-3", text="Also in flight"),
    ]
    e.fetch.script("whitehouse_remarks", items)
    orig = e._process_item

    def wrapped(j, it, force):
        orig(j, it, force)
        if it.get("locator") == "stay-1" and e.worker_available:
            r = _form(c, "/worker/stop", confirm="1")
            assert r.status_code != 500

    e._process_item = wrapped
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    jid = r.job["id"]
    e.drain()
    e._process_item = orig

    j = e.get_job(jid)
    assert j["status"] == "failed"
    assert j["error"] == "worker_lost"
    assert not any(x["status"] == "running" for x in e.list_jobs())
    stayed = e.get_record("stay-1")
    assert stayed is not None
    assert stayed["job_id"] == jid
    assert e.get_record("inflight-2") is None
    assert e.get_record("inflight-3") is None
    q = [x for x in e.list_quarantine() if x.get("open") and x["failed_rule"] == "job_stopped"]
    qlocs = {x["locator"] for x in q}
    assert "inflight-2" in qlocs
    assert "inflight-3" in qlocs
    assert "stay-1" not in qlocs
    for item in q:
        if item["locator"] in ("inflight-2", "inflight-3"):
            assert item["reason"] == "field-fail"
    assert _s9(j)
    job_stopped_n = sum(1 for x in q if x["locator"] in ("inflight-2", "inflight-3"))
    assert job_stopped_n >= 2
    assert int(j["quarantined"] or 0) >= job_stopped_n


def test_start_worker_does_not_resume_worker_lost_from_in_progress_stop(env):
    """Start worker: pill available, banner gone, that worker_lost id is not resumed."""
    e, c = env.engine, env.client
    _seed(e)
    items = [spoken_remark(locator="lost-1", text="Must not resume as this job id")]
    inner = e.fetch

    class StopThenReturn:
        def fetch(self, source, job_type, params):
            e.stop_worker(confirm=True)
            return list(items)

    e.fetch = StopThenReturn()
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    jid = r.job["id"]
    e.drain()
    e.fetch = inner

    j = e.get_job(jid)
    assert j["status"] == "failed"
    assert j["error"] == "worker_lost"

    r_start = _form(c, "/worker/start")
    assert r_start.status_code != 500
    html = _html(c, "/")
    assert "available" in html
    assert "Worker not available. New jobs sit queued. Nothing is executing." not in html
    assert e.worker_available is True
    after = e.get_job(jid)
    assert after["status"] == "failed"
    assert after["error"] == "worker_lost"
    e.drain()
    still = e.get_job(jid)
    assert still["status"] == "failed"
    assert still["error"] == "worker_lost"
    assert still["status"] not in ("running", "succeeded", "succeeded_empty")
