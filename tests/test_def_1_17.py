"""DEF-1 through DEF-17. HTML operator POST and Spec A/F cases those defects violate."""

from __future__ import annotations

from ptrp.fetch import parse_fetched
from tests.conftest import book_item, social_post, spoken_remark


def _form(client, path, **data):
    return client.post(path, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})


def _src_row(html, source):
    start = html.find('<table id="source-health">')
    chunk = html[start:]
    i = chunk.find("<td>" + source + "</td>")
    assert i >= 0, source + " missing from source-health"
    end = chunk.find("</tr>", i)
    return chunk[i:end if end > i else i + 400]


def test_DEF1_QA_A1_freshness_cadence_and_24h_never_succeeded(env):
    html = env.client.get("/").text
    actions = _src_row(html, "whitehouse_actions")
    assert "cadence stale" in actions
    assert "24h stale" in actions
    assert "never succeeded" in actions
    fr = _src_row(html, "federal_register")
    assert "cadence stale" in fr
    assert "24h stale" in fr
    assert "never succeeded" in fr
    books = _src_row(html, "books")
    assert "no cadence" in books
    assert "cadence stale" not in books
    interviews = _src_row(html, "interviews")
    assert "cadence stale" in interviews
    assert "24h stale" in interviews
    assert "never succeeded" in interviews
    ts = _src_row(html, "truth_social")
    assert "cadence stale" in ts
    assert "blocked: empty pin" in html


def test_DEF2_QA_A2_html_run_form_urlencoded_enqueues(env):
    r = _form(env.client, "/jobs", type="incremental", source="books")
    assert r.status_code != 500
    assert r.status_code in (200, 303, 302)
    jobs = env.engine.list_jobs()
    assert jobs, "HTML POST /jobs must enqueue a job"
    j = jobs[-1]
    assert j["type"] == "incremental"
    assert j["source"] == "books"
    env.engine.drain()
    j = env.engine.get_job(j["id"])
    assert j["status"] in ("queued", "running", "succeeded", "succeeded_empty", "failed")


def test_DEF3_QA_A3_ov_job_links_and_actions(env):
    e = env.engine
    e.add_topic("trade")
    e.add_occasion("press_conference")
    e.pause_execution = True
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    jid = r.job["id"]
    html = env.client.get("/control?job=" + jid).text
    assert 'id="ov-job"' in html
    assert "Cancel" in html
    assert "Cancel job " + jid + "?" in html
    assert "Clean records already written stay. In-flight items go to quarantine as job_stopped." in html
    e.pause_execution = False
    e.drain()
    j = e.get_job(jid)
    html = env.client.get("/control?job=" + jid).text
    assert "artifact" in html.lower()
    if j["written"] or j["updated"]:
        recs = e.search(source="whitehouse_remarks")
        assert recs
        assert recs[0]["record_id"] in html
    e.fetch.script_error("factbase", "network timeout talking to factbase")
    rf = e.enqueue_job(type="incremental", source="factbase", triggered_by="user")
    e.drain()
    fid = rf.job["id"]
    html_f = env.client.get("/control?job=" + fid).text
    assert "Retry" in html_f
    assert "Ack" in html_f


def test_DEF4_QA_A4_F2_html_missing_params_inline_refuse_no_500(env):
    before = len(env.engine.list_jobs())
    r = _form(env.client, "/jobs", type="incremental", source="")
    assert r.status_code != 500
    body = r.text
    assert "Source is required." in body
    assert len(env.engine.list_jobs()) == before

    r = _form(env.client, "/jobs", type="backfill", source="books")
    assert r.status_code != 500
    assert "Backfill needs a date window." in r.text
    assert len(env.engine.list_jobs()) == before

    r = _form(env.client, "/jobs", type="targeted", source="books")
    assert r.status_code != 500
    assert "Targeted needs a topic, query, or occasion." in r.text
    assert len(env.engine.list_jobs()) == before

    r = _form(env.client, "/jobs", type="re_extract", source="")
    assert r.status_code != 500
    assert "Pick a source or global." in r.text

    r = _form(
        env.client, "/jobs", type="backfill", source="books",
        window_start="2026-08-30", window_end="2026-08-01",
    )
    assert r.status_code != 500
    assert "Start must be on or before end." in r.text
    assert len(env.engine.list_jobs()) == before


def test_DEF5_QA_A5_A5b_F3_F4_ov_dup_real_choice(env):
    e, c = env.engine, env.client
    e.pause_execution = True
    e.fetch.script("truth_social", [social_post()])
    r1 = _form(c, "/jobs", type="incremental", source="truth_social")
    assert r1.status_code != 500
    jobs = e.list_jobs()
    assert len(jobs) == 1
    j1 = jobs[0]["id"]
    e.drain()
    assert e.get_job(j1)["status"] == "running"

    html_ctrl = c.get("/control").text
    assert 'id="ov-dup"' in html_ctrl

    r2 = _form(c, "/jobs", type="incremental", source="truth_social")
    assert r2.status_code != 500
    text = r2.text
    assert "Queue behind" in text
    assert "Don't start" in text
    assert 'id="ov-dup"' in text
    assert len(e.list_jobs()) == 1

    r_ds = _form(c, "/jobs", type="incremental", source="truth_social", dup_action="dont_start")
    assert r_ds.status_code != 500
    assert len(e.list_jobs()) == 1
    assert ("Rejected: a job for this source is already queued or running (job " + j1 + "). A second job would write the same source.") in r_ds.text

    r_qb = _form(c, "/jobs", type="incremental", source="truth_social", dup_action="queue_behind")
    assert r_qb.status_code != 500
    assert len(e.list_jobs()) == 2
    j2 = [j for j in e.list_jobs() if j["id"] != j1][0]
    assert j2["status"] == "queued"
    assert j2["waiting_reason"] == "waiting: same source as " + j1

    r3 = _form(c, "/jobs", type="incremental", source="truth_social")
    assert r3.status_code != 500
    assert len(e.list_jobs()) == 2
    assert ("Rejected: source truth_social already has a queued job waiting behind " + j1 + ".") in r3.text

    rg = _form(c, "/jobs", type="re_extract", source="global")
    assert rg.status_code != 500
    assert len(e.list_jobs()) == 2


def test_DEF6_QA_A6_cancel_confirm_and_toast(env):
    e, c = env.engine, env.client
    e.pause_execution = True
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    r = e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    jid = r.job["id"]
    html = c.get("/control?tab=jobs").text
    assert "Cancel" in html
    html_j = c.get("/control?job=" + jid).text
    assert "Cancel job " + jid + "? Clean records already written stay. In-flight items go to quarantine as job_stopped." in html_j
    rc = _form(c, "/jobs/" + jid + "/cancel")
    assert rc.status_code != 500
    assert e.get_job(jid)["status"] == "cancelled"
    assert "Job cancelled. Stayed clean remain. In-flight quarantined as job_stopped." in rc.text


def test_DEF7_QA_A8_F23_enable_disable_toggle_and_ov_disabled(env):
    c = env.client
    html = c.get("/control?tab=sources").text
    assert 'id="ov-disabled"' in html
    marker = html.find('id="ov-disabled"')
    around = html[max(0, marker - 80):marker + 80]
    assert "hidden" in around or "is-hidden" in around or "display:none" in around
    r = _form(c, "/sources/campaign/enabled", enabled="0")
    assert r.status_code != 500
    assert env.engine.sources_state()["campaign"]["enabled"] is False
    html = c.get("/control?tab=sources").text
    assert "not scheduled" in html
    r2 = _form(c, "/jobs", type="incremental", source="campaign")
    assert r2.status_code != 500
    assert env.engine.list_jobs() == []
    assert "This source is disabled. Scheduler will not run it. Manual Run still enqueues. Continue?" in r2.text
    assert "Confirm" in r2.text and "Cancel" in r2.text
    r3 = _form(c, "/jobs", type="incremental", source="campaign", confirm_disabled="1")
    assert r3.status_code != 500
    assert env.engine.list_jobs()


def test_DEF8_QA_A14_F13_F16_html_add_topic_shows_thin_row(env):
    r = _form(env.client, "/vocab/topics", tag="tariffs")
    assert r.status_code != 500
    assert "tariffs" in env.engine.list_topics()
    html = env.client.get("/").text
    assert "tariffs" in html
    assert "spoken" in html
    assert "written_social" in html
    assert "not-ready" in html
    assert "thin" in html.lower() or "zero usable" in html


def test_DEF9_QA_A17_records_filters_drawer_preference_copy(env):
    e, c = env.engine, env.client
    e.add_topic("trade")
    e.add_occasion("press_conference")
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    html = c.get("/records").text
    assert 'name="topic"' in html
    assert 'name="occasion"' in html
    assert "Clear" in html
    assert "published_time ET" in html or "Published time" in html
    assert "decision-usable" in html
    rec = e.search()[0]
    html_r = c.get("/records?record=" + rec["record_id"]).text
    assert rec["text"] in html_r
    assert "completeness" in html_r
    assert "mention-usable" in html_r
    assert "decision-usable" in html_r
    assert "contenteditable" not in html_r
    assert 'name="confidence"' not in html_r
    html_p = c.get("/records?pref_topic=tariffs").text
    assert "{'topic'" not in html_p
    assert "tariffs" in html_p
    assert "Supporting" in html_p or "supporting" in html_p


def test_DEF10_QA_F21_ov_delete_confirm_disabled_mismatch_no_500(env):
    html = env.client.get("/control?tab=sources").text
    assert 'id="ov-delete"' in html
    ov = html.split('id="ov-delete"')[1][:2000]
    assert "disabled" in ov
    r = _form(env.client, "/danger/delete-base", typed="delete")
    assert r.status_code != 500
    r = _form(env.client, "/danger/delete-base", typed="DELETEE")
    assert r.status_code != 500
    r = _form(env.client, "/danger/delete-base", typed="")
    assert r.status_code != 500


def test_DEF11_QA_F22_delete_clean_records_overlay_not_immediate(env):
    e = env.engine
    e.add_topic("trade")
    e.add_occasion("press_conference")
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    assert e.search()
    html = env.client.get("/control?tab=sources").text
    assert "ov-delete-records" in html
    r = _form(env.client, "/danger/delete-records")
    assert r.status_code != 500
    assert e.search(), "missing confirm must leave records"
    r3 = _form(env.client, "/danger/delete-records", confirm="1")
    assert r3.status_code != 500
    assert e.search() == []


def test_DEF12_QA_F24_ov_reindex_refresh_html_confirm_enqueues(env):
    html = env.client.get("/control").text
    assert 'id="ov-reindex"' in html
    assert 'id="ov-refresh"' in html
    r = _form(env.client, "/jobs", type="re_index", source="global")
    assert r.status_code != 500
    assert env.engine.list_jobs() == []
    assert "Rebuild the index from all stored clean records. Confirm." in r.text
    assert "Confirm" in r.text
    r2 = _form(env.client, "/jobs", type="re_index", source="global", confirm_reindex="1")
    assert r2.status_code != 500
    jobs = env.engine.list_jobs()
    assert jobs and jobs[-1]["type"] == "re_index"
    r3 = env.client.post("/jobs", json={"type": "refresh_preferences", "confirm": True})
    assert r3.status_code != 500
    body = r3.json()
    assert body.get("ok") is True
    assert body.get("job")


def test_DEF13_R_UI_18_occasions_allowlist_pins_not_topics_only(env):
    c = env.client
    html = c.get("/control?tab=vocabs").text
    assert "Occasions" in html
    r = _form(c, "/vocab/occasions", tag="press_conference")
    assert r.status_code != 500
    assert "press_conference" in env.engine.list_occasions()
    r = _form(c, "/vocab/occasions/remove", tag="press_conference")
    assert r.status_code != 500
    assert "press_conference" not in env.engine.list_occasions()
    r = _form(c, "/vocab/allowlist", outlet="nyt")
    assert r.status_code != 500
    assert "nyt" in env.engine.allowlist()
    r = _form(c, "/vocab/allowlist/remove", outlet="nyt")
    assert r.status_code != 500
    assert "nyt" not in env.engine.allowlist()
    r = _form(c, "/vocab/pins", x_personal="realDonaldTrump", truth_social="realDonaldTrump")
    assert r.status_code != 500
    assert env.engine.get_pin("x_personal") == "realDonaldTrump"
    assert env.engine.get_pin("truth_social") == "realDonaldTrump"


def test_DEF14_R_UI_8_jobs_filters_source_type_date_and_row_actions(env):
    e, c = env.engine, env.client
    e.pause_execution = True
    e.fetch.script("books", [book_item()])
    e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    e.enqueue_job(type="incremental", source="app", triggered_by="user")
    html = c.get("/control?tab=jobs").text
    assert 'name="status"' in html
    assert 'name="source"' in html
    assert 'name="type"' in html
    assert "date" in html.lower()
    html_s = c.get("/control?tab=jobs&source=books").text
    tbody = html_s.split("<tbody>")[1].split("</tbody>")[0]
    assert "books" in tbody
    assert "app" not in tbody
    html_t = c.get("/control?tab=jobs&type=incremental").text
    assert "incremental" in html_t
    assert "Cancel" in html
    e.pause_execution = False
    e.fetch.script_error("legal", "parse failed talking to legal")
    e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    e.drain()
    html_f = c.get("/control?tab=jobs&status=failed").text
    assert "Retry" in html_f
    assert "Ack" in html_f


def test_DEF15_ingest_scripted_fetch_clean_or_quarantine_and_empty_pin(env):
    e = env.engine
    e.add_topic("trade")
    e.add_occasion("press_conference")
    e.fetch.script("whitehouse_remarks", [spoken_remark()])
    e.enqueue_job(type="incremental", source="whitehouse_remarks", triggered_by="user")
    e.drain()
    recs = e.search(source="whitehouse_remarks")
    assert recs, "injected fetch must produce clean records when items pass the gate"
    assert recs[0]["source"] == "whitehouse_remarks"

    e.fetch.script("truth_social", [social_post()])
    e.enqueue_job(type="incremental", source="truth_social", triggered_by="user")
    e.drain()
    assert e.search(source="truth_social") == []
    q = [i for i in e.list_quarantine() if i["source"] == "truth_social"]
    assert q
    assert q[0]["reason"] == "field-fail"
    h = e.source_health()["truth_social"]
    assert h["last_succeeded"] in (None, "never")

    rss = '''<?xml version="1.0"?><rss><channel>
      <item><title>Remarks by President Trump</title>
      <link>https://www.whitehouse.gov/remarks/r-test</link>
      <pubDate>Sat, 15 Mar 2025 16:00:00 GMT</pubDate>
      <description>Thank you. We will build it.</description></item>
    </channel></rss>'''
    items = parse_fetched("whitehouse_remarks", rss, "https://www.whitehouse.gov/remarks/feed/")
    assert items, "production parser must extract in-scope items from public markup"
    assert items[0]["kind"] == "remark"
    assert items[0]["channel"] == "spoken"
    assert items[0]["text"]

    fr = '{"results":[{"title":"Executive Order 14100","html_url":"https://www.federalregister.gov/d/2025-1","publication_date":"2025-01-21","abstract":"An official presidential action.","presidential_document_type":"executive_order"}]}'
    items = parse_fetched("federal_register", fr, "https://www.federalregister.gov/api/v1/documents.json")
    assert items
    assert items[0]["kind"] == "decision"
    assert items[0]["channel"] == "written_official"


def test_DEF16_run_form_prefill_source_books(env):
    html = env.client.get("/control?tab=run&source=books").text
    assert 'value="books" selected' in html or 'selected>books' in html


def test_DEF17_succeeded_empty_pill_distinct_class(env):
    e = env.engine
    e.fetch.script("books", [])
    r = e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    j = e.get_job(r.job["id"])
    assert j["status"] == "succeeded_empty"
    html = env.client.get("/control?tab=jobs").text
    assert "pill succeeded_empty" in html
