"""FastAPI UI + JSON. No auth. Times displayed ET."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from ptrp.constants import (
    CADENCE,
    CHANNELS,
    COPY,
    JOB_TYPES,
    KINDS,
    SOURCES,
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


def _truthy(v):
    if v is True:
        return True
    if v is False or v is None or v == "":
        return False
    return str(v).strip().lower() in ("1", "true", "on", "yes")


def _json_safe(obj):
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]
    return str(obj)


def _blank(v):
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def chrome(engine, active, body, extra_banner="", overlay=None):
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
    if engine.worker_available:
        worker_btn = (
            '<form method="post" action="/worker/stop" style="display:inline">'
            '<button id="worker-stop" type="submit">Stop worker</button></form>'
        )
    else:
        worker_btn = (
            '<form method="post" action="/worker/start" style="display:inline">'
            f'<button id="worker-start" type="submit">{COPY["start_worker"]}</button></form>'
        )
    ov_ws_h = "" if overlay == "ov-worker-stop" else " hidden"
    ov_ws = (
        f'<div id="ov-worker-stop" class="overlay"{ov_ws_h}>{COPY["stop_worker"]}'
        '<form method="post" action="/worker/stop">'
        '<input type="hidden" name="confirm" value="1">'
        '<button type="submit">Confirm</button></form>'
        '<a href="/">Cancel</a></div>'
    )
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
.pill.succeeded{{background:#c8e6c9}}
.pill.failed{{background:#ffebee}}
.overlay{{border:1px solid #ccc;padding:.75rem;margin:1rem 0;background:#fafafa}}
.overlay[hidden],.overlay.is-hidden{{display:none}}
.helper{{color:#444;font-size:.9rem}}
.error{{color:#a00}}
.toast{{background:#e8f5e9;padding:.5rem;margin:.5rem 0}}
button:disabled{{opacity:.5}}
.kind-tile{{display:inline-block;min-width:6rem;border:1px solid #ddd;padding:.5rem;margin:.25rem}}
main{{padding:1rem}}
table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}
th,td{{border-bottom:1px solid #eee;padding:.35rem .4rem;text-align:left}}
</style></head>
<body>
<header>
  <span id="product">PTRP</span>
  <span id="worker-pill" class="pill">{pill}</span>
  {worker_btn}
  <a id="q-badge" href="/quarantine">{qn}</a>
  <nav>{''.join(nav)}</nav>
  <span id="clock">{clock}</span>
</header>
{banner}
{ov_ws}
<main>{body}</main>
</body></html>"""


def _load_error_body(screen: str) -> str:
    return (
        f'<p class="error" id="load-error">{_esc(screen)} failed to load</p>'
        f'<form method="post" action="/load-retry"><button>Retry</button></form>'
    )


def render_dashboard(engine: Engine, overlay=None) -> str:
    if engine.load_error == "dashboard":
        return chrome(engine, "dashboard", _load_error_body("Dashboard"), overlay=overlay)
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
        if h["cadence"] == "none":
            fresh = "no cadence"
        else:
            fresh = f'{_esc(h.get("cadence_age") or "")} {_esc(h.get("age_24h") or "")}'
            if h["cadence_stale"]:
                fresh += ' <span class="pill">cadence stale</span>'
            if h["stale_24h"]:
                fresh += ' <span class="pill">24h stale</span>'
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
    return chrome(engine, "dashboard", body, overlay=overlay)


def _parse_maybe(v):
    from ptrp.engine import _parse_dt
    return _parse_dt(v)


def _hidden_pending(pending):
    if not pending:
        return ""
    skip = {"dup_action", "confirm", "confirm_disabled", "confirm_reindex", "confirm_refresh"}
    out = []
    for k, v in pending.items():
        if k in skip or v is None or v == "":
            continue
        if k == "force_refetch" and not _truthy(v):
            continue
        out.append(f'<input type="hidden" name="{_esc(k)}" value="{_esc(v)}">')
    return "".join(out)


def _job_actions(j, include_confirm_copy=False):
    bits = []
    st = j["status"]
    jid = j["id"]
    if st in ("queued", "running"):
        copy = COPY["cancel_confirm"].format(id=jid)
        if include_confirm_copy:
            bits.append(f"<p>{_esc(copy)}</p>")
        bits.append(
            f'<form method="post" action="/jobs/{jid}/cancel" style="display:inline">'
            f'<button>Cancel</button></form>'
        )
    if st == "failed":
        bits.append(
            f'<form method="post" action="/jobs/{jid}/retry" style="display:inline">'
            f'<button>Retry</button></form>'
        )
        if not j.get("acknowledged"):
            bits.append(
                f'<form method="post" action="/jobs/{jid}/ack" style="display:inline">'
                f'<button>Ack</button></form>'
            )
    return " ".join(bits)


def render_control(engine: Engine, request: Request, error="", toast="", overlay=None, pending=None, blocking=None) -> str:
    if engine.load_error == "control":
        return chrome(engine, "control", _load_error_body("Control"), overlay=overlay)
    qp = request.query_params
    tab = qp.get("tab", "run")
    job_id = qp.get("job")
    status_f = qp.get("status")
    source_f = qp.get("source") if tab == "jobs" else None
    type_f = qp.get("type") if tab == "jobs" else None
    date_start = qp.get("date_start")
    date_end = qp.get("date_end")
    overlay = overlay or qp.get("overlay")
    error = error or qp.get("error") or ""
    toast = toast or qp.get("toast") or ""
    pending = pending or {}
    run_source = qp.get("source") if tab != "jobs" else pending.get("source", "")
    if not run_source:
        run_source = pending.get("source") or (qp.get("source") if tab == "run" else "") or ""

    def ov_hidden(name):
        return "" if overlay == name else " hidden"

    src_opts = ['<option value="">(none)</option>']
    for s in SOURCES:
        sel = " selected" if s == run_source else ""
        src_opts.append(f'<option value="{s}"{sel}>{s}</option>')
    src_opts.append('<option value="global">global</option>')
    type_opts = []
    run_type = pending.get("type") or "incremental"
    for t in JOB_TYPES:
        sel = " selected" if t == run_type else ""
        type_opts.append(f'<option value="{t}"{sel}>{t}</option>')

    pending_html = _hidden_pending(pending) or _hidden_pending({
        "type": pending.get("type") or "incremental",
        "source": run_source,
        "window_start": pending.get("window_start", ""),
        "window_end": pending.get("window_end", ""),
        "topic": pending.get("topic", ""),
        "query": pending.get("query", ""),
        "occasion": pending.get("occasion", ""),
    })

    run_error = f'<p class="error" id="run-error">{_esc(error)}</p>' if error else ""
    toast_html = f'<p class="toast" id="toast">{_esc(toast)}</p>' if toast else ""

    blocking_id = blocking or qp.get("blocking") or ""
    ov_dup_copy = ""
    if blocking_id:
        ov_dup_copy = f"Write-scoped job {_esc(blocking_id)} occupies source."
    overlays = f"""
<div id="ov-run" class="overlay">Run job form
  {run_error}
  <form method="post" action="/jobs">
    <label>Type <select name="type">{''.join(type_opts)}</select></label>
    <label>Targeted mode <select id="targeted-mode" name="targeted_mode">
      <option value="query"{" selected" if (pending or {}).get("targeted_mode")!="operator_item" else ""}>Query</option>
      <option value="operator_item"{" selected" if (pending or {}).get("targeted_mode")=="operator_item" else ""}>Operator item</option>
    </select></label>
    <label>Source <select name="source">{''.join(src_opts)}</select></label>
    <label>Date window start <input name="window_start" value="{_esc(pending.get('window_start', ''))}"></label>
    <label>Date window end <input name="window_end" value="{_esc(pending.get('window_end', ''))}"></label>
    <label>Topic <select name="topic"><option value=""></option>
      {''.join(f'<option>{_esc(t)}</option>' for t in engine.list_topics())}</select></label>
    <label>Query <input name="query" value="{_esc(pending.get('query', ''))}"></label>
    <label>Occasion <select name="occasion"><option value=""></option>
      {''.join(f'<option>{_esc(t)}</option>' for t in engine.list_occasions())}</select></label>
    <label><input type="checkbox" name="force_refetch"> {COPY["force_refetch"]}</label>
    <fieldset>
      <legend>Operator item</legend>
      <label>Locator <input name="locator" value="{_esc(pending.get('locator', '') if pending else '')}"></label>
      <label>Text <input name="text" value="{_esc(pending.get('text', '') if pending else '')}"></label>
      <label>Kind <input name="kind" value="{_esc(pending.get('kind', '') if pending else '')}"></label>
      <label>Channel <input name="channel" value="{_esc(pending.get('channel', '') if pending else '')}"></label>
      <div id="named-party-page"><label>named_party <input name="named_party" value="{_esc(pending.get('named_party', '') if pending else '')}"></label></div>
      <label>outlet <input name="outlet" value="{_esc(pending.get('outlet', '') if pending else '')}"></label>
      <div id="pin-match-page"><label>pin match <select name="pin_match">
        <option value="match">match</option>
        <option value="lookalike">lookalike</option>
      </select></label></div>
    </fieldset>
    <button type="submit">Run</button>
  </form>
  <p class="helper">Source is required. Backfill needs a date window. Targeted needs a topic, query, or occasion. Pick a source or global. Start must be on or before end. Operator item needs source, locator, text, kind, and channel.</p>
</div>
<div id="ov-disabled" class="overlay"{ov_hidden("ov-disabled")}>{COPY["disabled_confirm"]}
  <form method="post" action="/jobs">{pending_html}
    <input type="hidden" name="confirm_disabled" value="1">
    <button>Confirm</button>
  </form>
  <a href="/control?tab=run">Cancel</a>
</div>
<div id="ov-reindex" class="overlay"{ov_hidden("ov-reindex")}>{COPY["reindex_confirm"]}
  <form method="post" action="/jobs">
    <input type="hidden" name="type" value="re_index">
    <input type="hidden" name="source" value="global">
    <input type="hidden" name="confirm_reindex" value="1">
    <button>Confirm</button>
  </form>
  <a href="/control?tab=run">Cancel</a>
</div>
<div id="ov-refresh" class="overlay"{ov_hidden("ov-refresh")}>{COPY["refresh_confirm"]}
  <form method="post" action="/jobs">
    <input type="hidden" name="type" value="refresh_preferences">
    <input type="hidden" name="source" value="global">
    <input type="hidden" name="confirm_refresh" value="1">
    <button>Confirm</button>
  </form>
  <a href="/control?tab=run">Cancel</a>
</div>
<div id="ov-delete" class="overlay"{ov_hidden("ov-delete")}>{COPY["delete_base"]}
  <form method="post" action="/danger/delete-base">
    <input name="typed" id="delete-typed" placeholder="DELETE"
      oninput="document.getElementById('btn-delete-confirm').disabled = this.value !== 'DELETE'">
    <button id="btn-delete-confirm" disabled>Confirm</button>
  </form>
  <a href="/control?tab=sources">Cancel</a>
</div>
<div id="ov-delete-records" class="overlay"{ov_hidden("ov-delete-records")}>{COPY["delete_records"]}
  <form method="post" action="/danger/delete-records">
    <input type="hidden" name="confirm" value="1">
    <button>Confirm</button>
  </form>
  <a href="/control?tab=sources">Cancel</a>
</div>
<div id="ov-dup" class="overlay"{ov_hidden("ov-dup")}>{ov_dup_copy or "Queue behind / Don't start"}
  <form method="post" action="/jobs" style="display:inline">{pending_html}
    <input type="hidden" name="dup_action" value="queue_behind">
    <button>Queue behind</button>
  </form>
  <form method="post" action="/jobs" style="display:inline">{pending_html}
    <input type="hidden" name="dup_action" value="dont_start">
    <button>Don't start</button>
  </form>
</div>
"""
    jobs = engine.list_jobs(status=status_f, source=source_f, type=type_f, date_start=date_start, date_end=date_end)
    job_rows = ""
    if not jobs:
        job_rows = f'<tr><td colspan="8">{COPY["no_jobs"]}</td></tr>'
    else:
        for j in jobs:
            job_rows += (
                f'<tr><td><a href="/control?job={j["id"]}">{j["id"]}</a></td>'
                f'<td>{j["type"]}</td><td>{j["source"]}</td><td>{j["triggered_by"]}</td>'
                f'<td class="pill {j["status"]}">{j["status"]}</td><td>{j["fetched"]}</td>'
                f'<td>{_job_actions(j)}</td></tr>'
            )
    job_detail = ""
    if job_id:
        try:
            j = engine.get_job(job_id)
        except KeyError:
            j = None
        if j:
            arts = engine.list_artifacts(job_id=job_id)
            recs = engine.records_for_job(job_id)
            qs = engine.quarantine_for_job(job_id)
            art_links = " ".join(f'<a href="/records?record={_esc(a.get("record_id") or "")}">{_esc(a["id"])}</a>' for a in arts) or "—"
            rec_links = " ".join(f'<a href="/records?record={r["record_id"]}">{r["record_id"]}</a>' for r in recs) or "—"
            q_links = " ".join(f'<a href="/quarantine?item={q["id"]}">{q["id"]}</a>' for q in qs) or "—"
            job_detail = f"""
<div id="ov-job" class="overlay">
  <p>{j["id"]} {j["type"]} {j["source"]} <span class="pill {j["status"]}">{j["status"]}</span> {j["triggered_by"]}</p>
  <p>params {_esc(j["params"])}</p>
  <p>created {format_et(_parse_maybe(j["created"]))} started {format_et(_parse_maybe(j.get("started")))} finished {format_et(_parse_maybe(j.get("finished")))}</p>
  <p>fetched {j["fetched"]} written {j["written"]} updated {j["updated"]} unchanged {j["unchanged"]} quarantined {j["quarantined"]} fetch fail {j["fetch_fail"]}</p>
  <p>{COPY["equation"]}</p>
  <p class="helper">{COPY["stopped_helper"]}</p>
  <p>error {_esc(j.get("error") or "—")}</p>
  <p>log {_esc(j.get("log"))}</p>
  <p>artifacts {art_links}</p>
  <p>clean writes/updates {rec_links}</p>
  <p>quarantined items {q_links}</p>
  {_job_actions(j, include_confirm_copy=True)}
</div>"""
    src_rows = ""
    for s in SOURCES:
        st = engine.sources_state()[s]
        nxt = engine.next_scheduled_run(s)
        nxt_s = COPY["not_scheduled"] if nxt == COPY["not_scheduled"] else format_et(nxt if hasattr(nxt, "astimezone") else nxt)
        cad = CADENCE.get(s) or "none"
        en = "enabled" if st["enabled"] else "disabled"
        next_en = "0" if st["enabled"] else "1"
        conn = engine.get_connector(s)
        conn_opts = "".join(
            f'<option value="{v}"{" selected" if conn==v else ""}>{v}</option>'
            for v in ("ok", "network", "auth", "parse")
        )
        src_rows += (
            f'<tr id="next-run"><td>{s}</td>'
            f'<td><form method="post" action="/sources/{s}/enabled" style="display:inline">'
            f'<input type="hidden" name="enabled" value="{next_en}">'
            f'<button class="toggle">{en}</button></form></td>'
            f'<td>{cad}</td><td>{nxt_s}</td>'
            f'<td><form method="post" action="/sources/{s}/connector" style="display:inline">'
            f'<select id="connector-{s}" name="value">{conn_opts}</select>'
            f'<button>Set</button></form></td>'
            f'<td><a href="/control?tab=run&source={s}">Run</a></td></tr>'
        )
    topics_l = engine.list_topics()
    occ_l = engine.list_occasions()
    al_l = engine.allowlist()
    vocabs = f"""
<div id="tab-vocabs">
  <h3>Topics</h3>
  <ul>{''.join(f'<li>{_esc(t)} <form method="post" action="/vocab/topics/remove" style="display:inline"><input type="hidden" name="tag" value="{_esc(t)}"><button>Remove</button></form></li>' for t in topics_l)}</ul>
  <form method="post" action="/vocab/topics"><input name="tag"><button>Add</button></form>
  <h3>Occasions</h3>
  <ul>{''.join(f'<li>{_esc(t)} <form method="post" action="/vocab/occasions/remove" style="display:inline"><input type="hidden" name="tag" value="{_esc(t)}"><button>Remove</button></form></li>' for t in occ_l)}</ul>
  <form method="post" action="/vocab/occasions"><input name="tag"><button>Add</button></form>
  <h3>Interview-outlet allowlist</h3>
  <p class="helper">Empty allowlist blocks the interviews source. Empty jobs do not make it fresh.</p>
  <ul>{''.join(f'<li>{_esc(o)} <form method="post" action="/vocab/allowlist/remove" style="display:inline"><input type="hidden" name="outlet" value="{_esc(o)}"><button>Remove</button></form></li>' for o in al_l)}</ul>
  <form method="post" action="/vocab/allowlist"><input name="outlet"><button id="allowlist-add">Add</button></form>
  <h3>Official account pins</h3>
  <form method="post" action="/vocab/pins">
    <label>X pin: <input name="x_personal" value="{_esc(engine.get_pin("x_personal"))}"></label>
    <button id="pin-x-save" name="which" value="x">Save</button>
  </form>
  <form method="post" action="/vocab/pins">
    <label>Truth Social pin: <input name="truth_social" value="{_esc(engine.get_pin("truth_social"))}"></label>
    <button id="pin-ts-save" name="which" value="truth_social">Save</button>
  </form>
  <form method="post" action="/vocab/pins">
    <label>X pin: <input name="x_personal" value="{_esc(engine.get_pin("x_personal"))}"></label>
    <label>Truth Social pin: <input name="truth_social" value="{_esc(engine.get_pin("truth_social"))}"></label>
    <button>Save</button>
  </form>
  <p>X pin: {_esc(engine.get_pin("x_personal")) or "(empty)"}</p>
  <p>Truth Social pin: {_esc(engine.get_pin("truth_social")) or "(empty)"}</p>
  <p class="helper">Clean written_social attribution must match these pins. A lookalike is quarantined.</p>
</div>
"""
    src_sel = ['<option value="all">all</option>'] + [f'<option value="{s}"{" selected" if source_f==s else ""}>{s}</option>' for s in list(SOURCES)+["global"]]
    type_sel = ['<option value="all">all</option>'] + [f'<option value="{t}"{" selected" if type_f==t else ""}>{t}</option>' for t in JOB_TYPES]
    st_sel = ['<option value="all">all</option>'] + [
        f'<option {"selected" if status_f==s else ""} value="{s}">{s}</option>'
        for s in ("queued","running","succeeded","succeeded_empty","failed","cancelled")
    ]
    body = f"""
{toast_html}
<div>
  <a href="/control?tab=run">Run job</a>
  <a href="/control?tab=jobs">Jobs</a>
  <a href="/control?tab=sources">Sources</a>
  <a href="/control?tab=vocabs">Vocabularies</a>
  <a href="/control?tab=operator">Operator</a>
</div>
<div id="tab-run">{overlays}</div>
<div id="tab-jobs">
  <form method="get" action="/control">
    <input type="hidden" name="tab" value="jobs">
    <select name="status">{''.join(st_sel)}</select>
    <select name="source">{''.join(src_sel)}</select>
    <select name="type">{''.join(type_sel)}</select>
    <label>date <input name="date_start" type="date" value="{_esc(date_start or '')}">
      <input name="date_end" type="date" value="{_esc(date_end or '')}"></label>
    <button>Filter</button>
  </form>
  <table><thead><tr><th>id</th><th>type</th><th>source</th><th>triggered_by</th><th>status</th><th>fetched</th><th>actions</th></tr></thead>
  <tbody>{job_rows}</tbody></table>
  {job_detail}
</div>
<div id="tab-sources">
  <table><thead><tr><th>Source</th><th>Enabled</th><th>Cadence</th><th>Next scheduled run</th><th>Connector</th><th>Run</th></tr></thead>
  <tbody>{src_rows}</tbody></table>
  <div class="danger">Delete clean records…
    <a href="/control?tab=sources&overlay=ov-delete-records">Delete clean records</a>
    <a href="/control?tab=sources&overlay=ov-delete">Delete the base…</a>
    {COPY["delete_base"]}
    <form method="post" action="/danger/restart" style="display:inline">
      <button id="btn-restart" type="submit">Restart the app</button>
    </form>
    <div id="ov-restart" class="overlay"{ov_hidden("ov-restart")}>{COPY["restart_app"]}
      <form method="post" action="/danger/restart">
        <input type="hidden" name="confirm" value="1">
        <button>Confirm</button>
      </form>
      <a href="/control?tab=sources">Cancel</a>
    </div>
  </div>
</div>
<div id="tab-operator">
  <h3>Records reads</h3>
  <form method="post" action="/operator/records-reads">
    <select id="records-reads" name="value">
      <option value="available"{" selected" if not engine.read_down else ""}>available</option>
      <option value="down"{" selected" if engine.read_down else ""}>down</option>
    </select>
    <button>Set</button>
  </form>
  <h3>Fail next load</h3>
  <form method="post" action="/operator/fail-next-load">
    <select id="fail-next-load" name="screen">
      <option>Dashboard</option><option>Control</option><option>Records</option><option>Quarantine</option>
    </select>
    <button id="fail-next-load-set">Set</button>
  </form>
  <h3>Probe clock</h3>
  <form method="post" action="/operator/probe-clock">
    <input id="probe-clock" name="value" placeholder="YYYY-MM-DDTHH:MM">
    <button id="probe-clock-set">Set</button>
  </form>
  <form method="post" action="/operator/probe-clock-clear">
    <button id="probe-clock-clear">Clear probe clock</button>
  </form>
</div>
{vocabs}
"""
    return chrome(engine, "control", body, overlay=overlay)


def _pref_copy(pref):
    if not pref:
        return "No derived preference for this topic."
    topic = pref.get("topic") or ""
    sup = ", ".join(pref.get("supporting") or []) or "none"
    con = ", ".join(pref.get("contradicting") or []) or "none"
    cons = pref.get("consistency") or "none"
    terms = ", ".join(pref.get("terms") or []) or "none"
    return (
        f"Topic {topic}. Supporting records: {sup}. Contradicting records: {con}. "
        f"Consistency: {cons}. Terms: {terms}."
    )


def render_records(engine: Engine, request: Request, overlay=None) -> str:
    extra = ""
    if engine.load_error == "records":
        return chrome(engine, "records", _load_error_body("Records"), overlay=overlay)
    if engine.read_down:
        extra = (
            f'<p class="error" id="records-down-err">{COPY["search_cannot"]}</p>'
            f'<p class="error">{COPY["getrecord_cannot"]}</p>'
            f'<p class="error">{COPY["getpref_cannot"]}</p>'
            f'<p class="error">{COPY["export_cannot"]}</p>'
        )
        body = extra + (
            '<form id="records-filters" method="get" action="/records">'
            '<input name="q" placeholder="Search" disabled><button disabled>Apply</button></form>'
            f'<button id="btn-export" disabled>{COPY["export"]}</button>'
            '<form method="get" action="/records"><input name="pref_topic" placeholder="topic" disabled>'
            '<button disabled>Open preference</button></form>'
        )
        return chrome(engine, "records", body, overlay=overlay)
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
    if qp.get("topic"):
        filters["topic"] = qp.get("topic")
    if qp.get("occasion"):
        filters["occasion"] = qp.get("occasion")
    if qp.get("term"):
        filters["term"] = qp.get("term")
    if qp.get("event_start"):
        filters["event_start"] = qp.get("event_start")
    if qp.get("event_end"):
        filters["event_end"] = qp.get("event_end")
    if qp.get("pub_start"):
        filters["pub_start"] = qp.get("pub_start")
    if qp.get("pub_end"):
        filters["pub_end"] = qp.get("pub_end")
    if qp.get("mention_usable") == "yes":
        filters["mention_usable"] = True
    elif qp.get("mention_usable") == "no":
        filters["mention_usable"] = False
    if qp.get("decision_usable") == "yes":
        filters["decision_usable"] = True
    elif qp.get("decision_usable") == "no":
        filters["decision_usable"] = False
    recs = engine.search(**filters)
    rows = ""
    if not recs:
        rows = f'<tr><td colspan="11">{COPY["no_records"]}</td></tr>'
    else:
        for r in recs:
            topics = r.get("topics") or []
            if isinstance(topics, str):
                topics = topics
            else:
                topics = ", ".join(topics)
            rows += (
                f'<tr><td><a href="/records?record={r["record_id"]}">{r["record_id"]}</a></td>'
                f'<td>{r["kind"]}</td><td>{r["source"]}</td><td>{r["channel"]}</td>'
                f'<td>{format_et(_parse_maybe(r.get("event_time")))}</td>'
                f'<td>{format_et(_parse_maybe(r.get("published_time")))}</td>'
                f'<td>{r["completeness"]}</td>'
                f'<td>{"yes" if r["mention_usable"] else "no"}</td>'
                f'<td>{"yes" if r["decision_usable"] else "no"}</td>'
                f'<td>{_esc(r["title"])}</td><td>{_esc(topics)}</td></tr>'
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
            vlist = " ".join(
                f'<a href="/records?record={rec_id}&version={v["text_version"]}">v{v["text_version"]}</a>'
                for v in vers
            )
            arts = engine.list_artifacts(record_id=rec_id)
            art = arts[0]["id"] if arts else "—"
            pref_cites = "No derived preference cites this record."
            books_h = COPY["books_helper"] if rec["channel"] == "other" else ""
            topics = rec.get("topics") or []
            drawer = f"""
<div id="ov-record" class="overlay">
  <p>{rec["record_id"]} {rec["kind"]} {rec["source"]} {rec["channel"]} completeness {rec["completeness"]}
     mention-usable {rec["mention_usable"]} decision-usable {rec["decision_usable"]}</p>
  <div id="record-text">{_esc(rec["text"])}</div>
  <p>Version switcher {vlist}</p>
  <p>Extract topics {_esc(topics)} people {rec["people"]} phrases {rec["phrases"]} occasion {rec["occasion"]}</p>
  <p>event_time {format_et(_parse_maybe(rec.get("event_time")))} published_time {format_et(_parse_maybe(rec.get("published_time")))}</p>
  <p>Provenance artifact {_esc(art)} job <a href="/control?job={rec["job_id"]}">{rec["job_id"]}</a> source {rec["source"]}</p>
  <p>{pref_cites}</p>
  <div id="record-correct">
    <a href="/control?tab=sources">Open source config</a>
    <a href="/control?tab=run">Start re_extract</a>
    <a href="/control?tab=run">Start re-ingest</a>
  </div>
  <p class="helper">{COPY["correction"]}</p>
  <p class="helper">{books_h}</p>
  <p id="rec-named-party"{" hidden" if rec.get("kind") != "legal" else ""}>{_esc(rec.get("named_party") or "")}</p>
</div>"""
    topic_opts = "".join(f'<option value="{_esc(t)}">{_esc(t)}</option>' for t in engine.list_topics())
    occ_opts = "".join(f'<option value="{_esc(t)}">{_esc(t)}</option>' for t in engine.list_occasions())
    body = f"""
<form id="records-filters" method="get" action="/records">
  <input name="q" placeholder="Search">
  <select name="kind"><option value="">all</option>{''.join(f'<option>{k}</option>' for k in KINDS)}</select>
  <select name="source"><option value="">all</option>{''.join(f'<option>{s}</option>' for s in SOURCES)}</select>
  <label>Event time (ET) <input name="event_start"><input name="event_end"></label>
  <label>Published time (ET) <input name="pub_start"><input name="pub_end"></label>
  <label>topic <select name="topic"><option value="">all</option>{topic_opts}</select></label>
  <select name="channel"><option value="">all</option>{''.join(f'<option>{c}</option>' for c in CHANNELS)}</select>
  <label>occasion <select name="occasion"><option value="">all</option>{occ_opts}</select></label>
  <select name="term"><option value="">all</option>{''.join(f'<option>{t}</option>' for t in TERMS)}</select>
  <select name="mention_usable"><option value="">all</option><option>yes</option><option>no</option></select>
  <select name="decision_usable"><option value="">all</option><option>yes</option><option>no</option></select>
  <button>Apply</button>
  <a href="/records">Clear</a>
</form>
{export_btn}
<form method="get" action="/records"><input name="pref_topic" placeholder="topic">
<button>Open preference</button></form>
<table><thead><tr><th>id</th><th>kind</th><th>source</th><th>channel</th><th>event_time ET</th>
<th>published_time ET</th><th>completeness</th><th>mention-usable</th><th>decision-usable</th>
<th>title</th><th>topics</th></tr></thead>
<tbody>{rows}</tbody></table>
{drawer}
"""
    pref_topic = qp.get("pref_topic")
    if pref_topic:
        pref = engine.get_preference(pref_topic)
        body += f'<div id="preference">{_esc(_pref_copy(pref))}</div>'
    return chrome(engine, "records", extra + body, overlay=overlay)


def render_quarantine(engine: Engine, request: Request, overlay=None) -> str:
    if engine.load_error == "quarantine":
        return chrome(engine, "quarantine", _load_error_body("Quarantine"), overlay=overlay)
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
    return chrome(engine, "quarantine", body, overlay=overlay)


def _wants_json(request: Request) -> bool:
    ct = request.headers.get("content-type", "")
    return "json" in ct.lower()


async def _body(request: Request) -> dict:
    ct = request.headers.get("content-type", "")
    if "json" in ct.lower():
        data = await request.json()
        return data if isinstance(data, dict) else {}
    form = await request.form()
    return {k: form.get(k) for k in form.keys()}


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
                    app.state.engine.scheduler_tick()
                    app.state.engine.drain()
                except Exception:
                    pass
                time.sleep(5)

        threading.Thread(target=loop, daemon=True).start()

    def _eng():
        return app.state.engine

    def _html_any(request, overlay=None, **kw):
        engine = _eng()
        path = request.url.path
        if path.startswith("/control"):
            return HTMLResponse(render_control(engine, request, overlay=overlay, **kw))
        if path.startswith("/records"):
            return HTMLResponse(render_records(engine, request, overlay=overlay))
        if path.startswith("/quarantine"):
            return HTMLResponse(render_quarantine(engine, request, overlay=overlay))
        return HTMLResponse(render_dashboard(engine, overlay=overlay))

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request):
        return HTMLResponse(render_dashboard(_eng()))

    @app.get("/control", response_class=HTMLResponse)
    def control(request: Request):
        return HTMLResponse(render_control(_eng(), request))

    @app.get("/records", response_class=HTMLResponse)
    def records(request: Request):
        return HTMLResponse(render_records(_eng(), request))

    @app.get("/records/export")
    def export(request: Request):
        engine = _eng()
        if engine.read_down:
            return JSONResponse({"error": COPY["export_cannot"]}, status_code=503)
        data = engine.export_retrieval_set()
        return JSONResponse(data)

    @app.get("/quarantine", response_class=HTMLResponse)
    def quarantine(request: Request):
        return HTMLResponse(render_quarantine(_eng(), request))

    def _html_control(request, **kw):
        return HTMLResponse(render_control(_eng(), request, **kw))

    @app.post("/jobs")
    async def post_job(request: Request):
        try:
            body = await _body(request)
        except Exception as exc:
            if _wants_json(request):
                return JSONResponse({"ok": False, "message": str(exc), "job": None}, status_code=200)
            return _html_control(request, error=str(exc))
        job_type = _blank(body.get("type"))
        source = _blank(body.get("source"))
        confirm = _truthy(body.get("confirm"))
        try:
            engine = _eng()
            r = engine.enqueue_job(
                type=job_type,
                source=source,
                params={
                    "window_start": _blank(body.get("window_start")),
                    "window_end": _blank(body.get("window_end")),
                    "topic": _blank(body.get("topic")),
                    "query": _blank(body.get("query")),
                    "occasion": _blank(body.get("occasion")),
                    "targeted_mode": _blank(body.get("targeted_mode")) or "query",
                    "locator": _blank(body.get("locator")),
                    "text": _blank(body.get("text")),
                    "kind": _blank(body.get("kind")),
                    "channel": _blank(body.get("channel")),
                    "named_party": _blank(body.get("named_party")),
                    "outlet": _blank(body.get("outlet")),
                    "pin_match": _blank(body.get("pin_match")),
                    "event_time": _blank(body.get("event_time")),
                    "published_time": _blank(body.get("published_time")),
                    "author_handle": _blank(body.get("author_handle")),
                    "topics": body.get("topics") or [],
                },
                force_refetch=_truthy(body.get("force_refetch")),
                confirm_disabled=_truthy(body.get("confirm_disabled")),
                confirm_reindex=_truthy(body.get("confirm_reindex")) or (confirm and job_type == "re_index"),
                confirm_refresh=_truthy(body.get("confirm_refresh")) or (confirm and job_type == "refresh_preferences"),
                dup_action=_blank(body.get("dup_action")),
            )
            if r.ok:
                engine.drain()
                if r.job and r.job.get("id"):
                    try:
                        r.job = engine.get_job(r.job["id"])
                    except KeyError:
                        pass
        except Exception as exc:
            if _wants_json(request):
                return JSONResponse({"ok": False, "message": str(exc), "job": None}, status_code=200)
            return _html_control(request, error=str(exc))
        if _wants_json(request):
            return JSONResponse(_json_safe({
                "ok": r.ok, "overlay": r.overlay, "message": r.message,
                "job": r.job, "rejected": r.rejected,
            }))
        pending = {
            "type": job_type or "",
            "source": source or "",
            "window_start": body.get("window_start") or "",
            "window_end": body.get("window_end") or "",
            "topic": body.get("topic") or "",
            "query": body.get("query") or "",
            "occasion": body.get("occasion") or "",
            "targeted_mode": body.get("targeted_mode") or "",
            "locator": body.get("locator") or "",
            "text": body.get("text") or "",
            "kind": body.get("kind") or "",
            "channel": body.get("channel") or "",
            "named_party": body.get("named_party") or "",
        }
        blocking = None
        if r.overlay == "ov-dup" and r.message:
            # blocking id lives in occupants; parse from message if present
            blocking = None
            occupants = engine._occupants_for(engine._touched(job_type or "incremental", source or "global"))
            if occupants:
                blocking = occupants[0]["id"]
        if r.ok:
            return _html_control(request, toast=r.message or "Job enqueued.", overlay=None)
        return _html_control(
            request, error=r.message, overlay=r.overlay, pending=pending, blocking=blocking, toast="" if r.overlay else r.message,
        )

    @app.post("/jobs/{job_id}/ack")
    async def ack(job_id: str, request: Request):
        engine.ack(job_id)
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request, toast="Acknowledged.")

    @app.post("/jobs/{job_id}/cancel")
    async def cancel(job_id: str, request: Request):
        r = engine.cancel(job_id)
        if _wants_json(request):
            return JSONResponse({"ok": r.ok, "message": r.message})
        return _html_control(request, toast=r.message if r.ok else "", error="" if r.ok else r.message)

    @app.post("/jobs/{job_id}/retry")
    async def retry(job_id: str, request: Request):
        r = engine.retry(job_id)
        if r.ok:
            engine.drain()
        if _wants_json(request):
            return JSONResponse(_json_safe({"ok": r.ok, "job": r.job, "message": r.message, "overlay": r.overlay}))
        if r.ok:
            return _html_control(request, toast=r.message or "Retry enqueued.")
        return _html_control(request, error=r.message, overlay=r.overlay)

    @app.post("/danger/delete-base")
    async def del_base(request: Request):
        try:
            body = await _body(request)
        except Exception as exc:
            if _wants_json(request):
                return JSONResponse({"ok": False, "message": str(exc)})
            return _html_control(request, error=str(exc), overlay="ov-delete")
        r = engine.delete_base(typed=(body.get("typed") or ""))
        if _wants_json(request):
            return JSONResponse({"ok": r.ok, "message": r.message})
        if r.ok:
            return _html_control(request, toast="Base deleted.")
        return _html_control(request, error=r.message or COPY["delete_base"], overlay="ov-delete")

    @app.post("/danger/delete-records")
    async def del_recs(request: Request):
        try:
            body = await _body(request)
        except Exception:
            body = {}
        confirmed = _truthy(body.get("confirm"))
        r = engine.delete_clean_records(confirm=confirmed)
        if _wants_json(request):
            return JSONResponse({"ok": r.ok, "message": r.message})
        if r.ok:
            return _html_control(request, toast="Clean records deleted.")
        return _html_control(request, overlay="ov-delete-records", error=r.message or COPY["delete_records"])

    @app.post("/vocab/topics")
    async def add_topic(request: Request):
        try:
            body = await _body(request)
        except Exception as exc:
            if _wants_json(request):
                return JSONResponse({"ok": False, "message": str(exc)})
            return _html_control(request, error=str(exc))
        if body.get("tag"):
            engine.add_topic(str(body.get("tag")))
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request, toast="Topic added.")

    @app.post("/vocab/topics/remove")
    async def remove_topic(request: Request):
        body = await _body(request)
        engine.remove_topic(str(body.get("tag") or ""))
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request)

    @app.post("/vocab/occasions")
    async def add_occ(request: Request):
        body = await _body(request)
        if body.get("tag"):
            engine.add_occasion(str(body.get("tag")))
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request, toast="Occasion added.")

    @app.post("/vocab/occasions/remove")
    async def remove_occ(request: Request):
        body = await _body(request)
        engine.remove_occasion(str(body.get("tag") or ""))
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request)

    @app.post("/vocab/allowlist")
    async def add_al(request: Request):
        body = await _body(request)
        engine.add_allowlist(str(body.get("outlet") or ""))
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request, toast="Outlet added.")

    @app.post("/vocab/allowlist/remove")
    async def remove_al(request: Request):
        body = await _body(request)
        engine.remove_allowlist(str(body.get("outlet") or ""))
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request)

    @app.post("/vocab/pins")
    async def save_pins(request: Request):
        body = await _body(request)
        if "x_personal" in body:
            engine.set_pin("x_personal", str(body.get("x_personal") or ""))
        if "truth_social" in body:
            engine.set_pin("truth_social", str(body.get("truth_social") or ""))
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request, toast="Pins saved.")

    @app.post("/sources/{source}/enabled")
    async def set_enabled(source: str, request: Request):
        body = await _body(request)
        enabled = _truthy(body.get("enabled"))
        engine.set_source_enabled(source, enabled)
        if _wants_json(request):
            return JSONResponse({"ok": True, "enabled": enabled})
        return _html_control(request)

    @app.post("/quarantine/{qid}/accept")
    def q_acc(qid: str):
        r = engine.accept_quarantine(qid, confirm=True)
        return JSONResponse({"ok": r.ok, "message": r.message})

    @app.post("/quarantine/{qid}/discard")
    def q_dis(qid: str):
        r = _eng().discard_quarantine(qid, confirm=True)
        return JSONResponse({"ok": r.ok, "message": r.message})

    @app.post("/worker/stop")
    async def worker_stop(request: Request):
        engine = _eng()
        try:
            body = await _body(request)
        except Exception:
            body = {}
        r = engine.stop_worker(confirm=_truthy(body.get("confirm")))
        if _wants_json(request):
            return JSONResponse({"ok": r.ok, "overlay": r.overlay, "message": r.message})
        if not r.ok:
            return _html_any(request, overlay="ov-worker-stop")
        return _html_any(request)

    @app.post("/worker/start")
    async def worker_start(request: Request):
        engine = _eng()
        engine.start_worker()
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_any(request)

    @app.post("/danger/restart")
    async def restart_app(request: Request):
        engine = _eng()
        try:
            body = await _body(request)
        except Exception:
            body = {}
        if not _truthy(body.get("confirm")):
            if _wants_json(request):
                return JSONResponse({"ok": False, "overlay": "ov-restart", "message": COPY["restart_app"]})
            return _html_control(request, overlay="ov-restart")
        engine.apply_restart_s5()
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request, toast="App restarted.")

    @app.post("/operator/records-reads")
    async def records_reads(request: Request):
        body = await _body(request)
        _eng().set_records_reads(body.get("value") or "available")
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request)

    @app.post("/operator/fail-next-load")
    async def fail_next_load(request: Request):
        body = await _body(request)
        _eng().set_fail_next_load(body.get("screen") or body.get("value"))
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request)

    @app.post("/load-retry")
    async def load_retry(request: Request):
        engine = _eng()
        screen = engine.load_error
        engine.clear_load_error()
        if _wants_json(request):
            return JSONResponse({"ok": True})
        if screen == "control":
            return HTMLResponse(render_control(engine, request))
        if screen == "records":
            return HTMLResponse(render_records(engine, request))
        if screen == "quarantine":
            return HTMLResponse(render_quarantine(engine, request))
        return HTMLResponse(render_dashboard(engine))

    @app.post("/operator/probe-clock")
    async def probe_clock(request: Request):
        body = await _body(request)
        _eng().set_probe_clock(body.get("value"))
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request)

    @app.post("/operator/probe-clock-clear")
    async def probe_clock_clear(request: Request):
        _eng().clear_probe_clock()
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request)

    @app.post("/sources/{source}/connector")
    async def set_connector(source: str, request: Request):
        body = await _body(request)
        _eng().set_connector(source, body.get("value") or "ok")
        if _wants_json(request):
            return JSONResponse({"ok": True})
        return _html_control(request)

    return app
