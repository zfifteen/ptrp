"""DEF-1 QA-A3 / S9 leftover: succeeded incremental must not double-count.

Live hole (QA-A3, job 07844e48f44e): HTML incremental books, fetched=20 already
clean, ov-job showed fetched=20 written=0 updated=0 unchanged=20 quarantined=20
(20 != 40). job_stopped rows for that succeeded job were inserted AFTER
finished. Production background drain _work on a running job; the overlapping
_work then _abort_stopped_work after the job already succeeded and S6-quarantines
unchanged locators (S6 is for failed/cancelled/worker_lost only).

S9: fetched = written + updated + unchanged + quarantined + fetch_fail.
Succeeded job must not list the same locators as both unchanged and
quarantined. Earlier worker_lost job_stopped stay on the old job id.
Stop-during-fetch in-flight remains job_stopped (see
tests/test_stop_inflight_job_stopped.py).
"""

from __future__ import annotations

import re

from tests.conftest import book_item
from tests.test_spec_v7 import _form, _seed
from tests.test_stop_inflight_job_stopped import _s9


def _books(n=20):
    return [
        book_item(locator=f"a3-book-{i}", text=f"Signed chapter {i} of a book.")
        for i in range(n)
    ]


def _ov_counts(html: str):
    m = re.search(
        r"fetched (\d+) written (\d+) updated (\d+) unchanged (\d+) quarantined (\d+) fetch fail (\d+)",
        html,
    )
    assert m, html
    keys = ("fetched", "written", "updated", "unchanged", "quarantined", "fetch_fail")
    return dict(zip(keys, (int(x) for x in m.groups())))


def _job_stopped_for(e, job_id, locators):
    want = set(locators)
    return [
        x
        for x in e.list_quarantine()
        if x["job_id"] == job_id
        and x["failed_rule"] == "job_stopped"
        and x["locator"] in want
    ]


def _late_s6_leftover(e, job_id, items, fetched):
    """Overlapping _work after succeed: abort leftover on a terminal succeeded job."""
    remaining = [e._item_to_dict(it) for it in items]
    e._abort_stopped_work(job_id, remaining, fetched=fetched)


def _assert_succeeded_s9_unchanged(c, e, j, n, locs, prior_job_id):
    assert j["status"] == "succeeded"
    assert int(j["fetched"] or 0) == n
    assert int(j["unchanged"] or 0) == n
    assert int(j["written"] or 0) == 0
    assert int(j["updated"] or 0) == 0
    assert _s9(j), j
    assert int(j["quarantined"] or 0) == 0
    assert int(j["fetch_fail"] or 0) == 0
    html = c.get(f"/control?job={j['id']}").text
    assert 'id="ov-job"' in html
    counts = _ov_counts(html)
    assert counts["fetched"] == n
    assert counts["unchanged"] == n
    assert counts["quarantined"] == 0
    assert (
        counts["fetched"]
        == counts["written"]
        + counts["updated"]
        + counts["unchanged"]
        + counts["quarantined"]
        + counts["fetch_fail"]
    )
    assert _job_stopped_for(e, j["id"], locs) == []
    for loc in locs:
        rec = e.get_record(loc)
        assert rec is not None
        assert rec["job_id"] == prior_job_id


def test_html_second_incremental_books_s9_unchanged_not_also_quarantined(env):
    """HTML incremental books, 20 already clean, second run: S9 adds up.

    ov-job GET /control?job=ID. Succeeded job must not list the same 20 as both
    unchanged and quarantined, including after late S6 leftover abort.
    """
    e, c = env.engine, env.client
    _seed(e)
    n = 20
    items = _books(n)
    locs = [it.locator for it in items]
    e.fetch.script("books", items)

    r1 = _form(c, "/jobs", type="incremental", source="books")
    assert r1.status_code == 200
    first = [j for j in e.list_jobs() if j["source"] == "books" and j["type"] == "incremental"]
    j1 = e.get_job(first[-1]["id"])
    assert j1["status"] == "succeeded"
    assert int(j1["written"] or 0) == n

    r2 = _form(c, "/jobs", type="incremental", source="books")
    assert r2.status_code == 200
    jobs = [j for j in e.list_jobs() if j["source"] == "books" and j["type"] == "incremental"]
    j2 = e.get_job(jobs[-1]["id"])
    assert j2["id"] != j1["id"]
    _late_s6_leftover(e, j2["id"], items, n)
    j2 = e.get_job(j2["id"])
    _assert_succeeded_s9_unchanged(c, e, j2, n, locs, j1["id"])


def test_second_incremental_after_worker_lost_job_stopped_s9_no_duplicate(env):
    """After worker_lost job_stopped on the same locators, a new succeeded
    incremental S9 adds up. Old job_stopped stay on the old job id, not
    duplicated onto the new job, including after late S6 leftover abort.
    """
    e, c = env.engine, env.client
    _seed(e)
    n = 20
    items = _books(n)
    locs = [it.locator for it in items]
    e.fetch.script("books", items)

    r1 = _form(c, "/jobs", type="incremental", source="books")
    assert r1.status_code == 200
    j1 = e.get_job(
        [j for j in e.list_jobs() if j["source"] == "books"][-1]["id"]
    )
    assert j1["status"] == "succeeded"

    inner = e.fetch

    class StopDuringFetch:
        def fetch(self, source, job_type, params):
            e.set_worker_available(False)
            return list(items)

    e.fetch = StopDuringFetch()
    r_lost = _form(c, "/jobs", type="incremental", source="books")
    assert r_lost.status_code == 200
    e.fetch = inner
    e.fetch.script("books", items)
    lost = [
        j
        for j in e.list_jobs()
        if j["id"] != j1["id"] and j["source"] == "books"
    ][-1]
    lost_id = lost["id"]
    lost = e.get_job(lost_id)
    assert lost["status"] == "failed"
    assert lost["error"] == "worker_lost"
    assert int(lost["fetched"] or 0) == n
    assert _s9(lost), lost
    assert int(lost["quarantined"] or 0) == n
    q_lost = _job_stopped_for(e, lost_id, locs)
    assert {x["locator"] for x in q_lost} == set(locs)
    assert all(x.get("open") for x in q_lost)

    e.start_worker()
    r3 = _form(c, "/jobs", type="incremental", source="books")
    assert r3.status_code == 200
    jobs = [j for j in e.list_jobs() if j["source"] == "books" and j["type"] == "incremental"]
    j3 = e.get_job(jobs[-1]["id"])
    assert j3["id"] not in (j1["id"], lost_id)
    _late_s6_leftover(e, j3["id"], items, n)
    j3 = e.get_job(j3["id"])
    _assert_succeeded_s9_unchanged(c, e, j3, n, locs, j1["id"])

    q_old = _job_stopped_for(e, lost_id, locs)
    assert {x["locator"] for x in q_old} == set(locs)
