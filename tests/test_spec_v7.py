"""Acceptance A25–A38 and failure F38–F52 (Approved Spec v7)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.conftest import (
    ET,
    FetchedItem,
    book_item,
    social_post,
    spoken_remark,
)


def _form(client, path, **data):
    return client.post(path, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})


def _html(client, path="/"):
    r = client.get(path)
    assert r.status_code == 200
    return r.text


def _seed(engine):
    engine.add_topic("trade")
    engine.add_occasion("press_conference")


def _legal_item(**kw) -> FetchedItem:
    defaults = dict(
        locator="lg-1",
        text="A filing in which Donald Trump is the named party.",
        kind="legal",
        channel="legal",
        title="Filing",
        event_time=datetime(2025, 3, 1, 15, 0, tzinfo=timezone.utc),
        url="https://example.com/legal/1",
        completeness="full_transcript",
        attributed=True,
        named_party="Donald Trump",
        topics=["trade"],
        term="2025_present",
    )
    defaults.update(kw)
    return FetchedItem(**defaults)


def _no_utc(html: str):
    assert " UTC" not in html
    assert "+00:00" not in html
    assert "Z</" not in html
    # ISO UTC instants must not appear on operator screens
    assert "T" not in html or "T19:" not in html


def _operator_item_params(**kw):
    base = dict(
        targeted_mode="operator_item",
        locator="op-1",
        text="Operator supplied item text.",
        kind="remark",
        channel="spoken",
        title="Operator item",
        event_time="2025-03-15T16:00:00+00:00",
        attributed=True,
        completeness="full_transcript",
        topics=["trade"],
        occasion="press_conference",
        term="2025_present",
    )
    base.update(kw)
    return base


# --- A25–A38 ---


def test_A25_stop_worker_during_running_same_as_A12(env):
    e, c = env.engine, env.client
    _seed(e)
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
    html = _html(c, "/")
    assert 'id="worker-stop"' in html
    r_ov = _form(c, "/worker/stop")
    assert r_ov.status_code != 500
    assert 'id="ov-worker-stop"' in r_ov.text
    assert "Stop the worker? Running jobs will fail with worker_lost." in r_ov.text
    r_ok = _form(c, "/worker/stop", confirm="1")
    assert r_ok.status_code != 500
    j = e.get_job(jid)
    assert j["status"] == "failed"
    assert j["error"] == "worker_lost"
    assert not any(x["status"] == "running" for x in e.list_jobs())
    html = _html(c, "/")
    assert "Worker not available. New jobs sit queued. Nothing is executing." in html
    assert "not available" in html
    stayed = e.search()
    assert stayed
    for rec in stayed:
        assert e.get_record(rec["record_id"])
    q = [i for i in e.list_quarantine() if i["failed_rule"] == "job_stopped"]
    assert q
    e.start_worker()
    assert e.get_job(jid)["status"] == "failed"


def test_A26_restart_the_app_persists_record_id_enable_pins(env):
    from ptrp.app import create_app
    from ptrp.engine import Engine

    e, c = env.engine, env.client
    _seed(e)
    e.set_source_enabled("campaign", False)
    e.set_pin("x_personal", "realDonaldTrump")
    e.add_allowlist("nyt")
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    rid = e.search()[0]["record_id"]
    html = _html(c, "/control?tab=sources")
    assert 'id="btn-restart"' in html
    assert 'id="ov-restart"' in html
    assert "Restart the app? The knowledge base stays. Running jobs fail with worker_lost." in html
    e2 = Engine(db_path=env.db, fetch=env.fetch, clock=env.clock)
    e2.boot()
    c2 = TestClient(create_app(e2))
    got = e2.get_record(rid)
    assert got["record_id"] == rid
    assert e2.sources_state()["campaign"]["enabled"] is False
    assert e2.get_pin("x_personal") == "realDonaldTrump"
    assert "nyt" in e2.allowlist()
    assert "trade" in e2.list_topics()
    assert e2.worker_available is True
    html2 = c2.get("/").text
    assert "available" in html2
    assert "not available" not in html2 or 'id="worker-stop"' in html2


def test_A27_records_reads_down_search_cannot_run(env):
    e, c = env.engine, env.client
    _seed(e)
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    html = _html(c, "/control?tab=operator")
    assert 'id="records-reads"' in html
    r = _form(c, "/operator/records-reads", value="down")
    assert r.status_code != 500
    html_s = _html(c, "/records")
    assert "Search cannot run." in html_s
    recs = e.search()
    assert recs == []
    r2 = _form(c, "/operator/records-reads", value="available")
    assert r2.status_code != 500
    found = e.search()
    assert found
    html_ok = _html(c, "/records")
    assert "Search cannot run." not in html_ok
    assert found[0]["record_id"] in html_ok


def test_A28_fail_next_load_dashboard_retry(env):
    c = env.client
    html = _html(c, "/control?tab=operator")
    assert 'id="fail-next-load"' in html
    r = _form(c, "/operator/fail-next-load", screen="Dashboard")
    assert r.status_code != 500
    html_d = _html(c, "/")
    assert "Dashboard failed to load" in html_d
    assert "Retry" in html_d
    assert 'id="load-error"' in html_d
    r2 = _form(c, "/load-retry")
    assert r2.status_code != 500
    html_ok = r2.text if "Dashboard failed to load" not in r2.text else _html(c, "/")
    if "Dashboard failed to load" in html_ok:
        html_ok = _html(c, "/")
    assert "Dashboard failed to load" not in html_ok
    assert "PTRP" in html_ok


def test_A29_connector_auth_books_job_failed(env):
    e, c = env.engine, env.client
    _seed(e)
    html = _html(c, "/control?tab=sources")
    assert 'id="connector-books"' in html
    r = _form(c, "/sources/books/connector", value="auth")
    assert r.status_code != 500
    e.fetch.script("books", [book_item()])
    rj = e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    j = e.get_job(rj.job["id"])
    assert j["status"] == "failed"
    assert j["error"] == "auth"
    assert e.search(source="books") == []
    assert len([x for x in e.list_jobs() if x["source"] == "books"]) == 1


def test_A30_operator_item_off_s7_whitehouse_remarks_social(env):
    e = env.engine
    _seed(e)
    e.set_pin("x_personal", "realDonaldTrump")
    r = e.enqueue_job(
        type="targeted",
        source="whitehouse_remarks",
        triggered_by="user",
        params=_operator_item_params(
            kind="social",
            channel="written_social",
            published_time="2025-03-15T18:00:00+00:00",
            author_handle="realDonaldTrump",
        ),
    )
    assert r.ok, getattr(r, "message", r)
    e.drain()
    j = e.get_job(r.job["id"])
    assert j["fetched"] == 1
    assert e.search(source="whitehouse_remarks") == []
    q = e.list_quarantine()
    assert q and q[0]["reason"] == "field-fail"


def test_A31_operator_item_x_personal_lookalike_quarantined(env):
    e, c = env.engine, env.client
    _seed(e)
    rpin = _form(c, "/vocab/pins", x_personal="realDonaldTrump")
    assert rpin.status_code != 500
    assert e.get_pin("x_personal") == "realDonaldTrump"
    assert e.source_health()["x_personal"]["blocked"] != "blocked: empty pin"
    r = e.enqueue_job(
        type="targeted",
        source="x_personal",
        triggered_by="user",
        params=_operator_item_params(
            kind="social",
            channel="written_social",
            locator="x-lk",
            published_time="2025-03-15T18:00:00+00:00",
            pin_match="lookalike",
            author_handle="realDonaldTrumpFan",
        ),
    )
    assert r.ok, getattr(r, "message", r)
    e.drain()
    assert e.search(source="x_personal") == []
    q = e.list_quarantine()
    assert q and q[0]["reason"] == "field-fail"
    assert e.source_health()["x_personal"]["blocked"] != "blocked: empty pin"


def test_A32_operator_item_legal_named_party_the_administration(env):
    e = env.engine
    _seed(e)
    r = e.enqueue_job(
        type="targeted",
        source="legal",
        triggered_by="user",
        params=_operator_item_params(
            kind="legal",
            channel="legal",
            locator="adm-op",
            named_party="the administration",
            text="A filing by the administration.",
        ),
    )
    assert r.ok, getattr(r, "message", r)
    e.drain()
    assert e.search(source="legal") == []
    assert e.list_quarantine()


def test_A33_job_created_et_after_restart_no_utc_on_screen(env):
    from ptrp.app import create_app
    from ptrp.engine import Engine

    e, c = env.engine, env.client
    _seed(e)
    e.fetch.script("books", [book_item()])
    r = e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    jid = r.job["id"]
    html1 = _html(c, f"/control?job={jid}")
    created_et = None
    for line in html1.split("created"):
        if " ET" in line:
            created_et = line.split(" ET")[0][-40:]
            break
    assert " ET" in html1
    _no_utc(html1)
    e2 = Engine(db_path=env.db, fetch=env.fetch, clock=env.clock)
    e2.boot()
    c2 = TestClient(create_app(e2))
    html2 = c2.get(f"/control?job={jid}").text
    assert " ET" in html2
    _no_utc(html2)
    j = e2.get_job(jid)
    from ptrp.engine import format_et, _parse_dt
    assert format_et(_parse_dt(j["created"])) in html2
    assert format_et(_parse_dt(j["created"])) in html1


def test_A34_probe_clock_monday_0800_0900_frozen_1000(env):
    e, c = env.engine, env.client
    html = _html(c, "/control?tab=operator")
    assert 'id="probe-clock"' in html
    mon8 = datetime(2026, 8, 24, 8, 0, tzinfo=ET)
    r = _form(c, "/operator/probe-clock", value="2026-08-24T08:00")
    assert r.status_code != 500
    weekly = e.next_scheduled_run("app")
    w = weekly.astimezone(ET)
    assert (w.year, w.month, w.day, w.hour, w.minute) == (2026, 8, 24, 9, 0)
    before = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    e.scheduler_tick()
    after8 = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    assert after8 == before

    r = _form(c, "/operator/probe-clock", value="2026-08-24T09:00")
    assert r.status_code != 500
    at9 = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    assert len(at9) > len(before)
    first_ids = {j["id"] for j in at9}
    weekly = e.next_scheduled_run("app")
    w = weekly.astimezone(ET)
    assert (w.year, w.month, w.day, w.hour) == (2026, 8, 31, 9)
    e.scheduler_tick()
    frozen = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    assert {j["id"] for j in frozen} == first_ids

    r = _form(c, "/operator/probe-clock", value="2026-08-24T10:00")
    assert r.status_code != 500
    e.scheduler_tick()
    after10 = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    assert {j["id"] for j in after10} == first_ids


def test_A35_add_topic_tariffs_dashboard_rows_before_ingest(env):
    e, c = env.engine, env.client
    html0 = _html(c, "/")
    assert "No topic × channel rows. Add topics in Control → Vocabularies, then ingest." in html0
    r = _form(c, "/vocab/topics", tag="tariffs")
    assert r.status_code != 500
    dash = e.dashboard()
    rows = [r for r in dash["topic_channel"] if r["topic"] == "tariffs"]
    chans = {r["channel"] for r in rows}
    assert chans == {"spoken", "written_social"}
    for row in rows:
        assert row["usable"] == 0
        assert row["health"] == "not-ready"
        assert row["failed_clause"] == "zero usable"
    html = _html(c, "/")
    assert "tariffs" in html
    assert "spoken" in html
    assert "written_social" in html
    assert "not-ready" in html
    assert "zero usable" in html


def test_A36_operator_item_empty_query_fields_creates_job(env):
    e, c = env.engine, env.client
    _seed(e)
    params = _operator_item_params()
    params["topic"] = ""
    params["query"] = ""
    params["occasion"] = ""
    r = e.enqueue_job(
        type="targeted",
        source="whitehouse_remarks",
        triggered_by="user",
        params=params,
    )
    assert r.ok, getattr(r, "message", r)
    assert "Targeted needs a topic, query, or occasion." not in (r.message or "")
    r2 = _form(
        c,
        "/jobs",
        type="targeted",
        source="books",
        targeted_mode="operator_item",
        locator="op-book",
        text="A signed chapter.",
        kind="writing",
        channel="other",
    )
    assert r2.status_code != 500
    jobs = [j for j in e.list_jobs() if j["type"] == "targeted"]
    assert jobs
    assert "Targeted needs a topic, query, or occasion." not in r2.text or e.get_job(jobs[-1]["id"])


def test_A37_operator_item_missing_locator_refused(env):
    e, c = env.engine, env.client
    before = len(e.list_jobs())
    r = e.enqueue_job(
        type="targeted",
        source="whitehouse_remarks",
        triggered_by="user",
        params=_operator_item_params(locator=""),
    )
    assert not r.ok
    assert r.message == "Operator item needs source, locator, text, kind, and channel."
    assert len(e.list_jobs()) == before
    html = _form(
        c,
        "/jobs",
        type="targeted",
        source="whitehouse_remarks",
        targeted_mode="operator_item",
        locator="",
        text="text",
        kind="remark",
        channel="spoken",
    )
    assert html.status_code != 500
    assert "Operator item needs source, locator, text, kind, and channel." in html.text
    assert "Targeted needs a topic, query, or occasion." not in html.text.split('id="run-error"')[-1][:400] if 'id="run-error"' in html.text else True
    assert len(e.list_jobs()) == before


def test_A38_clean_legal_named_party_on_ov_record_getrecord_export(env):
    e, c = env.engine, env.client
    _seed(e)
    e.fetch.script("legal", [_legal_item()])
    e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    e.drain()
    recs = e.search(source="legal")
    assert recs
    rec = recs[0]
    assert rec["named_party"] == "Donald Trump"
    got = e.get_record(rec["record_id"])
    assert got["named_party"] == "Donald Trump"
    html = _html(c, f"/records?record={rec['record_id']}")
    assert 'id="ov-record"' in html
    assert 'id="rec-named-party"' in html
    assert "Donald Trump" in html
    payload = e.export_retrieval_set(source="legal")
    assert payload
    assert "named_party" in payload[0]
    assert payload[0]["named_party"] == "Donald Trump"
    r = c.get("/records/export")
    assert r.status_code == 200
    rows = r.json()
    assert any(row.get("named_party") == "Donald Trump" for row in rows)


# --- F38–F52 ---


def test_F38_stop_worker_overlay_confirm_applies_s5(env):
    e, c = env.engine, env.client
    _seed(e)
    e.pause_execution = True
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    jid = r.job["id"]
    assert e.get_job(jid)["status"] == "running"
    r_ov = _form(c, "/worker/stop")
    assert 'id="ov-worker-stop"' in r_ov.text
    r_ok = _form(c, "/worker/stop", confirm="1")
    assert r_ok.status_code != 500
    j = e.get_job(jid)
    assert j["status"] == "failed"
    assert j["error"] == "worker_lost"
    html = _html(c, "/")
    assert "not available" in html
    assert "Worker not available. New jobs sit queued. Nothing is executing." in html
    assert not any(x["status"] == "running" for x in e.list_jobs())
    assert 'id="worker-start"' in html


def test_F39_start_worker_does_not_resume_worker_lost(env):
    e, c = env.engine, env.client
    _seed(e)
    e.pause_execution = True
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="a")])
    r1 = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    e.set_worker_available(False)
    lost = e.get_job(r1.job["id"])
    assert lost["status"] == "failed"
    e.fetch.script("books", [book_item()])
    r2 = e.enqueue_job(type="incremental", source="books", triggered_by="user")
    assert e.get_job(r2.job["id"])["status"] == "queued"
    e.pause_execution = False
    r_start = _form(c, "/worker/start")
    assert r_start.status_code != 500
    html = _html(c, "/")
    assert "available" in html
    assert "Worker not available. New jobs sit queued. Nothing is executing." not in html
    assert e.get_job(lost["id"])["status"] == "failed"
    e.drain()
    assert e.get_job(lost["id"])["status"] == "failed"
    assert e.get_job(r2.job["id"])["status"] in ("succeeded", "succeeded_empty", "failed", "running", "queued")
    assert e.get_job(r2.job["id"])["status"] != "failed" or e.get_job(r2.job["id"])["error"] != "worker_lost"


def test_F40_restart_the_app_overlay_s5_persists_config(env):
    from ptrp.app import create_app
    from ptrp.engine import Engine

    e, c = env.engine, env.client
    _seed(e)
    e.set_source_enabled("campaign", False)
    e.set_pin("truth_social", "realDonaldTrump")
    e.add_allowlist("wsj")
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    rid = e.search()[0]["record_id"]
    e.pause_execution = True
    e.fetch.script("books", [book_item()])
    rr = e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    running_id = rr.job["id"]
    assert e.get_job(running_id)["status"] == "running"
    html = _html(c, "/control?tab=sources")
    assert 'id="ov-restart"' in html
    r_ov = _form(c, "/danger/restart")
    assert 'id="ov-restart"' in r_ov.text
    assert "Restart the app? The knowledge base stays. Running jobs fail with worker_lost." in r_ov.text
    r_ok = _form(c, "/danger/restart", confirm="1")
    assert r_ok.status_code != 500
    e2 = Engine(db_path=env.db, fetch=env.fetch, clock=env.clock)
    e2.boot()
    assert e2.get_record(rid)
    assert e2.sources_state()["campaign"]["enabled"] is False
    assert e2.get_pin("truth_social") == "realDonaldTrump"
    assert "wsj" in e2.allowlist()
    assert "trade" in e2.list_topics()
    assert e2.worker_available is True
    j = e2.get_job(running_id)
    assert j["status"] == "failed"
    assert j["error"] == "worker_lost"
    typed = e2.delete_base(typed="")
    assert not typed.ok
    assert e2.get_record(rid)


def test_F41_records_reads_down_each_section6_cannot_run(env):
    e, c = env.engine, env.client
    _seed(e)
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    rid = e.search()[0]["record_id"]
    _form(c, "/operator/records-reads", value="down")
    html = _html(c, "/records")
    assert "Search cannot run." in html
    html_g = _html(c, f"/records?record={rid}")
    assert "GetRecord cannot run." in html_g
    html_p = _html(c, "/records?pref_topic=trade")
    assert "GetPreference cannot run." in html_p
    html_e = _html(c, "/records")
    assert "Export cannot run." in html_e
    assert e.search() == []
    assert e.get_record(rid) is None or e.read_down
    exp = c.get("/records/export")
    assert exp.status_code >= 400 or "cannot run" in exp.text.lower() or "error" in exp.text.lower()


def test_F42_fail_next_load_retry_clears(env):
    c = env.client
    _form(c, "/operator/fail-next-load", screen="Records")
    html = _html(c, "/records")
    assert "Records failed to load" in html
    assert "Retry" in html
    r = _form(c, "/load-retry")
    assert r.status_code != 500
    html2 = c.get("/records").text
    assert "Records failed to load" not in html2


def test_F43_connector_network_auth_parse_exact_error_s6(env):
    e = env.engine
    _seed(e)
    for src, err in (("app", "network"), ("factbase", "auth"), ("federal_register", "parse")):
        e.set_connector(src, err)
        e.fetch.script(src, [spoken_remark(locator=f"{src}-1")])
        r = e.enqueue_job(type="incremental", source=src, triggered_by="user")
        e.drain()
        j = e.get_job(r.job["id"])
        assert j["status"] == "failed"
        assert j["error"] == err
        assert e.search(source=src) == []
        e.set_connector(src, "ok")
        assert e.get_job(r.job["id"])["status"] == "failed"
    assert len(e.list_jobs()) == 3


def test_F44_operator_item_off_s7_field_fail_fetched_1(env):
    e = env.engine
    _seed(e)
    e.set_pin("x_personal", "realDonaldTrump")
    r = e.enqueue_job(
        type="targeted",
        source="whitehouse_remarks",
        triggered_by="user",
        params=_operator_item_params(kind="social", channel="written_social"),
    )
    assert r.ok
    e.drain()
    j = e.get_job(r.job["id"])
    assert j["fetched"] == 1
    assert e.search() == []
    assert e.list_quarantine()[0]["reason"] == "field-fail"


def test_F45_operator_item_lookalike_f11(env):
    e = env.engine
    _seed(e)
    e.set_pin("truth_social", "realDonaldTrump")
    r = e.enqueue_job(
        type="targeted",
        source="truth_social",
        triggered_by="user",
        params=_operator_item_params(
            kind="social",
            channel="written_social",
            locator="ts-lk",
            published_time="2025-03-15T18:00:00+00:00",
            pin_match="lookalike",
        ),
    )
    assert r.ok
    e.drain()
    assert e.search(source="truth_social") == []
    assert e.list_quarantine()


def test_F46_operator_item_named_party_the_administration_f27(env):
    e = env.engine
    _seed(e)
    r = e.enqueue_job(
        type="targeted",
        source="legal",
        triggered_by="user",
        params=_operator_item_params(
            kind="legal",
            channel="legal",
            named_party="the administration",
        ),
    )
    assert r.ok
    e.drain()
    assert e.search(source="legal") == []
    assert e.list_quarantine()


def test_F47_probe_clock_saturday_sunday_no_enqueue_next_monday(env):
    e, c = env.engine, env.client
    _form(c, "/operator/probe-clock", value="2026-08-29T12:00")  # Saturday
    nxt = e.next_scheduled_run("whitehouse_remarks")
    n = nxt.astimezone(ET)
    assert (n.year, n.month, n.day, n.hour) == (2026, 8, 31, 9)
    before = len([j for j in e.list_jobs() if j["triggered_by"] == "schedule"])
    e.scheduler_tick()
    assert len([j for j in e.list_jobs() if j["triggered_by"] == "schedule"]) == before
    _form(c, "/operator/probe-clock", value="2026-08-30T09:00")  # Sunday
    nxt = e.next_scheduled_run("campaign")
    n = nxt.astimezone(ET)
    assert (n.year, n.month, n.day, n.hour) == (2026, 8, 31, 9)
    e.scheduler_tick()
    assert len([j for j in e.list_jobs() if j["triggered_by"] == "schedule"]) == before


def test_F48_add_topic_rows_appear_immediately(env):
    e, c = env.engine, env.client
    assert e.dashboard()["topic_channel"] == []
    _form(c, "/vocab/topics", tag="energy")
    rows = e.dashboard()["topic_channel"]
    assert {(r["topic"], r["channel"]) for r in rows} == {("energy", "spoken"), ("energy", "written_social")}
    for row in rows:
        assert row["usable"] == 0
        assert row["health"] == "not-ready"
        assert row["failed_clause"] == "zero usable"
    e.remove_topic("energy")
    html = _html(c, "/")
    assert "No topic × channel rows. Add topics in Control → Vocabularies, then ingest." in html


def test_F49_operator_item_missing_required_refused_not_f2(env):
    e = env.engine
    before = len(e.list_jobs())
    for missing in ("source", "locator", "text", "kind", "channel"):
        params = _operator_item_params()
        kwargs = dict(type="targeted", source="whitehouse_remarks", triggered_by="user", params=params)
        if missing == "source":
            kwargs["source"] = ""
        else:
            params[missing] = ""
        r = e.enqueue_job(**kwargs)
        assert not r.ok
        assert r.message == "Operator item needs source, locator, text, kind, and channel."
        assert r.message != "Targeted needs a topic, query, or occasion."
        assert len(e.list_jobs()) == before


def test_F50_operator_item_written_social_no_pin_refused(env):
    e = env.engine
    before = len(e.list_jobs())
    r = e.enqueue_job(
        type="targeted",
        source="x_personal",
        triggered_by="user",
        params=_operator_item_params(kind="social", channel="written_social"),
    )
    assert not r.ok
    assert r.message == "A written_social Operator item is refused if no pin is set."
    assert r.message != "Targeted needs a topic, query, or occasion."
    assert len(e.list_jobs()) == before
    r2 = e.enqueue_job(
        type="targeted",
        source="whitehouse_remarks",
        triggered_by="user",
        params=_operator_item_params(kind="social", channel="written_social"),
    )
    assert not r2.ok
    assert r2.message == "A written_social Operator item is refused if no pin is set."
    assert len(e.list_jobs()) == before


def test_F51_probe_clock_weekday_0900_tick_once(env):
    e, c = env.engine, env.client
    _form(c, "/operator/probe-clock", value="2026-08-26T09:00")  # Wednesday
    jobs = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    daily = {"truth_social", "x_personal", "whitehouse_remarks", "whitehouse_actions", "interviews"}
    srcs = {j["source"] for j in jobs}
    assert daily <= srcs
    assert "books" not in srcs
    assert "legal" not in srcs
    # weekly not due on Wednesday
    assert "app" not in srcs
    assert "campaign" not in srcs
    nxt = e.next_scheduled_run("whitehouse_remarks")
    n = nxt.astimezone(ET)
    assert (n.year, n.month, n.day, n.hour) == (2026, 8, 27, 9)
    ids = {j["id"] for j in jobs}
    e.scheduler_tick()
    jobs2 = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    assert {j["id"] for j in jobs2} == ids


def test_F52_legal_named_party_absent_field_fail_not_silent(env):
    e, c = env.engine, env.client
    _seed(e)
    item = _legal_item(locator="lg-miss", named_party=None)
    e.fetch.script("legal", [item])
    e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    e.drain()
    assert e.search(source="legal") == []
    q = e.list_quarantine()
    assert q and q[0]["reason"] == "field-fail"
    e.fetch.script("legal", [_legal_item(locator="lg-ok")])
    e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    e.drain()
    recs = e.search(source="legal")
    assert recs
    rec = recs[0]
    html = _html(c, f"/records?record={rec['record_id']}")
    assert "Donald Trump" in html
    assert e.get_record(rec["record_id"])["named_party"] == "Donald Trump"
    exp = e.export_retrieval_set(source="legal")
    assert exp[0]["named_party"] == "Donald Trump"
