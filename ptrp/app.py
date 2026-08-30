"""FastAPI UI + JSON. No auth. Times displayed ET."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from ptrp.constants import (
    CADENCE,
    CHANNELS,
    COPY,
    JOB_TYPES,
    KINDS,
    SOURCES,
    STATUS_PILLS,
    TERMS,
)
from ptrp.engine import Engine, format_et
from ptrp.fetch import HttpFetch

TEMPLATES_DIR = Path(__file__).parent / "templates"


def _esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def chrome(engine, active, body, extra_banner=""):
    pill = "available" if engine.worker_available else "not available"
    qn = sum(1 for q in engine.list_quarantine() if q.get("open"))
    banner = ""
    if not engine.worker_available:
        banner = f'<div id="worker-banner" class="banner">{COPY["worker_banner"]}</div>'
    if extra_banner:
        banner += extra_banner
    nav = []
    for href, label, key in (
        ("/", "Dashboard", "dashboard"),
        ("/control", "Control", "control"),
        ("/records", "Records", "records"),
        ("/quarantine", "Quarantine", "quarantine"),
    ):
        cls = ' class="active"' if active == key else ""
        nav.append(f'<a href="{href}"{cls}>{label}</a>')
    clock = format_et(engine.now())
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>PTRP</title>
<style>
body{{font-family:ui-sans-serif,system-ui,sans-serif;margin:0;color:#111}}
header{{display:flex;gap:1rem;align-items:center;padding:.75rem 1rem;border-bottom:1px solid #ddd}}
#product{{font-weight:700;letter-spacing:.04em}}
nav a{{margin-right:.75rem;text-decoration:none;color:#333}}
nav a.active{{font-weight:700;border-bottom:2px solid #111}}
.banner{{background:#111;color:#fff;padding:.5rem 1rem}}
.pill{{display:inline-block;padding:.1rem .4rem;border-radius:999px;border:1px solid #888;font-variant-numeric:tabular-nums}}
.pill.succeeded_empty{{background:#e8f5e9}}
main{{padding:1rem}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}
th,td{{border-bottom:1px solid #eee;padding:.35rem .4rem;text-align:left}}
.tiles span{{display:inline-block;margin:.25rem 1rem .25rem 0}}
.overlay{{border:1px solid #ccc;padding:.75rem;margin:1rem 0;background:#fafafa}}
.helper{{color:#444;font-size:.9rem}}
.error{{color:#a00}}
button:disabled{{opacity:.5}}
.kind-tile{{display:inline-block;min-width:6rem;border:1px solid #ddd;padding:.5rem;margin:.25rem}}
</style></head>
<body>
<header>
  <span id="product">PTRP</span>
  <span id="worker-pill" class="pill">{pill}</span>
  <a id="q-badge" href="/quarantine">{qn}</a>
  <nav>{''.join(nav)}</nav>
  <span id="clock">{clock}</span>
</header>
{banner}
<main>{body}</main>
</body></html>"""


def render_dashboard(engine: Engine) -> str:
    if engine.load_error == "dashboard":
        body = f'<p class="error">{COPY["dashboard_fail"]}</p><form method="get" action="/"><button>Retry</button></form>'
        return chrome(engine, "dashboard", body)
    d = engine.dashboard()
    tiles = "".join(
        f'<div class="kind-tile" data-kind="{k}"><div>{k}</div><div>{d["kinds"].get(k, 0)}</div></div>'
        for k in KINDS
    )
    newest = COPY["newest_none"] if not d["newest"] else f'Newest clean record {format_et(d["newest"])}'
    snap = (
        f'<div id="job-snapshot">Queued {len(d["queued"])} '
        f'Running {len(d["running"])} Failed {len(d["failed"])}</div>'
    )
    if not d["queued"] and not d["running"] and not d["failed"]:
        snap += f'<p>{COPY["empty_snapshot"]}</p>'
    failed_list = "<ul>"
    for j in d["failed"]:
        failed_list += (
            f'<li>{_esc(j["id"])} {_esc(j["type"])} {_esc(j["source"])} '
            f'{_esc(j.get("error") or "")} '
            f'<form method="post" action="/jobs/{j["id"]}/ack" style="display:inline">'
            f'<button id="ack-failed">Ack</button></form> '
            f'<a href="/control?job={j["id"]}">open</a></li>'
        )
    failed_list += "</ul>"
    qsplit = (
        f'<a id="q-split" href="/quarantine">field-fail {d["quarantine_field_fail"]} · '
        f'operator-hold {d["quarantine_operator_hold"]}</a>'
    )
    fam = "".join(
        f'<span class="pill">{name} {info["flag"]} {info["count"]}</span> '
        for name, info in d["families"].items()
    )
    rows = ""
    for s, h in d["sources"].items():
        last = format_et(h["last_succeeded"]) if h["last_succeeded"] else "never"
        last_e = format_et(h["last_succeeded_empty"]) if h["last_succeeded_empty"] else "none"
        en = "enabled" if h["enabled"] else "disabled"
        fresh = "no cadence" if h["cadence"] == "none" else (
            f'{h["cadence"]}'
            + (" cadence stale" if h["cadence_stale"] else "")
            + (" 24h stale" if h["stale_24h"] else "")
        )
        blocked = h["blocked"] or ""
        err = h["last_error"] or "—"
        rows += (
            f'<tr><td>{s}</td><td class="pill">{en}</td><td>{last}</td><td>{last_e}</td>'
            f'<td>{fresh}</td><td>{h["clean_count"]}</td><td>{_esc(err)}</td>'
            f'<td>{_esc(blocked)}</td></tr>'
        )
    trows = ""
    if not d["topic_channel"]:
        trows = f'<tr><td colspan="6">{COPY["empty_topics"]}</td></tr>'
    else:
        for r in d["topic_channel"]:
            trows += (
                f'<tr><td>{_esc(r["topic"])}</td><td>{r["channel"]}</td><td>{r["usable"]}</td>'
                f'<td>{_esc(r["failed_clause"])}</td><td>{r["raw_clean"]}</td>'
                f'<td class="pill">{r["health"]}</td></tr>'
            )
    body = f"""
<section id="kind-totals" class="tiles">{tiles}</section>
<p id="newest-clean">{newest}</p>
{snap}{failed_list}
<p>{qsplit}</p>
<p>Families: {fam}</p>
<table id="source-health"><thead><tr>
<th>Source</th><th>Enabled</th><th>Last succeeded</th><th>Last succeeded_empty</th>
<th>Freshness</th><th>Clean records</th><th>Last error</th><th>Status extra</th>
</tr></thead><tbody>{rows}</tbody></table>
<table id="thin-table"><thead><tr>
<th>Topic</th><th>Channel</th><th>Usable count</th><th>Failed clause</th>
<th>{COPY["raw_clean"]}</th><th>Health</th>
</tr></thead><tbody>{trows}</tbody></table>
<p class="helper">{COPY["footnote"]}</p>
"""
    return chrome(engine, "dashboard", body)


def render_control(engine: Engine, request: Request) -> str:
    tab = request.query_params.get("tab", "run")
    job_id = request.query_params.get("job")
    status_f = request.query_params.get("status")
    overlays = f"""
<div id="ov-run" class="overlay">Run job form
  <form method="post" action="/jobs">
    <label>Type <select name="type">{''.join(f'<option value="{t}">{t}</option>' for t in JOB_TYPES)}</select></label>
    <label>Source <select name="source"><option value="">(none)</option>
      {''.join(f'<option value="{s}">{s}</option>' for s in SOURCES)}
      <option value="global">global</option></select></label>
    <label>Date window start <input name="window_start"></label>
    <label>Date window end <input name="window_end"></label>
    <label>Topic <select name="topic"><option value=""></option>
      {''.join(f'<option>{_esc(t)}</option>' for t in engine.list_topics())}</select></label>
    <label>Query <input name="query"></label>
    <label>Occasion <select name="occasion"><option value=""></option>
      {''.join(f'<option>{_esc(t)}</option>' for t in engine.list_occasions())}</select></label>
    <label><input type="checkbox" name="force_refetch"> {COPY["force_refetch"]}</label>
    <button type="submit">Run</button>
  </form>
  <p class="helper">Source is required. Backfill needs a date window. Targeted needs a topic, query, or occasion. Pick a source or global. Start must be on or before end.</p>
</div>
<div id="ov-disabled" class="overlay">{COPY["disabled_confirm"]}</div>
<div id="ov-reindex" class="overlay">{COPY["reindex_confirm"]}</div>
<div id="ov-refresh" class="overlay">{COPY["refresh_confirm"]}</div>
<div id="ov-delete" class="overlay">{COPY["delete_base"]}
  <form method="post" action="/danger/delete-base"><input name="typed" placeholder="DELETE"><button>Confirm</button></form>
</div>
<div id="ov-dup" class="overlay">Queue behind / Don't start</div>
"""
    jobs = engine.list_jobs()
    if status_f and status_f != "all":
        jobs = [j for j in jobs if j["status"] == status_f]
    job_rows = ""
    if not jobs:
        job_rows = f'<tr><td colspan="8">{COPY["no_jobs"]}</td></tr>'
    else:
        for j in jobs:
            job_rows += (
                f'<tr><td><a href="/control?job={j["id"]}">{j["id"]}</a></td>'
                f'<td>{j["type"]}</td><td>{j["source"]}</td><td>{j["triggered_by"]}</td>'
                f'<td class="pill">{j["status"]}</td><td>{j["fetched"]}</td></tr>'
            )
    job_detail = ""
    if job_id:
        try:
            j = engine.get_job(job_id)
        except KeyError:
            j = None
        if j:
            job_detail = f"""
<div id="ov-job" class="overlay">
  <p>{j["id"]} {j["type"]} {j["source"]} <span class="pill">{j["status"]}</span> {j["triggered_by"]}</p>
  <p>params {_esc(j["params"])}</p>
  <p>created {format_et(_parse_maybe(j["created"]))} started {format_et(_parse_maybe(j.get("started")))} finished {format_et(_parse_maybe(j.get("finished")))}</p>
  <p>fetched {j["fetched"]} written {j["written"]} updated {j["updated"]} unchanged {j["unchanged"]} quarantined {j["quarantined"]} fetch fail {j["fetch_fail"]}</p>
  <p>{COPY["equation"]}</p>
  <p class="helper">{COPY["stopped_helper"]}</p>
  <p>error {_esc(j.get("error") or "—")}</p>
  <p>log {_esc(j.get("log"))}</p>
</div>"""
    src_rows = ""
    for s in SOURCES:
        st = engine.sources_state()[s]
        nxt = engine.next_scheduled_run(s)
        nxt_s = COPY["not_scheduled"] if nxt == COPY["not_scheduled"] else format_et(nxt if hasattr(nxt, "astimezone") else nxt)
        cad = CADENCE.get(s) or "none"
        en = "enabled" if st["enabled"] else "disabled"
        src_rows += (
            f'<tr id="next-run"><td>{s}</td><td class="pill">{en}</td><td>{cad}</td>'
            f'<td>{nxt_s}</td><td><a href="/control?tab=run&source={s}">Run</a></td></tr>'
        )
    vocabs = f"""
<div id="tab-vocabs">
  <h3>Topics</h3><ul>{''.join(f'<li>{_esc(t)}</li>' for t in engine.list_topics())}</ul>
  <form method="post" action="/vocab/topics"><input name="tag"><button>Add</button></form>
  <h3>Occasions</h3><ul>{''.join(f'<li>{_esc(t)}</li>' for t in engine.list_occasions())}</ul>
  <h3>Interview-outlet allowlist</h3>
  <p class="helper">Empty allowlist blocks the interviews source. Empty jobs do not make it fresh.</p>
  <ul>{''.join(f'<li>{_esc(o)}</li>' for o in engine.allowlist())}</ul>
  <h3>Official account pins</h3>
  <p>X pin: {_esc(engine.get_pin("x_personal")) or "(empty)"}</p>
  <p>Truth Social pin: {_esc(engine.get_pin("truth_social")) or "(empty)"}</p>
  <p class="helper">Clean written_social attribution must match these pins. A lookalike is quarantined.</p>
</div>
"""
    body = f"""
<div>
  <a href="/control?tab=run">Run job</a>
  <a href="/control?tab=jobs">Jobs</a>
  <a href="/control?tab=sources">Sources</a>
  <a href="/control?tab=vocabs">Vocabularies</a>
</div>
<div id="tab-run">{overlays}</div>
<div id="tab-jobs">
  <form method="get" action="/control">
    <input type="hidden" name="tab" value="jobs">
    <select name="status"><option value="all">all</option>
      {''.join(f'<option {"selected" if status_f==s else ""} value="{s}">{s}</option>' for s in ("queued","running","succeeded","succeeded_empty","failed","cancelled"))}
    </select>
    <button>Filter</button>
  </form>
  <table><thead><tr><th>id</th><th>type</th><th>source</th><th>triggered_by</th><th>status</th><th>fetched</th></tr></thead>
  <tbody>{job_rows}</tbody></table>
  {job_detail}
</div>
<div id="tab-sources">
  <table><thead><tr><th>Source</th><th>Enabled</th><th>Cadence</th><th>Next scheduled run</th><th>Run</th></tr></thead>
  <tbody>{src_rows}</tbody></table>
  <div class="danger">Delete clean records…
    <form method="post" action="/danger/delete-records"><button>Confirm delete records</button></form>
    Delete the base… {COPY["delete_base"]}
  </div>
</div>
{vocabs}
"""
    return chrome(engine, "control", body)


def _parse_maybe(v):
    from ptrp.engine import _parse_dt
    return _parse_dt(v)


def render_records(engine: Engine, request: Request) -> str:
    extra = ""
    if engine.read_down:
        extra = '<p class="error">Records search is unavailable. Retry. The app does not invent records.</p>'
        body = extra + '<p class="error">Export failed: control down.</p>'
        return chrome(engine, "records", body, extra_banner="")
    qp = request.query_params
    filters = {}
    if qp.get("kind"):
        filters["kind"] = qp.get("kind")
    if qp.get("source"):
        filters["source"] = qp.get("source")
    if qp.get("channel"):
        filters["channel"] = qp.get("channel")
    if qp.get("q"):
        filters["query"] = qp.get("q")
    recs = engine.search(**filters)
    rows = ""
    if not recs:
        rows = f'<tr><td colspan="8">{COPY["no_records"]}</td></tr>'
    else:
        for r in recs:
            rows += (
                f'<tr><td><a href="/records?record={r["record_id"]}">{r["record_id"]}</a></td>'
                f'<td>{r["kind"]}</td><td>{r["source"]}</td><td>{r["channel"]}</td>'
                f'<td>{format_et(_parse_maybe(r.get("event_time")))}</td>'
                f'<td>{r["completeness"]}</td><td>{"yes" if r["mention_usable"] else "no"}</td>'
                f'<td>{_esc(r["title"])}</td></tr>'
            )
    export_btn = (
        f'<a id="btn-export" href="/records/export">{COPY["export"]}</a>'
        if recs
        else f'<button id="btn-export" disabled>{COPY["export"]}</button><p>{COPY["nothing_export"]}</p>'
    )
    rec_id = qp.get("record")
    drawer = ""
    if rec_id:
        rec = engine.get_record(rec_id)
        if rec:
            vers = engine.conn.execute(
                "SELECT text_version FROM record_versions WHERE record_id=? ORDER BY text_version",
                (rec_id,),
            ).fetchall()
            vlist = " ".join(f'v{v["text_version"]}' for v in vers)
            pref_cites = "No derived preference cites this record."
            books_h = COPY["books_helper"] if rec["channel"] == "other" else ""
            drawer = f"""
<div id="ov-record" class="overlay">
  <p>{rec["record_id"]} {rec["kind"]} {rec["source"]} {rec["channel"]} {rec["completeness"]}
     mention-usable {rec["mention_usable"]} decision-usable {rec["decision_usable"]}</p>
  <div id="record-text">{_esc(rec["text"])}</div>
  <p>Version switcher {vlist}</p>
  <p>Extract topics {rec["topics"]} people {rec["people"]} phrases {rec["phrases"]} occasion {rec["occasion"]}</p>
  <p>event_time {format_et(_parse_maybe(rec.get("event_time")))} published_time {format_et(_parse_maybe(rec.get("published_time")))}</p>
  <p>Provenance artifact job {rec["job_id"]} source {rec["source"]}</p>
  <p>{pref_cites}</p>
  <div id="record-correct">
    <a href="/control?tab=sources">Open source config</a>
    <a href="/control?tab=run">Start re_extract</a>
    <a href="/control?tab=run">Start re-ingest</a>
  </div>
  <p class="helper">{COPY["correction"]}</p>
  <p class="helper">{books_h}</p>
</div>"""
    body = f"""
<form id="records-filters" method="get" action="/records">
  <input name="q" placeholder="Search">
  <select name="kind"><option value="">all</option>{''.join(f'<option>{k}</option>' for k in KINDS)}</select>
  <select name="source"><option value="">all</option>{''.join(f'<option>{s}</option>' for s in SOURCES)}</select>
  <label>Event time (ET) <input name="event_start"><input name="event_end"></label>
  <label>Published time (ET) <input name="pub_start"><input name="pub_end"></label>
  <select name="channel"><option value="">all</option>{''.join(f'<option>{c}</option>' for c in CHANNELS)}</select>
  <select name="term"><option value="">all</option>{''.join(f'<option>{t}</option>' for t in TERMS)}</select>
  <select name="mention_usable"><option value="">all</option><option>yes</option><option>no</option></select>
  <select name="decision_usable"><option value="">all</option><option>yes</option><option>no</option></select>
  <button>Apply</button>
</form>
{export_btn}
<form method="get" action="/records"><input name="pref_topic" placeholder="topic">
<button>Open preference</button></form>
<table><thead><tr><th>id</th><th>kind</th><th>source</th><th>channel</th><th>event_time ET</th>
<th>completeness</th><th>mention-usable</th><th>title</th></tr></thead>
<tbody>{rows}</tbody></table>
{drawer}
"""
    pref_topic = qp.get("pref_topic")
    if pref_topic:
        pref = engine.get_preference(pref_topic)
        body += f'<div id="preference">{_esc(pref)}</div>'
    return chrome(engine, "records", extra + body)


def render_quarantine(engine: Engine, request: Request) -> str:
    reason = request.query_params.get("reason", "all")
    items = [q for q in engine.list_quarantine() if q.get("open") or q.get("discarded")]
    if reason in ("field-fail", "operator-hold"):
        items = [q for q in items if q["reason"] == reason and q.get("open")]
        empty = f"No {reason} items." if not items else ""
    else:
        empty = COPY["no_q"] if not [q for q in items if q.get("open")] else ""
    rows = ""
    if empty:
        rows = f'<tr><td colspan="6">{empty}</td></tr>'
    else:
        for q in items:
            if not q.get("open") and not q.get("discarded"):
                continue
            rows += (
                f'<tr><td><a href="/quarantine?item={q["id"]}">{q["id"]}</a></td>'
                f'<td>{q["source"]}</td><td>{_esc(q["failed_rule"])}</td>'
                f'<td class="pill">{q["reason"]}</td><td>{q["job_id"]}</td></tr>'
            )
    item_id = request.query_params.get("item")
    drawer = ""
    if item_id:
        q = engine.get_quarantine(item_id)
        if q:
            oid = "ov-q-fieldfail" if q["reason"] == "field-fail" or q["failed_rule"] == "job_stopped" else "ov-q-hold"
            accept_dis = "disabled" if q["reason"] == "field-fail" or q["failed_rule"] == "job_stopped" else ""
            helper = COPY["accept_fieldfail"] if accept_dis else "Promote this item to clean? Fields will not be edited."
            if q["failed_rule"] == "job_stopped":
                helper = COPY["job_stopped_accept"]
            drawer = f"""
<div id="{oid}" class="overlay">
  <p>{_esc(q["locator"])} {q["source"]} {q["failed_rule"]} {q["reason"]}</p>
  <p>fields (read-only) {_esc(q.get("fields"))}</p>
  <form method="post" action="/quarantine/{q["id"]}/accept">
    <button {accept_dis}>Accept</button>
  </form>
  <p class="helper">{helper}</p>
  <form method="post" action="/quarantine/{q["id"]}/discard"><button>Discard</button></form>
</div>"""
    body = f"""
<form id="q-reason" method="get" action="/quarantine">
  <select name="reason"><option>all</option><option>field-fail</option><option>operator-hold</option></select>
  <button>Filter</button>
</form>
<p id="q-discard-helper" class="helper">{COPY["discard_helper"]}</p>
<p class="helper">{COPY["accept_fieldfail"]}</p>
<table><thead><tr><th>id</th><th>source</th><th>failed rule</th><th>reason</th><th>job</th></tr></thead>
<tbody>{rows}</tbody></table>
{drawer}
"""
    return chrome(engine, "quarantine", body)


def create_app(engine: Engine | None = None, background: bool = False) -> FastAPI:
    if engine is None:
        db = Path(os.environ.get("PTRP_DB", "data/ptrp.sqlite"))
        db.parent.mkdir(parents=True, exist_ok=True)
        engine = Engine(db_path=db, fetch=HttpFetch())
        engine.boot()
        background = True
    app = FastAPI(title="PTRP")
    app.state.engine = engine

    if background:
        import threading
        import time

        def loop():
            while True:
                try:
                    engine.scheduler_tick()
                    engine.drain()
                except Exception:
                    pass
                time.sleep(5)

        threading.Thread(target=loop, daemon=True).start()

    @app.get("/", response_class=HTMLResponse)
    def dashboard():
        return HTMLResponse(render_dashboard(engine))

    @app.get("/control", response_class=HTMLResponse)
    def control(request: Request):
        return HTMLResponse(render_control(engine, request))

    @app.get("/records", response_class=HTMLResponse)
    def records(request: Request):
        return HTMLResponse(render_records(engine, request))

    @app.get("/records/export")
    def export(request: Request):
        if engine.read_down:
            return JSONResponse({"error": "Records export is unavailable."}, status_code=503)
        data = engine.export_retrieval_set()
        return JSONResponse(data)

    @app.get("/quarantine", response_class=HTMLResponse)
    def quarantine(request: Request):
        return HTMLResponse(render_quarantine(engine, request))

    @app.post("/jobs")
    async def post_job(request: Request):
        ct = request.headers.get("content-type", "")
        if "json" in ct:
            body = await request.json()
        else:
            form = await request.form()
            body = dict(form)
        r = engine.enqueue_job(
            type=body.get("type"),
            source=body.get("source") or None,
            params={
                "window_start": body.get("window_start"),
                "window_end": body.get("window_end"),
                "topic": body.get("topic"),
                "query": body.get("query"),
                "occasion": body.get("occasion"),
            },
            force_refetch=bool(body.get("force_refetch")),
            confirm_disabled=bool(body.get("confirm_disabled")),
            confirm_reindex=bool(body.get("confirm_reindex")),
            confirm_refresh=bool(body.get("confirm_refresh")),
            dup_action=body.get("dup_action"),
        )
        if r.ok:
            engine.drain()
        return JSONResponse({"ok": r.ok, "overlay": r.overlay, "message": r.message, "job": r.job, "rejected": r.rejected})

    @app.post("/jobs/{job_id}/ack")
    def ack(job_id: str):
        engine.ack(job_id)
        return JSONResponse({"ok": True})

    @app.post("/jobs/{job_id}/cancel")
    def cancel(job_id: str):
        r = engine.cancel(job_id)
        return JSONResponse({"ok": r.ok, "message": r.message})

    @app.post("/jobs/{job_id}/retry")
    def retry(job_id: str):
        r = engine.retry(job_id)
        return JSONResponse({"ok": r.ok, "job": r.job, "message": r.message, "overlay": r.overlay})

    @app.post("/danger/delete-base")
    async def del_base(request: Request):
        form = await request.form()
        r = engine.delete_base(typed=form.get("typed") or "")
        return JSONResponse({"ok": r.ok, "message": r.message})

    @app.post("/danger/delete-records")
    async def del_recs():
        r = engine.delete_clean_records(confirm=True)
        return JSONResponse({"ok": r.ok})

    @app.post("/vocab/topics")
    async def add_topic(request: Request):
        form = await request.form()
        if form.get("tag"):
            engine.add_topic(form.get("tag"))
        return JSONResponse({"ok": True})

    @app.post("/quarantine/{qid}/accept")
    def q_acc(qid: str):
        r = engine.accept_quarantine(qid, confirm=True)
        return JSONResponse({"ok": r.ok, "message": r.message})

    @app.post("/quarantine/{qid}/discard")
    def q_dis(qid: str):
        r = engine.discard_quarantine(qid, confirm=True)
        return JSONResponse({"ok": r.ok, "message": r.message})

    return app
