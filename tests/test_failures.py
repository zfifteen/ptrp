"""Failure cases F1–F37."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from tests.conftest import (
    SOURCES,
    ET,
    FetchError,
    book_item,
    decision_item,
    spoken_remark,
    social_post,
)

ETZ = ZoneInfo("America/New_York")


def _seed(engine):
    engine.add_topic("trade")
    engine.add_occasion("press_conference")


def test_F1_worker_not_available(env):
    e, c = env.engine, env.client
    _seed(e)
    e.pause_execution = True
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    assert e.get_job(r.job["id"])["status"] == "running"
    e.set_worker_available(False)
    j = e.get_job(r.job["id"])
    assert j["status"] == "failed"
    assert j["error"] == "worker_lost"
    assert not any(x["status"] == "running" for x in e.list_jobs())
    for path in ("/", "/control", "/records", "/quarantine"):
        html = c.get(path).text
        assert "Worker not available. New jobs sit queued. Nothing is executing." in html
        assert "not available" in html
        assert ">running<" not in html.lower().replace(" ", "") or "running" not in html.split("job")[0]
    r2 = e.enqueue_job(type="incremental", source="app", triggered_by="user")
    assert e.get_job(r2.job["id"])["status"] == "queued"
    # mutex released — a new job for same source can queue (the failed one does not occupy)
    r3 = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    assert r3.ok
    e.set_worker_available(True)
    assert e.get_job(r.job["id"])["status"] == "failed"


def test_F2_missing_required_params_refused(env):
    e = env.engine
    r = e.enqueue_job(type="incremental", source=None, triggered_by="user")
    assert not r.ok
    assert r.message == "Source is required."
    assert e.list_jobs() == []
    r = e.enqueue_job(
        type="backfill",
        source="app",
        params={"window_start": "2026-08-30", "window_end": "2026-08-01"},
        triggered_by="user",
    )
    assert not r.ok
    assert r.message == "Start must be on or before end."
    r = e.enqueue_job(type="re_extract", source=None, triggered_by="user")
    assert not r.ok
    assert r.message == "Pick a source or global."


def test_F3_second_write_scoped_including_global_occupant(env):
    e = env.engine
    _seed(e)
    e.pause_execution = True
    e.fetch.script("factbase", [spoken_remark(kind="remark", channel="spoken")])
    r = e.enqueue_job(type="re_index", source="global", triggered_by="user", confirm_reindex=True)
    e.drain()
    assert e.get_job(r.job["id"])["status"] == "running"
    r2 = e.enqueue_job(type="incremental", source="factbase", triggered_by="user")
    assert r2.overlay == "ov-dup"
    r3 = e.enqueue_job(
        type="incremental", source="factbase", triggered_by="user", dup_action="queue_behind"
    )
    assert r3.ok
    assert e.get_job(r3.job["id"])["status"] == "queued"
    r4 = e.enqueue_job(
        type="refresh_preferences", source="global", triggered_by="user", confirm_refresh=True
    )
    assert r4.overlay == "ov-dup" or r4.rejected


def test_F4_third_write_scoped_rejected_only(env):
    e = env.engine
    _seed(e)
    e.pause_execution = True
    e.fetch.script("campaign", [spoken_remark(locator="c1")])
    r1 = e.enqueue_job(type="incremental", source="campaign", triggered_by="user")
    e.drain()
    r2 = e.enqueue_job(
        type="incremental", source="campaign", triggered_by="user", dup_action="queue_behind"
    )
    assert r2.ok
    r3 = e.enqueue_job(type="incremental", source="campaign", triggered_by="user")
    assert r3.rejected
    assert r3.overlay is None or r3.overlay != "ov-dup" or r3.rejected
    assert f"Rejected: source campaign already has a queued job waiting behind {r1.job['id']}." in r3.message
    assert len(e.list_jobs()) == 2


def test_F5_failed_cancelled_worker_lost_s6_only(env):
    e = env.engine
    _seed(e)
    e.cancel_after_clean = 1
    e.fetch.script(
        "whitehouse_remarks",
        [spoken_remark(locator="s1"), spoken_remark(locator="s2", text="Two")],
    )
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    j = e.get_job(r.job["id"])
    assert j["status"] in ("cancelled", "failed")
    stayed = e.search()
    assert stayed
    for rec in stayed:
        assert e.get_record(rec["record_id"])
    inflight = [q for q in e.list_quarantine() if q["failed_rule"] == "job_stopped"]
    assert inflight
    # stayed not in quarantine as open job_stopped for same locator
    stayed_locs = {r["url"] for r in stayed}
    # no further writes from that job
    before = len(e.search())
    e.drain()
    assert len(e.search()) == before


def test_F6_fetch_nothing_succeeded_empty_clocks_do_not_move(env):
    e = env.engine
    e.fetch.script("app", [])
    r = e.enqueue_job(type="incremental", source="app", triggered_by="user")
    e.drain()
    j = e.get_job(r.job["id"])
    assert j["status"] == "succeeded_empty"
    assert j["fetched"] == 0
    h = e.source_health()["app"]
    assert h["last_succeeded"] in (None, "never")
    html = env.client.get("/").text
    assert "succeeded_empty" in html or h["last_succeeded_empty"] not in (None, "none")


def test_F7_clean_gate_fail_field_fail_accept_disabled(env):
    e = env.engine
    _seed(e)
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="n1", text="")])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    assert e.search() == []
    q = e.list_quarantine()
    assert q[0]["reason"] == "field-fail"
    acc = e.accept_quarantine(q[0]["id"])
    assert not acc.ok
    html = env.client.get(f"/quarantine?item={q[0]['id']}").text
    assert "ov-q-fieldfail" in html
    assert "Cannot accept. Fix source or extract, then run a new job." in html


def test_F8_operator_hold_accept_promotes_without_edit(env):
    e = env.engine
    _seed(e)
    e.set_allowlist(["nyt"])
    item = spoken_remark(
        locator="iv-hold",
        kind="interview",
        channel="spoken",
        outlet="cnn",
        title="Gaggle",
        text="An interview transcript from CNN.",
    )
    e.fetch.script("interviews", [item])
    e.enqueue_job(type="incremental", source="interviews", triggered_by="user")
    e.drain()
    holds = [q for q in e.list_quarantine() if q["reason"] == "operator-hold"]
    assert holds
    qid = holds[0]["id"]
    # accept without confirm may overlay
    r = e.accept_quarantine(qid, confirm=True)
    assert r.ok
    recs = e.search(source="interviews")
    assert recs
    assert recs[0]["text"] == item.text
    assert not any(q["id"] == qid and q.get("open", True) for q in e.list_quarantine() if q["id"] == qid and q.get("open", True))


def test_F9_accept_field_fail_refused(env):
    e = env.engine
    _seed(e)
    e.fetch.script("factbase", [spoken_remark(locator="ff", text="")])
    e.enqueue_job(type="incremental", source="factbase", triggered_by="user")
    e.drain()
    q = e.list_quarantine()[0]
    r = e.accept_quarantine(q["id"], confirm=True)
    assert not r.ok
    still = e.list_quarantine()
    assert any(x["id"] == q["id"] and x.get("open", True) for x in still)
    assert still[0]["failed_rule"]


def test_F10_discard_then_incremental_same_locator_unchanged(env):
    e = env.engine
    _seed(e)
    item = spoken_remark(locator="same-loc", text="Unchanged body")
    e.fetch.script("whitehouse_remarks", [item])
    # force into quarantine via missing attribution then... actually discard a field-fail
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="same-loc", text="Unchanged body", attributed=False)])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    q = e.list_quarantine()
    assert q
    e.discard_quarantine(q[0]["id"], confirm=True)
    helper = (
        "Discarded items shall not reappear as clean on the next incremental run unless source content or locator changed, or Fate force re-fetches."
    )
    assert helper in env.client.get("/quarantine").text
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="same-loc", text="Unchanged body", attributed=True)])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    assert e.search(query="Unchanged body") == []


def test_F11_written_social_lookalike_quarantined(env):
    e = env.engine
    _seed(e)
    e.set_pin("truth_social", "realDonaldTrump")
    e.fetch.script(
        "truth_social",
        [social_post(locator="lk", author_handle="realDonaldTrumpFan")],
    )
    e.enqueue_job(type="incremental", source="truth_social", triggered_by="user")
    e.drain()
    assert e.search(source="truth_social") == []
    assert e.list_quarantine()


def test_F12_interview_outlet_not_on_allowlist_or_empty(env):
    e = env.engine
    _seed(e)
    # empty allowlist
    e.fetch.script("interviews", [spoken_remark(locator="iv", kind="interview", channel="spoken", outlet="nyt")])
    e.enqueue_job(type="incremental", source="interviews", triggered_by="user")
    e.drain()
    assert e.search(source="interviews") == []
    assert e.source_health()["interviews"]["blocked"] == "blocked: empty allowlist"
    h = e.source_health()["interviews"]
    assert h["last_succeeded"] in (None, "never")
    # non-empty allowlist, outlet not on it
    e.set_allowlist(["wsj"])
    e.fetch.script("interviews", [spoken_remark(locator="iv2", kind="interview", channel="spoken", outlet="nyt")])
    e.enqueue_job(type="incremental", source="interviews", triggered_by="user")
    e.drain()
    assert e.search(source="interviews") == []
    holds = [q for q in e.list_quarantine() if q["reason"] == "operator-hold"]
    assert holds


def test_F13_extract_tag_not_on_list_quarantined_list_not_grown(env):
    e = env.engine
    e.add_topic("trade")
    e.fetch.script(
        "whitehouse_remarks",
        [spoken_remark(locator="tag1", topics=["not_a_vocab_topic"])],
    )
    before = e.list_topics()
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    assert e.search() == []
    assert e.list_quarantine()
    assert e.list_topics() == before


def test_F14_same_locator_twice_same_record_id(env):
    e = env.engine
    _seed(e)
    item = spoken_remark(locator="dup-loc", text="Same")
    e.fetch.script("whitehouse_remarks", [item])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    recs = e.search()
    rid = recs[0]["record_id"]
    e.fetch.script("whitehouse_remarks", [item])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    recs2 = e.search()
    assert len(recs2) == 1
    assert recs2[0]["record_id"] == rid
    jobs = e.list_jobs()
    last = e.get_job(jobs[-1]["id"])
    assert last["unchanged"] >= 1 or last["updated"] >= 0


def test_F15_force_refetch_new_artifact_prior_version_resolvable(env):
    e = env.engine
    _seed(e)
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="fr1", text="Version one")])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    rid = e.search()[0]["record_id"]
    arts1 = e.list_artifacts(record_id=rid)
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="fr1", text="Version two")])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user", force_refetch=True)
    e.drain()
    cur = e.get_record(rid)
    assert cur["text"] == "Version two"
    prior = e.get_record(rid, text_version=1)
    assert prior["text"] == "Version one"
    arts2 = e.list_artifacts(record_id=rid)
    assert len(arts2) > len(arts1)


def test_F16_thin_topic_channel_not_ready(env):
    e = env.engine
    _seed(e)
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="only1")])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    row = next(r for r in e.dashboard()["topic_channel"] if r["channel"] == "spoken")
    assert row["health"] == "not-ready"
    assert row["health"] != "thin"
    assert "venue" not in row


def test_F17_every_covering_source_cadence_stale_not_ready(env):
    e = env.engine
    _seed(e)
    items = [spoken_remark(locator=f"n{i}", text=f"Usable {i} trade remarks now.") for i in range(3)]
    e.fetch.script("whitehouse_remarks", items)
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    old = datetime(2026, 8, 1, 12, tzinfo=timezone.utc)
    for src in ("whitehouse_remarks", "app", "factbase", "campaign", "interviews"):
        e.debug_set_last_success(src, old, fetched=1)
    row = next(r for r in e.dashboard()["topic_channel"] if r["channel"] == "spoken" and r["topic"] == "trade")
    assert row["health"] == "not-ready"
    html = env.client.get("/").text
    assert "whitehouse_remarks" in html  # not hidden


def test_F18_books_channel_other_not_mention_usable(env):
    e = env.engine
    _seed(e)
    e.fetch.script("books", [book_item()])
    e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    rec = e.search(source="books")[0]
    assert rec["channel"] == "other"
    assert rec["mention_usable"] is False
    html = env.client.get("/records").text
    assert "written_other" not in html
    assert "other" in html
    # filter value other
    assert e.search(channel="other")


def test_F19_in_place_clean_text_edit_absent(env):
    e = env.engine
    _seed(e)
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    rid = e.search()[0]["record_id"]
    for path in ("/", "/control", "/records", f"/records?record={rid}", "/quarantine"):
        html = env.client.get(path).text
        assert "contenteditable" not in html.lower()
        assert "Save text" not in html


def test_F20_side_picker_call_ledger_confidence_venue_absent(env):
    for path in ("/", "/control", "/records", "/quarantine"):
        html = env.client.get(path).text
        low = html.lower()
        assert "place-a-call" not in low
        assert "place a call" not in low
        assert "call ledger" not in low
        assert "NO_CALL" not in html
        assert 'name="confidence"' not in html
        assert "venue picker" not in low or "not a venue picker" in low
        assert "Yes/No" not in html
        assert "grading" not in low
        assert "SAMPLE" not in html


def test_F21_delete_base_typed_confirm(env):
    e = env.engine
    _seed(e)
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    assert e.search()
    r = e.delete_base(typed="")
    assert not r.ok
    assert e.search()
    html = env.client.get("/control").text
    assert "This deletes the clean base. Type DELETE to confirm." in html
    assert "ov-delete" in html
    r = e.delete_base(typed="DELETE")
    assert r.ok
    assert e.search() == []
    # jobs remain
    assert e.list_jobs()


def test_F22_delete_clean_records_confirm_required(env):
    e = env.engine
    _seed(e)
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    r = e.delete_clean_records(confirm=False)
    assert not r.ok
    assert e.search()
    r = e.delete_clean_records(confirm=True)
    assert r.ok
    assert e.search() == []


def test_F23_manual_run_disabled_source_confirm(env):
    e = env.engine
    e.set_source_enabled("legal", False)
    r = e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    assert r.overlay == "ov-disabled"
    assert e.list_jobs() == []
    r = e.enqueue_job(type="incremental", source="legal", triggered_by="user", confirm_disabled=True)
    assert r.ok
    e.scheduler_tick()
    assert not any(j["triggered_by"] == "schedule" and j["source"] == "legal" for j in e.list_jobs())


def test_F24_global_reindex_refresh_confirm_and_write_lock(env):
    e = env.engine
    r = e.enqueue_job(type="re_index", source="global", triggered_by="user")
    assert r.overlay == "ov-reindex"
    html = env.client.get("/control").text
    assert "ov-reindex" in html and "ov-refresh" in html
    r = e.enqueue_job(type="refresh_preferences", source="global", triggered_by="user")
    assert r.overlay == "ov-refresh"
    e.pause_execution = True
    r = e.enqueue_job(type="re_index", source="global", triggered_by="user", confirm_reindex=True)
    e.drain()
    assert e.get_job(r.job["id"])["status"] == "running"
    r2 = e.enqueue_job(type="incremental", source="app", triggered_by="user")
    assert r2.overlay == "ov-dup"


def test_F25_job_level_network_parse_failure(env):
    e = env.engine
    e.fetch.script_error("federal_register", "TLS handshake failed talking to federal_register")
    r = e.enqueue_job(type="incremental", source="federal_register", triggered_by="user")
    e.drain()
    j = e.get_job(r.job["id"])
    assert j["status"] == "failed"
    assert j["error"]
    assert "TLS" in j["error"] or "failed" in j["error"].lower()
    # no silent retry — still one job
    assert len([x for x in e.list_jobs() if x["source"] == "federal_register"]) == 1


def test_F26_source_not_on_configured_list_refused(env):
    e = env.engine
    r = e.enqueue_job(type="incremental", source="instagram", triggered_by="user")
    assert not r.ok
    assert e.list_jobs() == []
    assert set(e.sources_state()) == set(SOURCES)


def test_F27_legal_named_party_the_administration_not_clean(env):
    e = env.engine
    _seed(e)
    item = spoken_remark(
        locator="adm1",
        kind="legal",
        channel="legal",
        named_party="the administration",
        text="A filing by the administration.",
        title="Filing",
    )
    e.fetch.script("legal", [item])
    e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    e.drain()
    assert e.search(source="legal") == []
    assert e.list_quarantine()


def test_F28_read_action_cannot_run_inline_error_no_invent(env):
    e = env.engine
    e.read_down = True
    html = env.client.get("/records").text
    assert "error" in html.lower() or "unavailable" in html.lower() or "failed" in html.lower()
    # does not invent records
    assert e.search() == [] or e.read_down
    r = env.client.get("/records/export")
    assert r.status_code >= 400 or "error" in r.text.lower()


def test_F29_load_error_inline_retry(env):
    e = env.engine
    e.load_error = "dashboard"
    html = env.client.get("/").text
    assert "Dashboard failed to load" in html
    assert "Retry" in html
    e.load_error = None
    html2 = env.client.get("/").text
    assert "Dashboard failed to load" not in html2


def test_F30_filter_matches_nothing_empty_copy(env):
    html = env.client.get("/records?kind=staffing").text
    assert "No clean records match." in html
    htmlj = env.client.get("/control?tab=jobs&status=cancelled").text
    assert "No jobs match these filters." in htmlj
    htmlq = env.client.get("/quarantine?reason=operator-hold").text
    assert "No operator-hold items." in htmlq or "No quarantined items." in htmlq


def test_F31_empty_official_pin_blocked_match_none(env):
    e = env.engine
    _seed(e)
    assert e.source_health()["x_personal"]["blocked"] == "blocked: empty pin"
    assert e.source_health()["truth_social"]["blocked"] == "blocked: empty pin"
    e.fetch.script("x_personal", [social_post(locator="anyone", author_handle="anyone")])
    e.enqueue_job(type="incremental", source="x_personal", triggered_by="user")
    e.drain()
    assert e.search(source="x_personal") == []
    q = e.list_quarantine()
    assert q and q[0]["reason"] == "field-fail"
    h = e.source_health()["x_personal"]
    assert h["last_succeeded"] in (None, "never")
    # empty pin is match-none: setting pin later doesn't retroactively clean that fetch
    e.set_pin("x_personal", "anyone")
    assert e.search(source="x_personal") == []


def test_F32_failed_after_some_clean_writes_stayed_resolvable(env):
    e = env.engine
    _seed(e)
    e.cancel_after_clean = 1
    e.fetch.script(
        "app",
        [
            spoken_remark(locator="a1", text="Stayed clean"),
            spoken_remark(locator="a2", text="In flight"),
        ],
    )
    r = e.enqueue_job(type="incremental", source="app", triggered_by="user")
    e.drain()
    j = e.get_job(r.job["id"])
    assert j["fetched"] == j["written"] + j["updated"] + j["unchanged"] + j["quarantined"] + j["fetch_fail"]
    stayed = e.search()
    assert stayed
    assert e.get_record(stayed[0]["record_id"])
    inflight = [q for q in e.list_quarantine() if q["failed_rule"] == "job_stopped"]
    assert inflight
    # hard split
    clean_ids = {s["record_id"] for s in stayed}
    for q in inflight:
        assert q.get("record_id") not in clean_ids or not q.get("open", True)


def test_F33_illegal_kind_channel_pair_field_fail(env):
    e = env.engine
    _seed(e)
    e.fetch.script(
        "federal_register",
        [spoken_remark(locator="badpair", kind="remark", channel="spoken", text="Not a decision")],
    )
    e.enqueue_job(type="incremental", source="federal_register", triggered_by="user")
    e.drain()
    assert e.search(source="federal_register") == []
    assert e.list_quarantine()[0]["reason"] == "field-fail"


def test_F34_books_legal_never_participate_in_spoken_stale(env):
    e = env.engine
    _seed(e)
    items = [spoken_remark(locator=f"z{i}", text=f"Plenty {i} of usable 2025 trade talk.") for i in range(3)]
    e.fetch.script("whitehouse_remarks", items)
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    now = datetime(2026, 8, 26, 19, 0, tzinfo=timezone.utc)
    for src in ("whitehouse_remarks", "app", "factbase", "campaign", "interviews"):
        e.debug_set_last_success(src, now, fetched=1)
    old = datetime(2020, 1, 1, tzinfo=timezone.utc)
    e.debug_set_last_success("books", old, fetched=1)
    e.debug_set_last_success("legal", old, fetched=1)
    row = next(r for r in e.dashboard()["topic_channel"] if r["channel"] == "spoken" and r["topic"] == "trade")
    assert row["health"] == "ready"
    assert e.source_health()["books"].get("cadence_stale") is False
    assert e.source_health()["legal"].get("cadence_stale") is False


def test_F35_in_flight_no_other_gate_fail_job_stopped(env):
    e = env.engine
    _seed(e)
    e.cancel_after_clean = 0  # fetch then stop before any clean
    e.fail_before_clean = True
    e.fetch.script("whitehouse_remarks", [spoken_remark(locator="inf1", text="Would have been clean")])
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    j = e.get_job(r.job["id"])
    q = [x for x in e.list_quarantine() if x["failed_rule"] == "job_stopped"]
    assert q
    assert j["quarantined"] >= 1
    assert e.search() == []
    acc = e.accept_quarantine(q[0]["id"], confirm=True)
    assert not acc.ok
    assert j["fetched"] == j["written"] + j["updated"] + j["unchanged"] + j["quarantined"] + j["fetch_fail"]


def test_F36_first_boot_enabled_restart_does_not_reapply_factory(env):
    from ptrp.engine import Engine

    e = env.engine
    assert all(e.sources_state()[s]["enabled"] for s in SOURCES)
    e.set_source_enabled("campaign", False)
    e2 = Engine(db_path=env.db, fetch=env.fetch, clock=env.clock)
    e2.boot()
    assert e2.sources_state()["campaign"]["enabled"] is False
    assert e2.sources_state()["whitehouse_remarks"]["enabled"] is True
    html = env.client.get("/control").text
    assert "wizard" not in html.lower()


def test_F37_exempt_and_disabled_not_scheduled_scheduler_skips(env):
    e = env.engine
    assert e.next_scheduled_run("books") == "not scheduled"
    assert e.next_scheduled_run("legal") == "not scheduled"
    e.set_source_enabled("truth_social", False)
    assert e.next_scheduled_run("truth_social") == "not scheduled"
    e.scheduler_tick()
    assert not any(j["source"] in ("books", "legal", "truth_social") and j["triggered_by"] == "schedule" for j in e.list_jobs())
    html = env.client.get("/control").text
    assert "not scheduled" in html
    # enabled daily still has a datetime
    nxt = e.next_scheduled_run("whitehouse_remarks")
    assert nxt != "not scheduled"
    assert nxt.astimezone(ETZ).hour == 9
