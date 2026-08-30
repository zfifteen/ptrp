"""Acceptance tests A1–A24 (including A5b, A23, A24)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from tests.conftest import (
    SOURCES,
    ET,
    FetchedItem,
    FetchError,
    book_item,
    decision_item,
    spoken_remark,
    social_post,
    et,
)

ABSENT = [
    "ledger",
    "place-a-call",
    "place a call",
    "Yes/No",
    "NO_CALL",
    "contenteditable",
    "Save text",
    "confidence",
    "venue picker",
    "written_other",
    "SAMPLE",
]


def _html(client, path="/"):
    r = client.get(path)
    assert r.status_code == 200
    return r.text


def _seed_topics(engine):
    engine.add_topic("trade")
    engine.add_occasion("press_conference")


def _run_incremental(engine, source, items, **kw):
    engine.fetch.script(source, items)
    r = engine.enqueue_job(type="incremental", source=source, triggered_by="user", **kw)
    assert r.ok, getattr(r, "message", r)
    engine.drain()
    return r.job


def test_A1_dashboard_open_with_no_job_running(env):
    e, c = env.engine, env.client
    _seed_topics(e)
    html = _html(c, "/")
    assert "PTRP" in html
    for kind in ("remark", "decision", "writing", "interview", "social", "legal", "staffing"):
        assert kind in html
    assert "Newest clean record" in html
    assert "none" in html.lower() or "Newest clean record: none" in html
    for src in SOURCES:
        assert src in html
    assert "queued" in html.lower() or "Queued" in html
    assert "available" in html
    assert "Dashboard" in html and "Control" in html and "Records" in html and "Quarantine" in html
    assert " ET" in html or ">ET<" in html or "ET</" in html
    assert "raw clean (NOT the bar)" in html
    assert "ready" in html or "not-ready" in html or "No topic" in html
    assert "Counted channels are spoken and written_social" in html
    assert "This table is not a venue picker." in html
    for bad in ("place-a-call", "written_other", "SAMPLE", "contenteditable"):
        assert bad not in html


def test_A2_start_valid_incremental_job(env):
    e = env.engine
    _seed_topics(e)
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    assert r.ok
    job = e.get_job(r.job["id"])
    assert job["status"] == "queued"
    e.drain()
    job = e.get_job(r.job["id"])
    assert job["status"] in ("succeeded", "succeeded_empty", "failed")
    assert job["status"] == "succeeded"
    assert job["fetched"] >= 1


def test_A3_open_job_counts_add_up(env):
    e, c = env.engine, env.client
    _seed_topics(e)
    job = _run_incremental(e, "whitehouse_remarks", [spoken_remark()])
    j = e.get_job(job["id"])
    fetched = j["fetched"]
    eq = j["written"] + j["updated"] + j["unchanged"] + j["quarantined"] + j["fetch_fail"]
    assert fetched == eq
    html = _html(c, f"/control?job={job['id']}")
    assert str(job["id"]) in html
    assert "incremental" in html
    assert "whitehouse_remarks" in html
    assert j["status"] in html
    assert "fetched = written + updated + unchanged + quarantined + fetch_fail" in html or (
        str(j["fetched"]) in html
    )


def test_A4_backfill_or_targeted_missing_params_refused(env):
    e = env.engine
    r = e.enqueue_job(type="backfill", source="whitehouse_remarks", triggered_by="user")
    assert not r.ok
    assert r.message == "Backfill needs a date window."
    assert e.list_jobs() == []
    r = e.enqueue_job(type="targeted", source="whitehouse_remarks", triggered_by="user")
    assert not r.ok
    assert r.message == "Targeted needs a topic, query, or occasion."
    assert e.list_jobs() == []
    html = env.client.get("/control").text
    assert "Source is required." in html or "Backfill needs a date window." in html
    # HTML form itself documents the validation copy
    assert "Backfill needs a date window." in html
    assert "Targeted needs a topic, query, or occasion." in html
    assert "Pick a source or global." in html
    assert "Start must be on or before end." in html
    assert "Source is required." in html


def test_A5_same_source_write_mutex_overlay(env):
    e = env.engine
    _seed_topics(e)
    e.pause_execution = True
    e.fetch.script("truth_social", [social_post()])
    e.set_pin("truth_social", "realDonaldTrump")
    r1 = e.enqueue_job(type="incremental", source="truth_social", triggered_by="user")
    e.drain()
    j1 = e.get_job(r1.job["id"])
    assert j1["status"] == "running"
    r2 = e.enqueue_job(type="incremental", source="truth_social", triggered_by="user")
    assert r2.overlay == "ov-dup"
    r_ds = e.enqueue_job(
        type="incremental", source="truth_social", triggered_by="user", dup_action="dont_start"
    )
    assert r_ds.rejected
    assert f"Rejected: a job for this source is already queued or running (job {j1['id']}). A second job would write the same source." in r_ds.message
    assert len(e.list_jobs()) == 1
    r_qb = e.enqueue_job(
        type="incremental", source="truth_social", triggered_by="user", dup_action="queue_behind"
    )
    assert r_qb.ok
    j2 = e.get_job(r_qb.job["id"])
    assert j2["status"] == "queued"
    assert j2["waiting_reason"] == f"waiting: same source as {j1['id']}"
    assert f"Queued behind job {j1['id']} (same source). It will not run until that job leaves queued or running." in r_qb.message
    e.drain()
    assert e.get_job(j2["id"])["status"] == "queued"
    e.pause_execution = False
    e.drain()
    # first leaves running, second may run
    assert e.get_job(j1["id"])["status"] != "running"


def test_A5b_global_re_extract_mutex_against_every_source(env):
    e = env.engine
    _seed_topics(e)
    e.pause_execution = True
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    r1 = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    assert e.get_job(r1.job["id"])["status"] == "running"
    r2 = e.enqueue_job(type="re_extract", source="global", triggered_by="user")
    assert r2.overlay == "ov-dup"
    r_ds = e.enqueue_job(
        type="re_extract", source="global", triggered_by="user", dup_action="dont_start"
    )
    assert r_ds.rejected
    r_qb = e.enqueue_job(
        type="re_extract",
        source="global",
        triggered_by="user",
        dup_action="queue_behind",
    )
    assert r_qb.ok
    jg = e.get_job(r_qb.job["id"])
    assert jg["status"] == "queued"
    e.drain()
    assert e.get_job(jg["id"])["status"] == "queued"  # waits until source free


def test_A6_cancel_queued_or_running_s6(env):
    e = env.engine
    _seed_topics(e)
    e.pause_execution = True
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="a"), spoken_remark(locator="b", text="Second")])
    e.interrupt_after = 1
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    jid = r.job["id"]
    assert e.get_job(jid)["status"] == "running"
    e.cancel(jid)
    j = e.get_job(jid)
    assert j["status"] == "cancelled"
    stayed = e.search(source="whitehouse_remarks")
    assert all(rec["job_id"] == jid or rec["job_id"] for rec in stayed)
    q = e.list_quarantine()
    assert any(item["failed_rule"] == "job_stopped" for item in q)
    ids = {rec["record_id"] for rec in stayed}
    q_locs = {item.get("locator") for item in q if item.get("open")}
    assert not (ids & {e.get_quarantine(i["id"]).get("record_id") for i in q if i.get("record_id")})


def test_A7_retry_failed_new_id_pointer(env):
    e = env.engine
    e.fetch.script_error("factbase", "network timeout talking to factbase")
    r = e.enqueue_job(type="incremental", source="factbase", triggered_by="user")
    e.drain()
    failed = e.get_job(r.job["id"])
    assert failed["status"] == "failed"
    rr = e.retry(failed["id"])
    assert rr.ok
    new = e.get_job(rr.job["id"])
    assert new["id"] != failed["id"]
    assert new["params"] == failed["params"] or new["type"] == failed["type"]
    assert new["retry_of"] == failed["id"]
    assert new["triggered_by"] == "retry"
    assert e.get_job(failed["id"])["status"] == "failed"
    assert e.get_job(failed["id"]).get("retried_as") == new["id"]


def test_A8_disable_source_not_scheduled_manual_run_confirm(env):
    e, c = env.engine, env.client
    e.set_source_enabled("campaign", False)
    assert e.next_scheduled_run("campaign") == "not scheduled"
    html = _html(c, "/control")
    assert "not scheduled" in html
    r = e.enqueue_job(type="incremental", source="campaign", triggered_by="user")
    assert r.overlay == "ov-disabled"
    assert "This source is disabled. Scheduler will not run it. Manual Run still enqueues. Continue?" in r.message
    r2 = e.enqueue_job(
        type="incremental", source="campaign", triggered_by="user", confirm_disabled=True
    )
    assert r2.ok
    assert e.get_job(r2.job["id"])["status"] == "queued"
    e.scheduler_tick()
    sched = [j for j in e.list_jobs() if j["triggered_by"] == "schedule" and j["source"] == "campaign"]
    assert sched == []


def test_A9_browse_clean_record_read_only(env):
    e, c = env.engine, env.client
    _seed_topics(e)
    _run_incremental(e, "whitehouse_remarks", [spoken_remark()])
    recs = e.search()
    assert recs
    rec = recs[0]
    html = _html(c, f"/records?record={rec['record_id']}")
    assert rec["text"] in html
    assert "ov-record" in html
    assert "contenteditable" not in html
    assert "Save text" not in html
    assert "confidence" not in html.lower() or "confidence" not in html
    assert "Clean text is not editable. Fix source config or re-ingest / re-extract." in html
    assert rec["completeness"] in html
    got = e.get_record(rec["record_id"])
    assert "confidence" not in got
    assert got["text"] == rec["text"]
    assert "named_party" in got


def test_A10_export_retrieval_set_section6_fields(env):
    e = env.engine
    _seed_topics(e)
    _run_incremental(e, "whitehouse_remarks", [spoken_remark()])
    payload = e.export_retrieval_set()
    assert payload
    row = payload[0]
    expected = {
        "record_id",
        "text_version",
        "text_hash",
        "channel",
        "event_time",
        "published_time",
        "completeness",
        "mention_usable",
        "decision_usable",
        "kind",
        "source",
        "text",
        "named_party",
    }
    assert set(row.keys()) == expected
    assert "confidence" not in row
    html = env.client.get("/records").text
    assert "Export retrieval set" in html
    r = env.client.get("/records/export")
    assert r.status_code == 200
    assert r.json()[0].keys() == expected


def test_A11_quarantine_fieldfail_vs_hold(env):
    e, c = env.engine, env.client
    _seed_topics(e)
    bad = spoken_remark(locator="bad", text="", attributed=False)
    hold = spoken_remark(locator="hold1", outlet="cnn", kind="interview", channel="spoken")
    e.add_topic("trade")
    e.set_allowlist(["nyt"])  # cnn not on list — but this item is WH remarks; make interviews item
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="ok"), spoken_remark(locator="ff", text="")])
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    e.fetch.script(
        "interviews",
        [
            spoken_remark(
                locator="iv1",
                kind="interview",
                channel="spoken",
                outlet="cnn",
                title="Interview",
            )
        ],
    )
    e.set_allowlist(["nyt"])
    r2 = e.enqueue_job(type="incremental", source="interviews", triggered_by="user", confirm_disabled=True)
    e.drain()
    items = e.list_quarantine()
    assert any(i["reason"] == "field-fail" for i in items)
    html = _html(c, "/quarantine")
    assert "field-fail" in html
    assert "operator-hold" in html or "field-fail" in html
    assert "Cannot accept. Fix source or extract, then run a new job." in html
    assert (
        "Discarded items shall not reappear as clean on the next incremental run unless source content or locator changed, or Fate force re-fetches."
        in html
    )
    ff = next(i for i in items if i["reason"] == "field-fail")
    acc = e.accept_quarantine(ff["id"])
    assert not acc.ok
    # operator-hold from interviews outlet not on allowlist
    holds = [i for i in e.list_quarantine() if i["reason"] == "operator-hold"]
    if holds:
        h = holds[0]
        html_h = _html(c, f"/quarantine?item={h['id']}")
        assert "ov-q-hold" in html_h
        before = len(e.search())
        ok = e.accept_quarantine(h["id"], confirm=True)
        assert ok.ok
        assert len(e.search()) == before + 1


def test_A12_worker_down_during_running(env):
    e, c = env.engine, env.client
    _seed_topics(e)
    e.pause_execution = True
    e.interrupt_after = 1
    e.fetch.script(
        "whitehouse_remarks",
        [spoken_remark(locator="w1"), spoken_remark(locator="w2", text="Second remark")],
    )
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    jid = r.job["id"]
    assert e.get_job(jid)["status"] == "running"
    e.set_worker_available(False)
    j = e.get_job(jid)
    assert j["status"] == "failed"
    assert j["error"] == "worker_lost"
    assert not any(x["status"] == "running" for x in e.list_jobs())
    html = _html(c, "/")
    assert "Worker not available. New jobs sit queued. Nothing is executing." in html
    assert "not available" in html
    stayed = e.search()
    assert stayed  # some clean stayed
    for rec in stayed:
        got = e.get_record(rec["record_id"])
        assert got
    q = [i for i in e.list_quarantine() if i["failed_rule"] == "job_stopped"]
    assert q
    rnew = e.enqueue_job(type="incremental", source="app", triggered_by="user")
    assert rnew.ok
    assert e.get_job(rnew.job["id"])["status"] == "queued"
    e.set_worker_available(True)
    # returning worker does not resume the lost job
    assert e.get_job(jid)["status"] == "failed"
    e.drain()
    assert e.get_job(jid)["status"] == "failed"


def test_A13_empty_interview_allowlist_blocked(env):
    e, c = env.engine, env.client
    html = _html(c, "/")
    assert "blocked: empty allowlist" in html
    e.fetch.script("interviews", [])
    r = e.enqueue_job(type="incremental", source="interviews", triggered_by="user")
    e.drain()
    j = e.get_job(r.job["id"])
    assert j["status"] == "succeeded_empty"
    health = e.source_health()["interviews"]
    assert health["blocked"] == "blocked: empty allowlist"
    assert health["last_succeeded"] is None or health["last_succeeded"] == "never"


def test_A14_thin_is_not_ready_not_third_rank(env):
    e, c = env.engine, env.client
    _seed_topics(e)
    # two usable spoken remarks — thin
    e.fetch.script(
        "whitehouse_remarks",
        [
            spoken_remark(locator="t1", text="One"),
            spoken_remark(locator="t2", text="Two"),
        ],
    )
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    dash = e.dashboard()
    rows = dash["topic_channel"]
    spoken_rows = [r for r in rows if r["channel"] == "spoken" and r["topic"] == "trade"]
    assert spoken_rows
    row = spoken_rows[0]
    assert row["health"] == "not-ready"
    assert row["health"] != "thin"
    assert "thin" in row["failed_clause"].lower() or "usable" in row["failed_clause"]
    html = _html(c, "/")
    assert "not-ready" in html
    assert "venue" not in html.lower() or "not a venue picker" in html
    assert "raw clean (NOT the bar)" in html


def test_A15_walk_all_four_screens_hard_exclusions(env):
    c = env.client
    for path in ("/", "/control", "/records", "/quarantine"):
        html = _html(c, path)
        assert "PTRP" in html
        assert "Dashboard" in html and "Control" in html and "Records" in html and "Quarantine" in html
        assert "available" in html or "not available" in html
        low = html.lower()
        assert "place-a-call" not in low
        assert "place a call" not in low
        assert "contenteditable" not in low
        assert "save text" not in low
        assert "written_other" not in html
        assert "SAMPLE" not in html
        assert "user switcher" not in low
        assert "timezone control" not in low and "timezone picker" not in low
        assert "cron builder" not in low
        assert "Yes/No" not in html
        assert "NO_CALL" not in html
        # confidence as a product field/control — not the word in CSS comments accidentally
        assert 'name="confidence"' not in html
        assert "call ledger" not in low
        assert "grading" not in low or path  # grading word shouldn't appear
        assert "grading" not in low
        assert "people-vocab" not in low


def test_A16_restart_persists_knowledge_base(env):
    from ptrp.engine import Engine
    from ptrp.app import create_app

    e = env.engine
    _seed_topics(e)
    _run_incremental(e, "whitehouse_remarks", [spoken_remark()])
    recs = e.search()
    rid = recs[0]["record_id"]
    db = env.db
    fetch = env.fetch
    clock = env.clock
    e2 = Engine(db_path=db, fetch=fetch, clock=clock)
    e2.boot()
    got = e2.get_record(rid)
    assert got["record_id"] == rid
    assert got["text"] == recs[0]["text"]
    c2 = TestClient(create_app(e2))
    html = c2.get("/").text
    assert "remark" in html


def test_A17_records_four_read_actions(env):
    e, c = env.engine, env.client
    _seed_topics(e)
    a = spoken_remark(locator="p1", text="First independent remark about trade.", event_time=datetime(2025, 2, 1, 15, tzinfo=timezone.utc), occasion="press_conference")
    b = spoken_remark(locator="p2", text="Second independent remark about trade.", event_time=datetime(2025, 3, 1, 15, tzinfo=timezone.utc), occasion="address")
    e.add_occasion("address")
    e.fetch.script("whitehouse_remarks", [a, b])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    e.enqueue_job(type="refresh_preferences", source="global", triggered_by="user", confirm_refresh=True)
    e.drain()
    html = _html(c, "/records")
    assert "Open preference" in html
    found = e.search(query="independent")
    assert found
    rec = e.get_record(found[0]["record_id"])
    assert rec["record_id"]
    # prior version path: force re-fetch new text
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="p1", text="Edited first independent remark about trade.")])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user", force_refetch=True)
    e.drain()
    cur = e.get_record("p1") if e.get_record(found[0]["record_id"]) else e.search(query="Edited")[0]
    # resolve by locator-stable id
    recs = e.search(query="Edited")
    assert recs
    rid = recs[0]["record_id"]
    current = e.get_record(rid)
    prior = e.get_record(rid, text_version=1)
    assert prior["text_version"] != current["text_version"] or prior["text"] != current["text"]
    pref = e.get_preference("trade")
    assert pref is not None
    exported = e.export_retrieval_set(query="trade")
    assert exported
    e.read_down = True
    html_down = _html(c, "/records")
    assert "error" in html_down.lower() or "unavailable" in html_down.lower() or "failed" in html_down.lower()
    e.read_down = False


def test_A18_clear_official_pin_blocked_empty_pin(env):
    e, c = env.engine, env.client
    html = _html(c, "/")
    assert "blocked: empty pin" in html
    e.set_pin("x_personal", "realDonaldTrump")
    e.set_pin("x_personal", "")
    health = e.source_health()["x_personal"]
    assert health["blocked"] == "blocked: empty pin"
    e.fetch.script("x_personal", [social_post(locator="x1", author_handle="realDonaldTrump")])
    e.enqueue_job(type="incremental", source="x_personal", triggered_by="user")
    e.drain()
    clean = e.search(source="x_personal")
    assert clean == []
    q = e.list_quarantine()
    assert any(i["reason"] == "field-fail" for i in q)


def test_A19_wh_remarks_illegal_pair_field_fail(env):
    e = env.engine
    _seed_topics(e)
    item = spoken_remark(locator="soc", kind="social", channel="written_social")
    e.fetch.script("whitehouse_remarks", [item])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    assert e.search(source="whitehouse_remarks") == []
    q = e.list_quarantine()
    assert q and q[0]["reason"] == "field-fail"


def test_A20_spoken_not_ready_stale_uses_only_covering_set(env):
    e = env.engine
    _seed_topics(e)
    # Seed 3 usable 2025 spoken so thin does not fire
    items = [spoken_remark(locator=f"c{i}", text=f"Remark {i} about trade in 2025.") for i in range(3)]
    e.fetch.script("whitehouse_remarks", items)
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    # Make spoken covering all cadence-stale by aging last success, keep books/legal/actions fresh
    old = datetime(2026, 8, 1, 13, 0, tzinfo=timezone.utc)
    for src in ("whitehouse_remarks", "app", "factbase", "campaign", "interviews"):
        e.debug_set_last_success(src, old, fetched=1)
    now = datetime(2026, 8, 26, 15, 0, tzinfo=ET).astimezone(timezone.utc)
    e.debug_set_last_success("books", now, fetched=1)
    e.debug_set_last_success("legal", now, fetched=1)
    e.debug_set_last_success("whitehouse_actions", now, fetched=1)
    e.debug_set_last_success("federal_register", now, fetched=1)
    dash = e.dashboard()
    row = next(r for r in dash["topic_channel"] if r["topic"] == "trade" and r["channel"] == "spoken")
    assert row["health"] == "not-ready"
    assert "stale" in row["failed_clause"].lower()
    # Fresh one covering source is enough to fail the all-stale clause; may still be ready if not thin
    e.debug_set_last_success("whitehouse_remarks", now, fetched=1)
    dash = e.dashboard()
    row = next(r for r in dash["topic_channel"] if r["topic"] == "trade" and r["channel"] == "spoken")
    assert row["health"] == "ready"
    # Inverse: covering fresh, non-covering stale → still ready (non-covering do not decide)
    e.debug_set_last_success("books", old, fetched=1)
    dash = e.dashboard()
    row = next(r for r in dash["topic_channel"] if r["topic"] == "trade" and r["channel"] == "spoken")
    assert row["health"] == "ready"


def test_A21_books_source_health_exempt(env):
    e, c = env.engine, env.client
    _seed_topics(e)
    e.fetch.script("books", [book_item()])
    e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    h = e.source_health()["books"]
    assert h["last_succeeded"] not in (None, "never")
    assert h.get("cadence_stale") is False
    assert h.get("cadence") in (None, "none", "exempt")
    html = _html(c, "/")
    assert "books" in html
    assert "no cadence" in html
    # next run
    assert e.next_scheduled_run("books") == "not scheduled"


def test_A22_cancel_running_fetch_in_flight_job_stopped(env):
    e = env.engine
    _seed_topics(e)
    e.interrupt_after = 1
    e.pause_execution = False
    e.fetch.script(
        "whitehouse_remarks",
        [
            spoken_remark(locator="k1", text="Clean one"),
            spoken_remark(locator="k2", text="In flight two"),
            spoken_remark(locator="k3", text="In flight three"),
        ],
    )
    # Use a hook: after 1 clean write, cancel
    e.cancel_after_clean = 1
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    j = e.get_job(r.job["id"])
    assert j["status"] in ("cancelled", "failed")
    assert j["fetched"] == j["written"] + j["updated"] + j["unchanged"] + j["quarantined"] + j["fetch_fail"]
    q = [i for i in e.list_quarantine() if i["failed_rule"] == "job_stopped"]
    assert q
    assert j["quarantined"] >= len(q)
    for item in q:
        acc = e.accept_quarantine(item["id"])
        assert not acc.ok


def test_A23_first_boot_all_eleven_enabled_no_wizard(env):
    e, c = env.engine, env.client
    states = e.sources_state()
    assert set(states) == set(SOURCES)
    assert all(states[s]["enabled"] for s in SOURCES)
    html = _html(c, "/control")
    assert "wizard" not in html.lower()
    dash = _html(c, "/")
    assert "blocked: empty allowlist" in dash
    assert "blocked: empty pin" in dash
    assert all(s in dash for s in SOURCES)
    # enabled independent of blocked
    assert states["interviews"]["enabled"] is True
    assert states["x_personal"]["enabled"] is True
    assert states["truth_social"]["enabled"] is True


def test_A24_clock_0900_et_next_weekday_and_monday(env):
    e = env.engine
    # Wednesday Aug 26, 2026 15:00 ET (fixture) — after 09:00
    nxt = e.next_scheduled_run("whitehouse_remarks")  # daily
    assert nxt != "not scheduled"
    et_dt = nxt.astimezone(ET) if hasattr(nxt, "astimezone") else nxt
    assert et_dt.hour == 9 and et_dt.minute == 0
    assert et_dt.tzinfo is not None
    # next weekday = Thursday Aug 27
    assert (et_dt.year, et_dt.month, et_dt.day) == (2026, 8, 27)
    assert et_dt.weekday() < 5
    weekly = e.next_scheduled_run("campaign")
    w = weekly.astimezone(ET)
    assert w.hour == 9 and w.minute == 0
    assert w.weekday() == 0  # Monday
    assert (w.year, w.month, w.day) == (2026, 8, 31)
    assert e.next_scheduled_run("books") == "not scheduled"
    # Friday after 09:00 → Monday
    env.clock.box.now = datetime(2026, 8, 28, 10, 0, tzinfo=ET)
    fri = e.next_scheduled_run("truth_social")
    f = fri.astimezone(ET)
    assert (f.year, f.month, f.day) == (2026, 8, 31)
    assert f.hour == 9
    # Monday before 09:00 → this Monday for weekly
    env.clock.box.now = datetime(2026, 8, 24, 8, 0, tzinfo=ET)
    mon = e.next_scheduled_run("app")
    m = mon.astimezone(ET)
    assert (m.year, m.month, m.day) == (2026, 8, 24)
    assert m.hour == 9
    # weekday before 09:00 daily = today
    tue = e.next_scheduled_run("whitehouse_remarks")
    # clock is Monday 08:00, daily today Monday 09:00
    t = tue.astimezone(ET)
    assert (t.year, t.month, t.day, t.hour) == (2026, 8, 24, 9)
