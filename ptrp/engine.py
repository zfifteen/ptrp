"""PTRP domain engine. Product behavior from Approved Spec v7."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from ptrp.constants import (
    CADENCE,
    COPY,
    COUNTED_CHANNELS,
    COVERING,
    EXPORT_FIELDS,
    FETCH_TYPES,
    GLOBAL_TYPES,
    JOB_TYPES,
    KINDS,
    LEGAL_PAIRS,
    SOURCES,
)

ET = ZoneInfo("America/New_York")
CLOCK_HOUR = 9
CLOCK_MINUTE = 0


def _now_factory():
    return datetime.now(timezone.utc)


def _iso(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _parse_dt(value):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    s = str(value)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        try:
            dt = datetime.strptime(s[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_et(dt):
    if dt is None:
        return "—"
    local = dt.astimezone(ET)
    return local.strftime("%a %b %d, %Y %H:%M").replace(" 0", " ") + " ET"


def term_for(dt):
    if dt is None:
        return None
    d = dt.astimezone(timezone.utc).date()
    if d < datetime(2017, 1, 20, tzinfo=timezone.utc).date():
        return "pre_2017"
    if d < datetime(2021, 1, 20, tzinfo=timezone.utc).date():
        return "2017_2021"
    if d < datetime(2025, 1, 20, tzinfo=timezone.utc).date():
        return "2021_2024"
    return "2025_present"


def _g(obj, name, default=None):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _sha(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def weekdays_between(start, end):
    d = start.astimezone(ET).date() + timedelta(days=1)
    last = end.astimezone(ET).date()
    n = 0
    while d <= last:
        if d.weekday() < 5:
            n += 1
        d += timedelta(days=1)
    return n


def next_weekday_0900(now_et, weekly):
    d = now_et.date()
    if weekly:
        monday = d - timedelta(days=now_et.weekday())
        cand = datetime(monday.year, monday.month, monday.day, CLOCK_HOUR, CLOCK_MINUTE, tzinfo=ET)
        if now_et < cand:
            return cand
        monday = monday + timedelta(days=7)
        return datetime(monday.year, monday.month, monday.day, CLOCK_HOUR, CLOCK_MINUTE, tzinfo=ET)
    if now_et.weekday() >= 5:
        days = 7 - now_et.weekday()
        d = d + timedelta(days=days)
        return datetime(d.year, d.month, d.day, CLOCK_HOUR, CLOCK_MINUTE, tzinfo=ET)
    cand = datetime(d.year, d.month, d.day, CLOCK_HOUR, CLOCK_MINUTE, tzinfo=ET)
    if now_et < cand:
        return cand
    d = d + timedelta(days=1)
    while d.weekday() >= 5:
        d = d + timedelta(days=1)
    return datetime(d.year, d.month, d.day, CLOCK_HOUR, CLOCK_MINUTE, tzinfo=ET)


@dataclass
class Result:
    ok: bool = False
    job: dict | None = None
    error: str | None = None
    overlay: str | None = None
    message: str = ""
    rejected: bool = False


class Engine:
    def __init__(self, db_path, fetch, clock=None):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.fetch = fetch
        self.clock = clock or _now_factory
        self.worker_available = True
        self.pause_execution = False
        self.interrupt_after = None
        self.cancel_after_clean = None
        self.fail_before_clean = False
        self.load_error = None
        self.read_down = False
        self.probe_clock = None
        self.connectors = {s: "ok" for s in SOURCES}
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._in_flight = {}
        self._working = set()

    def now(self):
        if self.probe_clock is not None:
            n = self.probe_clock
        else:
            n = self.clock()
        if n.tzinfo is None:
            n = n.replace(tzinfo=timezone.utc)
        return n.astimezone(timezone.utc)

    def boot(self):
        c = self.conn
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                enabled INTEGER NOT NULL DEFAULT 1,
                last_succeeded_at TEXT,
                last_succeeded_empty_at TEXT,
                last_error TEXT
            );
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                source TEXT NOT NULL,
                params TEXT,
                status TEXT NOT NULL,
                triggered_by TEXT NOT NULL,
                created TEXT NOT NULL,
                started TEXT,
                finished TEXT,
                fetched INTEGER DEFAULT 0,
                written INTEGER DEFAULT 0,
                updated INTEGER DEFAULT 0,
                unchanged INTEGER DEFAULT 0,
                quarantined INTEGER DEFAULT 0,
                fetch_fail INTEGER DEFAULT 0,
                error TEXT,
                waiting_reason TEXT,
                retry_of TEXT,
                retried_as TEXT,
                acknowledged INTEGER DEFAULT 0,
                log TEXT,
                in_flight TEXT
            );
            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                source TEXT,
                locator TEXT,
                retrieved_at TEXT,
                job_id TEXT,
                raw TEXT,
                content_hash TEXT,
                record_id TEXT
            );
            CREATE TABLE IF NOT EXISTS records (
                record_id TEXT PRIMARY KEY,
                locator TEXT,
                kind TEXT,
                title TEXT,
                event_time TEXT,
                published_time TEXT,
                text TEXT,
                text_version INTEGER,
                text_hash TEXT,
                completeness TEXT,
                url TEXT,
                source TEXT,
                occasion TEXT,
                audience TEXT,
                delivery TEXT,
                channel TEXT,
                topics TEXT,
                people TEXT,
                phrases TEXT,
                term TEXT,
                mention_usable INTEGER,
                decision_usable INTEGER,
                job_id TEXT,
                act_type TEXT,
                direction TEXT,
                decision_status TEXT,
                related TEXT,
                created_at TEXT,
                named_party TEXT
            );
            CREATE TABLE IF NOT EXISTS record_versions (
                record_id TEXT,
                text_version INTEGER,
                text TEXT,
                text_hash TEXT,
                job_id TEXT,
                created_at TEXT,
                PRIMARY KEY (record_id, text_version)
            );
            CREATE TABLE IF NOT EXISTS quarantine (
                id TEXT PRIMARY KEY,
                source TEXT,
                locator TEXT,
                reason TEXT,
                failed_rule TEXT,
                job_id TEXT,
                first_seen TEXT,
                open INTEGER DEFAULT 1,
                discarded INTEGER DEFAULT 0,
                fields TEXT,
                record_id TEXT,
                artifact_id TEXT
            );
            CREATE TABLE IF NOT EXISTS discarded (
                source TEXT,
                locator TEXT,
                content_hash TEXT,
                PRIMARY KEY (source, locator, content_hash)
            );
            CREATE TABLE IF NOT EXISTS topics (tag TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS occasions (tag TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS allowlist (outlet TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS pins (k TEXT PRIMARY KEY, v TEXT);
            CREATE TABLE IF NOT EXISTS preferences (topic TEXT PRIMARY KEY, payload TEXT);
            """
        )
        existing = {r["id"] for r in c.execute("SELECT id FROM sources")}
        if not existing:
            for s in SOURCES:
                c.execute("INSERT INTO sources (id, enabled) VALUES (?, 1)", (s,))
            c.execute("INSERT OR IGNORE INTO pins (k, v) VALUES ('x_personal', '')")
            c.execute("INSERT OR IGNORE INTO pins (k, v) VALUES ('truth_social', '')")
        cols = [r[1] for r in c.execute("PRAGMA table_info(records)")]
        if "named_party" not in cols:
            c.execute("ALTER TABLE records ADD COLUMN named_party TEXT")
        c.commit()
        self._demote_leftover_legal_missing_named_party()

    def _demote_leftover_legal_missing_named_party(self):
        """S12: leftover clean legal with empty or missing named_party is field-fail, not silent drop."""
        rows = self.conn.execute(
            """SELECT * FROM records
               WHERE kind = 'legal'
                 AND (named_party IS NULL OR TRIM(named_party) = '')"""
        ).fetchall()
        for r in rows:
            d = dict(r)
            locator = d.get("locator") or d["record_id"]
            item = {
                "locator": locator,
                "text": d.get("text") or "",
                "kind": d.get("kind"),
                "channel": d.get("channel"),
                "title": d.get("title") or "",
                "event_time": d.get("event_time"),
                "published_time": d.get("published_time"),
                "url": d.get("url") or "",
                "named_party": d.get("named_party"),
                "completeness": d.get("completeness"),
            }
            job = {"id": d.get("job_id") or "", "source": d.get("source") or "legal"}
            self._quarantine(job, item, "field-fail", "missing named_party (legal)")
            self.conn.execute("DELETE FROM records WHERE record_id=?", (d["record_id"],))
        if rows:
            self.conn.commit()

    def _job_row(self, job_id):
        r = self.conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(r) if r else None

    def get_job(self, job_id):
        j = self._job_row(job_id)
        if not j:
            raise KeyError(job_id)
        j["params"] = json.loads(j["params"] or "{}")
        j["log"] = json.loads(j["log"] or "[]")
        if isinstance(j.get("in_flight"), str):
            j["in_flight"] = json.loads(j["in_flight"] or "[]")
        return j

    def list_jobs(self, status=None, source=None, type=None, date_start=None, date_end=None):
        rows = self.conn.execute("SELECT * FROM jobs ORDER BY created").fetchall()
        out = []
        for r in rows:
            j = dict(r)
            j["params"] = json.loads(j["params"] or "{}")
            if status and status != "all" and j["status"] != status:
                continue
            if source and source != "all" and j["source"] != source:
                continue
            if type and type != "all" and j["type"] != type:
                continue
            created = _parse_dt(j.get("created"))
            if date_start:
                ds = _parse_dt(date_start)
                if ds and created and created < ds:
                    continue
            if date_end:
                de = _parse_dt(date_end)
                if de and created and created > de + timedelta(days=1):
                    continue
            out.append(j)
        return out

    def _save_job(self, j):
        existing = self._job_row(j["id"]) if j.get("id") else None
        if existing and existing["status"] in ("failed", "cancelled"):
            if j.get("status") in ("running", "succeeded", "succeeded_empty", "queued"):
                j = dict(j)
                j["status"] = existing["status"]
                j["error"] = existing.get("error")
                j["finished"] = existing.get("finished")
        params = j.get("params") if isinstance(j.get("params"), str) else json.dumps(j.get("params") or {})
        log = j.get("log") if isinstance(j.get("log"), str) else json.dumps(j.get("log") or [])
        inflight = j.get("in_flight") if isinstance(j.get("in_flight"), str) else json.dumps(j.get("in_flight") or [])
        self.conn.execute(
            """INSERT OR REPLACE INTO jobs
            (id,type,source,params,status,triggered_by,created,started,finished,
             fetched,written,updated,unchanged,quarantined,fetch_fail,error,
             waiting_reason,retry_of,retried_as,acknowledged,log,in_flight)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                j["id"], j["type"], j["source"], params, j["status"], j["triggered_by"],
                j["created"], j.get("started"), j.get("finished"),
                j.get("fetched", 0), j.get("written", 0), j.get("updated", 0),
                j.get("unchanged", 0), j.get("quarantined", 0), j.get("fetch_fail", 0),
                j.get("error"), j.get("waiting_reason"), j.get("retry_of"),
                j.get("retried_as"), int(j.get("acknowledged") or 0), log, inflight,
            ),
        )
        self.conn.commit()

    def sources_state(self):
        rows = self.conn.execute("SELECT * FROM sources").fetchall()
        return {r["id"]: {"enabled": bool(r["enabled"]), "id": r["id"]} for r in rows}

    def set_source_enabled(self, source, enabled):
        self.conn.execute("UPDATE sources SET enabled=? WHERE id=?", (1 if enabled else 0, source))
        self.conn.commit()

    def add_topic(self, tag):
        self.conn.execute("INSERT OR IGNORE INTO topics (tag) VALUES (?)", (tag,))
        self.conn.commit()

    def remove_topic(self, tag):
        self.conn.execute("DELETE FROM topics WHERE tag=?", (tag,))
        self.conn.commit()

    def list_topics(self):
        return [r["tag"] for r in self.conn.execute("SELECT tag FROM topics ORDER BY tag")]

    def add_occasion(self, tag):
        self.conn.execute("INSERT OR IGNORE INTO occasions (tag) VALUES (?)", (tag,))
        self.conn.commit()

    def remove_occasion(self, tag):
        self.conn.execute("DELETE FROM occasions WHERE tag=?", (tag,))
        self.conn.commit()

    def list_occasions(self):
        return [r["tag"] for r in self.conn.execute("SELECT tag FROM occasions ORDER BY tag")]

    def set_allowlist(self, outlets):
        self.conn.execute("DELETE FROM allowlist")
        for o in outlets:
            self.conn.execute("INSERT OR IGNORE INTO allowlist (outlet) VALUES (?)", (o,))
        self.conn.commit()

    def add_allowlist(self, outlet):
        if outlet:
            self.conn.execute("INSERT OR IGNORE INTO allowlist (outlet) VALUES (?)", (outlet,))
            self.conn.commit()

    def remove_allowlist(self, outlet):
        self.conn.execute("DELETE FROM allowlist WHERE outlet=?", (outlet,))
        self.conn.commit()

    def allowlist(self):
        return [r["outlet"] for r in self.conn.execute("SELECT outlet FROM allowlist")]

    def set_pin(self, source, value):
        key = "x_personal" if source in ("x_personal", "x") else "truth_social"
        self.conn.execute("INSERT OR REPLACE INTO pins (k, v) VALUES (?, ?)", (key, value or ""))
        self.conn.commit()

    def get_pin(self, source):
        key = "x_personal" if source in ("x_personal", "x") else "truth_social"
        r = self.conn.execute("SELECT v FROM pins WHERE k=?", (key,)).fetchone()
        return (r["v"] if r else "") or ""

    def debug_set_last_success(self, source, dt, fetched=1):
        iso = _iso(dt)
        if fetched > 0:
            self.conn.execute("UPDATE sources SET last_succeeded_at=? WHERE id=?", (iso, source))
        else:
            self.conn.execute("UPDATE sources SET last_succeeded_empty_at=? WHERE id=?", (iso, source))
        self.conn.commit()

    def next_scheduled_run(self, source):
        st = self.conn.execute("SELECT enabled FROM sources WHERE id=?", (source,)).fetchone()
        cad = CADENCE.get(source)
        if not st or not st["enabled"] or cad is None:
            return COPY["not_scheduled"]
        now_et = self.now().astimezone(ET)
        return next_weekday_0900(now_et, weekly=(cad == "weekly"))

    def _meta_get(self, k, default=None):
        r = self.conn.execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
        return r["v"] if r else default

    def _meta_set(self, k, v):
        self.conn.execute("INSERT OR REPLACE INTO meta (k, v) VALUES (?, ?)", (k, v))
        self.conn.commit()

    def set_connector(self, source, value):
        if value not in ("ok", "network", "auth", "parse"):
            value = "ok"
        self.connectors[source] = value

    def get_connector(self, source):
        return self.connectors.get(source, "ok")

    def set_records_reads(self, value):
        self.read_down = str(value).strip().lower() == "down"

    def set_fail_next_load(self, screen):
        name = str(screen or "").strip()
        key = name.lower()
        if key in ("dashboard", "control", "records", "quarantine"):
            self.load_error = key

    def clear_load_error(self):
        self.load_error = None

    def set_probe_clock(self, value):
        if value is None or value == "":
            self.probe_clock = None
            return
        if isinstance(value, datetime):
            dt = value
        else:
            s = str(value).strip()
            if s.endswith("Z"):
                s = s[:-1] + "+00:00"
            dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ET)
        else:
            dt = dt.astimezone(ET)
        self.probe_clock = dt
        self.scheduler_tick()

    def clear_probe_clock(self):
        self.probe_clock = None

    def scheduler_tick(self):
        now_et = self.now().astimezone(ET)
        if now_et.weekday() >= 5:
            return
        if now_et.hour != CLOCK_HOUR or now_et.minute != CLOCK_MINUTE:
            return
        tick_key = now_et.strftime("%Y-%m-%dT09:00")
        last = self._meta_get("last_schedule_tick")
        if last and last >= tick_key:
            return
        is_monday = now_et.weekday() == 0
        enqueued = 0
        due = 0
        for source in SOURCES:
            cad = CADENCE.get(source)
            if cad is None:
                continue
            st = self.conn.execute("SELECT enabled FROM sources WHERE id=?", (source,)).fetchone()
            if not st or not st["enabled"]:
                continue
            if cad == "weekly" and not is_monday:
                continue
            due += 1
            r = self.enqueue_job(
                type="incremental", source=source, triggered_by="schedule",
                confirm_disabled=True,
                dup_action="queue_behind",
            )
            if r.ok:
                enqueued += 1
        # Recording last_schedule_tick without enqueue is a fail when sources
        # were due. Occupied sources still get a queued incremental for this tick.
        if enqueued > 0 or due == 0:
            self._meta_set("last_schedule_tick", tick_key)

    def _touched(self, job_type, source):
        if job_type in GLOBAL_TYPES or source == "global":
            return list(SOURCES)
        if job_type == "re_extract" and source == "global":
            return list(SOURCES)
        return [source]

    def _occupants_for(self, sources, exclude_id=None):
        rows = self.conn.execute(
            "SELECT * FROM jobs WHERE status IN ('queued','running')"
        ).fetchall()
        out = []
        srcset = set(sources)
        for r in rows:
            j = dict(r)
            if exclude_id and j["id"] == exclude_id:
                continue
            touched = set(self._touched(j["type"], j["source"]))
            if touched & srcset:
                out.append(j)
        return out

    def _can_run(self, job):
        if not self.worker_available:
            return False
        others = self._occupants_for(self._touched(job["type"], job["source"]), exclude_id=job["id"])
        running = [o for o in others if o["status"] == "running"]
        earlier_q = [o for o in others if o["status"] == "queued" and o["created"] <= job["created"]]
        return not running and not earlier_q

    def enqueue_job(
        self,
        type,
        source=None,
        params=None,
        triggered_by="user",
        force_refetch=False,
        confirm_disabled=False,
        confirm_reindex=False,
        confirm_refresh=False,
        dup_action=None,
        retry_of=None,
    ):
        params = dict(params or {})
        if force_refetch:
            params["force_refetch"] = True
        job_type = type
        if job_type not in JOB_TYPES:
            return Result(ok=False, message="Unknown job type.")

        if job_type in GLOBAL_TYPES:
            source = "global"
        if job_type == "re_extract" and source is None:
            return Result(ok=False, message=COPY["pick_source"])

        targeted_mode = str(params.get("targeted_mode") or "query").strip() or "query"
        if job_type == "targeted" and targeted_mode == "operator_item":
            loc = str(params.get("locator") or "").strip()
            text = str(params.get("text") or "").strip()
            kind = str(params.get("kind") or "").strip()
            channel = str(params.get("channel") or "").strip()
            if not source or not loc or not text or not kind or not channel:
                return Result(ok=False, message=COPY["operator_item_need"])
            if source not in SOURCES:
                return Result(ok=False, message=f"Source is not on the configured list: {source}")
            needs_pin = (channel == "written_social") or (source in ("truth_social", "x_personal"))
            if needs_pin:
                if source in ("truth_social", "x_personal"):
                    pin = self.get_pin(source)
                else:
                    pin = self.get_pin("x_personal") or self.get_pin("truth_social")
                if not pin:
                    return Result(ok=False, message=COPY["operator_item_pin"])
        elif job_type in FETCH_TYPES:
            if not source:
                return Result(ok=False, message=COPY["src_required"])
            if source not in SOURCES:
                return Result(ok=False, message=f"Source is not on the configured list: {source}")
        if job_type == "re_extract" and source not in SOURCES + ["global"]:
            return Result(ok=False, message=COPY["pick_source"])

        if job_type == "backfill":
            ws = params.get("window_start")
            we = params.get("window_end")
            if not ws or not we:
                return Result(ok=False, message=COPY["backfill_window"])
            if str(ws) > str(we):
                return Result(ok=False, message=COPY["start_end"])
        if job_type == "targeted" and targeted_mode != "operator_item":
            if not (params.get("topic") or params.get("query") or params.get("occasion")):
                return Result(ok=False, message=COPY["targeted_need"])

        if job_type == "re_index" and not confirm_reindex:
            return Result(ok=False, overlay="ov-reindex", message=COPY["reindex_confirm"])
        if job_type == "refresh_preferences" and not confirm_refresh:
            return Result(ok=False, overlay="ov-refresh", message=COPY["refresh_confirm"])

        if source and source in SOURCES:
            st = self.conn.execute("SELECT enabled FROM sources WHERE id=?", (source,)).fetchone()
            if st and not st["enabled"] and not confirm_disabled and triggered_by == "user":
                return Result(ok=False, overlay="ov-disabled", message=COPY["disabled_confirm"])

        touched = self._touched(job_type, source or "global")
        occupants = self._occupants_for(touched)
        if occupants:
            by_src = {}
            for o in occupants:
                for s in self._touched(o["type"], o["source"]):
                    if s in touched:
                        by_src.setdefault(s, []).append(o)
            blocking = occupants[0]
            for s, jobs in by_src.items():
                uniq = {j["id"]: j for j in jobs}
                if len(uniq) >= 2:
                    run = [j for j in uniq.values() if j["status"] == "running"]
                    first = run[0] if run else sorted(uniq.values(), key=lambda x: x["created"])[0]
                    msg = COPY["third"].format(source=s, id=first["id"])
                    return Result(ok=False, rejected=True, message=msg, overlay=None)
            if dup_action == "dont_start":
                msg = COPY["dont_start"].format(id=blocking["id"])
                return Result(ok=False, rejected=True, message=msg)
            if dup_action != "queue_behind":
                return Result(ok=False, overlay="ov-dup", message=f"Write-scoped job {blocking['id']} occupies source.")
            waiting = COPY["waiting"].format(id=blocking["id"])
            toast = COPY["queue_behind"].format(id=blocking["id"])
            job = self._new_job(job_type, source, params, triggered_by, retry_of, waiting_reason=waiting)
            return Result(ok=True, job=job, message=toast)

        job = self._new_job(job_type, source, params, triggered_by, retry_of)
        return Result(ok=True, job=job)

    def _new_job(self, job_type, source, params, triggered_by, retry_of=None, waiting_reason=None):
        job = {
            "id": uuid.uuid4().hex[:12],
            "type": job_type,
            "source": source or "global",
            "params": params,
            "status": "queued",
            "triggered_by": triggered_by,
            "created": _iso(self.now()),
            "started": None,
            "finished": None,
            "fetched": 0, "written": 0, "updated": 0, "unchanged": 0,
            "quarantined": 0, "fetch_fail": 0,
            "error": None,
            "waiting_reason": waiting_reason,
            "retry_of": retry_of,
            "retried_as": None,
            "acknowledged": 0,
            "log": [f"queued type={job_type} source={source}"],
            "in_flight": [],
        }
        self._save_job(job)
        if retry_of:
            old = self.get_job(retry_of)
            old["retried_as"] = job["id"]
            self._save_job(old)
        return self.get_job(job["id"])

    def retry(self, job_id, dup_action=None):
        old = self.get_job(job_id)
        if old["status"] != "failed":
            return Result(ok=False, message="Retry is for failed jobs only.")
        return self.enqueue_job(
            type=old["type"],
            source=old["source"],
            params=old["params"],
            triggered_by="retry",
            force_refetch=bool((old["params"] or {}).get("force_refetch")),
            confirm_disabled=True,
            confirm_reindex=True,
            confirm_refresh=True,
            dup_action=dup_action,
            retry_of=job_id,
        )

    def ack(self, job_id):
        j = self.get_job(job_id)
        j["acknowledged"] = 1
        self._save_job(j)

    def set_worker_available(self, available):
        self.worker_available = available
        if not available:
            rows = self.conn.execute("SELECT id FROM jobs WHERE status='running'").fetchall()
            for r in rows:
                self._stop_job(r["id"], status="failed", error="worker_lost")

    def stop_worker(self, confirm=False):
        if not confirm:
            return Result(ok=False, overlay="ov-worker-stop", message=COPY["stop_worker"])
        self.set_worker_available(False)
        return Result(ok=True)

    def start_worker(self):
        self.set_worker_available(True)
        self.drain()
        return Result(ok=True)

    def apply_restart_s5(self):
        self.set_worker_available(False)
        self.worker_available = True

    def cancel(self, job_id, confirmed=True):
        j = self.get_job(job_id)
        if j["status"] not in ("queued", "running"):
            return Result(ok=False, message="Cancel is disabled on terminal statuses.")
        if j["status"] == "queued":
            j["status"] = "cancelled"
            j["finished"] = _iso(self.now())
            self._save_job(j)
            return Result(ok=True, job=self.get_job(job_id), message=COPY["cancel_toast"])
        self._stop_job(job_id, status="cancelled", error=None)
        return Result(ok=True, job=self.get_job(job_id), message=COPY["cancel_toast"])

    def drain(self):
        if not self.worker_available:
            return
        if not self.pause_execution:
            for r in list(self.conn.execute("SELECT id FROM jobs WHERE status='running'").fetchall()):
                self._work(r["id"])
        while self.worker_available:
            queued = self.conn.execute(
                "SELECT * FROM jobs WHERE status='queued' ORDER BY created"
            ).fetchall()
            claimed = None
            for r in queued:
                j = dict(r)
                if self._can_run(j):
                    claimed = j
                    break
            if not claimed:
                break
            claimed["status"] = "running"
            claimed["started"] = _iso(self.now())
            claimed["waiting_reason"] = None
            log = json.loads(claimed.get("log") or "[]")
            log.append("running")
            claimed["log"] = log
            claimed["params"] = json.loads(claimed["params"] or "{}")
            self._save_job(claimed)
            if self.pause_execution:
                if self.interrupt_after or self.cancel_after_clean or self.fail_before_clean:
                    self._work(claimed["id"], stay_running=True)
                break
            self._work(claimed["id"])

    def _item_to_dict(self, item):
        def g(n, d=None):
            return _g(item, n, d)
        etime = g("event_time")
        ptime = g("published_time")
        return {
            "locator": g("locator"),
            "text": g("text") or "",
            "kind": g("kind"),
            "channel": g("channel"),
            "title": g("title") or "",
            "event_time": _iso(_parse_dt(etime)) if etime else None,
            "published_time": _iso(_parse_dt(ptime)) if ptime else None,
            "url": g("url") or "",
            "attributed": bool(g("attributed", True)),
            "completeness": g("completeness") or "full_transcript",
            "outlet": g("outlet"),
            "author_handle": g("author_handle"),
            "named_party": g("named_party"),
            "topics": list(g("topics") or []),
            "occasion": g("occasion"),
            "act_type": g("act_type"),
            "direction": g("direction"),
            "status": g("status"),
            "related_remarks": list(g("related_remarks") or []),
            "people": list(g("people") or []),
            "phrases": list(g("phrases") or []),
            "audience": g("audience"),
            "delivery": g("delivery"),
            "term": g("term"),
            "fetch_failed": bool(g("fetch_failed", False)),
            "fetch_error": g("fetch_error"),
        }

    def _operator_item_from_params(self, source, params):
        pin_match = str(params.get("pin_match") or "match").strip() or "match"
        handle = params.get("author_handle")
        if source in ("truth_social", "x_personal"):
            pin = self.get_pin(source)
            if pin_match == "lookalike":
                handle = handle or ((pin + "Fan") if pin else "lookalike")
                if pin and handle.lower().lstrip("@") == pin.lower().lstrip("@"):
                    handle = pin + "Fan"
            else:
                handle = handle or pin
        topics = params.get("topics") or []
        if isinstance(topics, str):
            topics = [x for x in topics.split(",") if x.strip()]
        return {
            "locator": params.get("locator"),
            "text": params.get("text") or "",
            "kind": params.get("kind"),
            "channel": params.get("channel"),
            "title": params.get("title") or "",
            "event_time": params.get("event_time"),
            "published_time": params.get("published_time"),
            "url": params.get("url") or "",
            "attributed": True if params.get("attributed") is None else bool(params.get("attributed")),
            "completeness": params.get("completeness") or "full_transcript",
            "outlet": params.get("outlet"),
            "author_handle": handle,
            "named_party": params.get("named_party"),
            "topics": topics,
            "occasion": params.get("item_occasion") or None,
            "act_type": params.get("act_type"),
            "direction": params.get("direction"),
            "status": params.get("status"),
            "related_remarks": list(params.get("related_remarks") or []),
            "people": list(params.get("people") or []),
            "phrases": list(params.get("phrases") or []),
            "audience": params.get("audience"),
            "delivery": params.get("delivery"),
            "term": params.get("term"),
        }

    def _locator_is_clean(self, locator):
        if not locator:
            return False
        r = self.conn.execute("SELECT 1 FROM records WHERE record_id=?", (locator,)).fetchone()
        return bool(r)

    def _locator_written_clean_by_job(self, locator, job_id):
        if not locator or not job_id:
            return False
        r = self.conn.execute(
            "SELECT 1 FROM records WHERE record_id=? AND job_id=?",
            (locator, job_id),
        ).fetchone()
        return bool(r)

    def _worker_down_or_job_not_running(self, job_id):
        if not self.worker_available:
            return True
        row = self._job_row(job_id)
        return not row or row["status"] != "running"

    def _s6_quarantine_remaining(self, j, remaining):
        already = {
            r["locator"]
            for r in self.conn.execute(
                "SELECT locator FROM quarantine WHERE job_id=? AND failed_rule='job_stopped' AND open=1",
                (j["id"],),
            ).fetchall()
        }
        for it in remaining or []:
            if not isinstance(it, dict):
                continue
            if it.get("fetch_failed"):
                j["fetch_fail"] = j.get("fetch_fail", 0) + 1
                continue
            loc = it.get("locator")
            if loc and (loc in already or self._locator_written_clean_by_job(loc, j["id"])):
                continue
            self._quarantine(j, it, "field-fail", "job_stopped")
            j["quarantined"] = j.get("quarantined", 0) + 1
            if loc:
                already.add(loc)

    def _abort_stopped_work(self, job_id, remaining, fetched=None):
        if not self._worker_down_or_job_not_running(job_id):
            return False
        latest = self.get_job(job_id)
        # S6 is for failed/cancelled/worker_lost only. Overlapping _work after
        # succeed must not job_stopped locators already counted as unchanged.
        if latest["status"] in ("succeeded", "succeeded_empty"):
            self._in_flight.pop(job_id, None)
            return True
        if fetched is not None:
            latest["fetched"] = fetched
        self._s6_quarantine_remaining(latest, remaining)
        latest["in_flight"] = []
        if latest["status"] == "running":
            latest["status"] = "failed"
            latest["error"] = "worker_lost"
            latest["finished"] = _iso(self.now())
            latest["log"] = (latest.get("log") or []) + ["failed worker_lost"]
        self._in_flight.pop(job_id, None)
        self._save_job(latest)
        return True

    def _work(self, job_id, stay_running=False):
        if job_id in self._working:
            return
        self._working.add(job_id)
        try:
            self._execute_job(job_id, stay_running=stay_running)
        finally:
            self._working.discard(job_id)

    def _execute_job(self, job_id, stay_running=False):
        j = self.get_job(job_id)
        if j["status"] != "running":
            return
        jtype = j["type"]
        source = j["source"]
        params = j["params"] or {}
        if jtype == "re_index":
            self._finish(j, "succeeded")
            return
        if jtype == "refresh_preferences":
            self._rebuild_preferences()
            self._finish(j, "succeeded")
            return
        if jtype == "re_extract":
            self._finish(j, "succeeded")
            return
        if jtype in FETCH_TYPES and source in SOURCES:
            conn_err = self.get_connector(source)
            if conn_err != "ok":
                self._stop_job(job_id, status="failed", error=conn_err)
                self.conn.execute("UPDATE sources SET last_error=? WHERE id=?", (conn_err, source))
                self.conn.commit()
                return

        if jtype == "targeted" and str((params or {}).get("targeted_mode") or "") == "operator_item":
            raw_items = [self._operator_item_from_params(source, params)]
        else:
            try:
                raw_items = self.fetch.fetch(source, jtype, params)
            except Exception as exc:
                if self._abort_stopped_work(job_id, []):
                    return
                msg = getattr(exc, "message", None) or str(exc)
                self._stop_job(job_id, status="failed", error=msg)
                if source in SOURCES:
                    self.conn.execute("UPDATE sources SET last_error=? WHERE id=?", (msg, source))
                    self.conn.commit()
                return

        items = [self._item_to_dict(x) for x in (raw_items or [])]
        self._in_flight[job_id] = list(items)
        if self._abort_stopped_work(job_id, items, fetched=len(items)):
            return
        j = self.get_job(job_id)
        j["fetched"] = len(items)
        force = bool(params.get("force_refetch"))
        j["in_flight"] = items
        j["log"] = (j.get("log") or []) + [f"fetched {len(items)}"]
        self._save_job(j)

        if self.fail_before_clean:
            for it in items:
                self._quarantine(j, it, "field-fail", "job_stopped")
                j["quarantined"] = j.get("quarantined", 0) + 1
            self._finish(j, "failed", error="job_stopped")
            return

        remaining = []
        process_cap = self.interrupt_after if stay_running else None
        stop_after_clean = None if stay_running else self.cancel_after_clean
        todo = list(items)

        while todo:
            self._in_flight[job_id] = list(todo)
            j["in_flight"] = list(todo)
            self._save_job(j)
            if self._abort_stopped_work(job_id, todo, fetched=len(items)):
                return
            it = todo[0]
            if it.get("fetch_failed"):
                j["fetch_fail"] = j.get("fetch_fail", 0) + 1
                todo.pop(0)
                continue
            written_clean = j.get("written", 0) + j.get("updated", 0)
            if process_cap is not None and written_clean >= process_cap:
                remaining.extend(todo)
                break
            if stop_after_clean is not None and written_clean >= stop_after_clean:
                remaining.extend(todo)
                break
            todo.pop(0)
            self._in_flight[job_id] = [it] + list(todo)
            self._store_artifact(j, it)
            accounted = (
                j.get("written", 0)
                + j.get("updated", 0)
                + j.get("unchanged", 0)
                + j.get("quarantined", 0)
                + j.get("fetch_fail", 0)
            )
            self._process_item(j, it, force)
            accounted_after = (
                j.get("written", 0)
                + j.get("updated", 0)
                + j.get("unchanged", 0)
                + j.get("quarantined", 0)
                + j.get("fetch_fail", 0)
            )
            leftover = []
            if self._worker_down_or_job_not_running(job_id):
                handled = accounted_after > accounted or self._locator_written_clean_by_job(
                    it.get("locator"), job_id
                )
                if not handled:
                    leftover.append(it)
                leftover.extend(todo)
                if self._abort_stopped_work(job_id, leftover, fetched=len(items)):
                    return
            self._in_flight[job_id] = list(todo)
            j["in_flight"] = list(todo)
            self._save_job(j)

        j["in_flight"] = remaining
        self._in_flight[job_id] = list(remaining)
        self._save_job(j)
        if self._abort_stopped_work(job_id, remaining, fetched=len(items)):
            return

        if stay_running:
            return
        if remaining:
            for it in remaining:
                self._quarantine(j, it, "field-fail", "job_stopped")
                j["quarantined"] = j.get("quarantined", 0) + 1
            self._finish(j, "cancelled")
            return
        if j["fetched"] == 0:
            self._finish(j, "succeeded_empty")
            if source in SOURCES:
                self.conn.execute(
                    "UPDATE sources SET last_succeeded_empty_at=?, last_error=NULL WHERE id=?",
                    (_iso(self.now()), source),
                )
                self.conn.commit()
            return
        self._finish(j, "succeeded")
        if source in SOURCES and j["fetched"] > 0 and not self._blocked(source):
            self.conn.execute(
                "UPDATE sources SET last_succeeded_at=?, last_error=NULL WHERE id=?",
                (_iso(self.now()), source),
            )
            self.conn.commit()

    def _finish(self, j, status, error=None):
        latest = self._job_row(j["id"]) if j.get("id") else None
        if latest and latest["status"] in ("failed", "cancelled") and status in (
            "succeeded",
            "succeeded_empty",
            "running",
        ):
            keep = dict(j)
            keep["status"] = latest["status"]
            keep["error"] = latest.get("error")
            keep["finished"] = latest.get("finished")
            keep["in_flight"] = []
            self._save_job(keep)
            self._in_flight.pop(j["id"], None)
            return
        if status == "running":
            j["status"] = "running"
            self._save_job(j)
            return
        j["status"] = status
        j["finished"] = _iso(self.now())
        if error:
            j["error"] = error
        if status in ("succeeded", "succeeded_empty"):
            j["error"] = None
        j["in_flight"] = []
        self._save_job(j)
        self._in_flight.pop(j.get("id"), None)

    def _stop_job(self, job_id, status, error):
        j = self.get_job(job_id)
        inflight = self._in_flight.get(job_id)
        if inflight is None:
            inflight = j.get("in_flight") or []
        if isinstance(inflight, str):
            inflight = json.loads(inflight or "[]")
        self._s6_quarantine_remaining(j, inflight)
        j["status"] = status
        j["error"] = error
        j["finished"] = _iso(self.now())
        j["in_flight"] = []
        j["log"] = (j.get("log") or []) + [f"{status} {error or ''}"]
        self._in_flight.pop(job_id, None)
        self._save_job(j)

    def _store_artifact(self, j, it):
        aid = uuid.uuid4().hex[:12]
        self.conn.execute(
            """INSERT INTO artifacts (id,source,locator,retrieved_at,job_id,raw,content_hash,record_id)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                aid, j["source"], it["locator"], _iso(self.now()), j["id"],
                it.get("text") or "", _sha(it.get("text") or ""), it["locator"],
            ),
        )
        self.conn.commit()
        it["_artifact_id"] = aid

    def _discarded(self, source, locator, chash):
        r = self.conn.execute(
            "SELECT 1 FROM discarded WHERE source=? AND locator=? AND content_hash=?",
            (source, locator, chash),
        ).fetchone()
        return bool(r)

    def _process_item(self, j, it, force):
        if self._worker_down_or_job_not_running(j["id"]):
            return
        source = j["source"]
        locator = it["locator"]
        chash = _sha(it.get("text") or "")
        if not force and self._discarded(source, locator, chash):
            return
        gate = self._gate(it, source)
        if not gate["ok"]:
            self._quarantine(j, it, gate["reason"], gate["rule"])
            j["quarantined"] = j.get("quarantined", 0) + 1
            return
        record_id = locator
        existing = self.conn.execute("SELECT * FROM records WHERE record_id=?", (record_id,)).fetchone()
        rec = self._record_from_item(it, source, j["id"], record_id)
        if existing:
            if existing["text_hash"] == rec["text_hash"] and not force:
                j["unchanged"] = j.get("unchanged", 0) + 1
            else:
                prev = existing["text_version"]
                try:
                    prev_n = int(prev) if prev is not None and str(prev).strip() != "" else 0
                except (TypeError, ValueError):
                    prev_n = 0
                if prev_n < 1:
                    stored = self.conn.execute(
                        "SELECT 1 FROM record_versions WHERE record_id=? AND text_version=1",
                        (record_id,),
                    ).fetchone()
                    if not stored:
                        self._save_version({
                            "record_id": record_id,
                            "text_version": 1,
                            "text": existing["text"],
                            "text_hash": existing["text_hash"],
                            "job_id": existing["job_id"],
                            "created_at": existing["created_at"] or rec["created_at"],
                        })
                    prev_n = 1
                rec["text_version"] = prev_n + 1
                self._upsert_record(rec)
                self._save_version(rec)
                j["updated"] = j.get("updated", 0) + 1
        else:
            rec["text_version"] = 1
            self._upsert_record(rec)
            self._save_version(rec)
            j["written"] = j.get("written", 0) + 1
        self.conn.execute(
            "UPDATE quarantine SET open=0 WHERE source=? AND locator=? AND open=1",
            (source, locator),
        )
        self.conn.commit()
        self._save_job(j)

    def _record_from_item(self, it, source, job_id, record_id):
        channel = it["channel"]
        kind = it["kind"]
        mention = True
        if source == "books" or channel not in ("spoken", "written_social"):
            mention = False
        if it.get("completeness") == "paraphrase":
            mention = False
        decision_u = kind == "decision" and bool(it.get("act_type")) and bool(it.get("direction"))
        dt = _parse_dt(it.get("event_time")) or _parse_dt(it.get("published_time"))
        return {
            "record_id": record_id,
            "locator": it["locator"],
            "kind": kind,
            "title": it.get("title") or "",
            "event_time": it.get("event_time"),
            "published_time": it.get("published_time"),
            "text": it.get("text") or "",
            "text_version": 1,
            "text_hash": _sha(it.get("text") or ""),
            "completeness": it.get("completeness") or "full_transcript",
            "url": it.get("url") or "",
            "source": source,
            "occasion": it.get("occasion"),
            "audience": it.get("audience"),
            "delivery": it.get("delivery"),
            "channel": channel,
            "topics": json.dumps(it.get("topics") or []),
            "people": json.dumps(it.get("people") or []),
            "phrases": json.dumps(it.get("phrases") or []),
            "term": it.get("term") or term_for(dt),
            "mention_usable": 1 if mention else 0,
            "decision_usable": 1 if decision_u else 0,
            "job_id": job_id,
            "act_type": it.get("act_type"),
            "direction": it.get("direction"),
            "decision_status": it.get("status"),
            "related": json.dumps(it.get("related_remarks") or []),
            "created_at": _iso(self.now()),
            "named_party": (it.get("named_party") or "") if (kind == "legal") else (it.get("named_party") or ""),
        }

    def _upsert_record(self, rec):
        self.conn.execute(
            """INSERT OR REPLACE INTO records
            (record_id,locator,kind,title,event_time,published_time,text,text_version,text_hash,
             completeness,url,source,occasion,audience,delivery,channel,topics,people,phrases,term,
             mention_usable,decision_usable,job_id,act_type,direction,decision_status,related,created_at,named_party)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                rec["record_id"], rec["locator"], rec["kind"], rec["title"], rec["event_time"],
                rec["published_time"], rec["text"], rec["text_version"], rec["text_hash"],
                rec["completeness"], rec["url"], rec["source"], rec["occasion"], rec["audience"],
                rec["delivery"], rec["channel"], rec["topics"], rec["people"], rec["phrases"], rec["term"],
                rec["mention_usable"], rec["decision_usable"], rec["job_id"], rec["act_type"],
                rec["direction"], rec["decision_status"], rec["related"], rec["created_at"],
                rec.get("named_party") or "",
            ),
        )
        self.conn.commit()

    def _save_version(self, rec):
        self.conn.execute(
            """INSERT OR REPLACE INTO record_versions
               (record_id,text_version,text,text_hash,job_id,created_at) VALUES (?,?,?,?,?,?)""",
            (rec["record_id"], rec["text_version"], rec["text"], rec["text_hash"], rec["job_id"], rec["created_at"]),
        )
        self.conn.commit()

    def _gate(self, it, source, field_only=False):
        kind, channel = it.get("kind"), it.get("channel")
        pairs = LEGAL_PAIRS.get(source, set())
        if (kind, channel) not in pairs:
            return {"ok": False, "reason": "field-fail", "rule": "illegal_pair"}
        if source == "legal" or kind == "legal":
            raw_party = it.get("named_party")
            if raw_party is None or str(raw_party).strip() == "":
                return {"ok": False, "reason": "field-fail", "rule": "missing named_party (legal)"}
            party = str(raw_party).strip()
            if party == "the administration":
                return {"ok": False, "reason": "field-fail", "rule": "named_party"}
            if party != "Donald Trump":
                return {"ok": False, "reason": "field-fail", "rule": "named_party"}
        if not it.get("attributed", True):
            return {"ok": False, "reason": "field-fail", "rule": "attribution"}
        if not (it.get("text") or "").strip():
            return {"ok": False, "reason": "field-fail", "rule": "text"}
        if not it.get("locator"):
            return {"ok": False, "reason": "field-fail", "rule": "locator"}
        if (channel == "spoken" or kind in ("decision", "staffing")) and not it.get("event_time"):
            return {"ok": False, "reason": "field-fail", "rule": "event_time"}
        if channel == "written_social" and not it.get("published_time"):
            return {"ok": False, "reason": "field-fail", "rule": "published_time"}
        if source in ("x_personal", "truth_social"):
            pin = self.get_pin(source)
            if not pin:
                return {"ok": False, "reason": "field-fail", "rule": "pin_required"}
            handle = (it.get("author_handle") or "").lstrip("@")
            if handle.lower() != pin.lower().lstrip("@"):
                return {"ok": False, "reason": "field-fail", "rule": "pin_mismatch"}
        if source == "interviews":
            al = [x.lower() for x in self.allowlist()]
            if not al:
                return {"ok": False, "reason": "field-fail", "rule": "empty_allowlist"}
            outlet = (it.get("outlet") or "").lower()
            if outlet not in al and not field_only:
                return {"ok": False, "reason": "operator-hold", "rule": "outlet_not_allowlisted"}
        vocab_t = set(self.list_topics())
        for t in it.get("topics") or []:
            if t not in vocab_t:
                return {"ok": False, "reason": "field-fail", "rule": "unknown_topic"}
        occ = it.get("occasion")
        if occ and occ not in set(self.list_occasions()):
            return {"ok": False, "reason": "field-fail", "rule": "unknown_occasion"}
        return {"ok": True, "reason": None, "rule": None}

    def _quarantine(self, j, it, reason, rule):
        qid = uuid.uuid4().hex[:12]
        self.conn.execute(
            """INSERT INTO quarantine
               (id,source,locator,reason,failed_rule,job_id,first_seen,open,discarded,fields,record_id,artifact_id)
               VALUES (?,?,?,?,?,?,?,1,0,?,?,?)""",
            (
                qid, j["source"], it.get("locator"), reason, rule, j["id"], _iso(self.now()),
                json.dumps(it), it.get("locator"), it.get("_artifact_id"),
            ),
        )
        self.conn.commit()

    def list_quarantine(self):
        rows = self.conn.execute("SELECT * FROM quarantine ORDER BY first_seen").fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["open"] = bool(d["open"])
            d["discarded"] = bool(d["discarded"])
            out.append(d)
        return out

    def get_quarantine(self, qid):
        r = self.conn.execute("SELECT * FROM quarantine WHERE id=?", (qid,)).fetchone()
        return dict(r) if r else {}

    def accept_quarantine(self, qid, confirm=False):
        q = self.get_quarantine(qid)
        if not q or not q.get("open"):
            return Result(ok=False, message="Not found.")
        if q["reason"] == "field-fail" or q["failed_rule"] == "job_stopped":
            return Result(ok=False, message=COPY["accept_fieldfail"])
        if q["reason"] != "operator-hold":
            return Result(ok=False, message=COPY["accept_fieldfail"])
        if not confirm:
            return Result(ok=False, overlay="ov-q-hold", message="Promote this item to clean? Fields will not be edited.")
        fields = json.loads(q["fields"] or "{}")
        gate = self._gate(fields, q["source"], field_only=True)
        if not gate["ok"]:
            return Result(ok=False, message=f"Accept refused: still fails {gate['rule']}.")
        rec = self._record_from_item(fields, q["source"], q["job_id"], fields.get("locator"))
        rec["text_version"] = 1
        self._upsert_record(rec)
        self._save_version(rec)
        self.conn.execute("UPDATE quarantine SET open=0 WHERE id=?", (qid,))
        self.conn.commit()
        return Result(ok=True)

    def discard_quarantine(self, qid, confirm=False):
        q = self.get_quarantine(qid)
        if not q:
            return Result(ok=False)
        fields = json.loads(q.get("fields") or "{}")
        chash = _sha(fields.get("text") or "")
        self.conn.execute(
            "INSERT OR IGNORE INTO discarded (source,locator,content_hash) VALUES (?,?,?)",
            (q["source"], q["locator"], chash),
        )
        self.conn.execute("UPDATE quarantine SET open=0, discarded=1 WHERE id=?", (qid,))
        self.conn.commit()
        return Result(ok=True, message=COPY["discard_helper"])

    def _row_record(self, r, version_override=None):
        d = dict(r)
        d["topics"] = json.loads(d["topics"] or "[]")
        d["people"] = json.loads(d["people"] or "[]")
        d["phrases"] = json.loads(d["phrases"] or "[]")
        d["mention_usable"] = bool(d["mention_usable"])
        d["decision_usable"] = bool(d["decision_usable"])
        d["related"] = json.loads(d.get("related") or "[]")
        d["named_party"] = d.get("named_party") or ""
        if version_override:
            d["text"] = version_override["text"]
            d["text_hash"] = version_override["text_hash"]
            d["text_version"] = version_override["text_version"]
        return d

    def search(self, **filters):
        if self.read_down:
            return []
        sql = "SELECT * FROM records WHERE 1=1"
        args = []
        if filters.get("source"):
            sql += " AND source=?"
            args.append(filters["source"])
        if filters.get("kind"):
            sql += " AND kind=?"
            args.append(filters["kind"])
        if filters.get("channel"):
            sql += " AND channel=?"
            args.append(filters["channel"])
        if filters.get("topic"):
            sql += " AND topics LIKE ?"
            args.append('%"' + filters["topic"] + '"%')
        if filters.get("occasion"):
            sql += " AND occasion=?"
            args.append(filters["occasion"])
        if filters.get("event_start"):
            sql += " AND event_time>=?"
            args.append(str(filters["event_start"]))
        if filters.get("event_end"):
            sql += " AND event_time<=?"
            args.append(str(filters["event_end"]) + "T23:59:59")
        if filters.get("pub_start") or filters.get("published_start"):
            sql += " AND published_time>=?"
            args.append(str(filters.get("pub_start") or filters.get("published_start")))
        if filters.get("pub_end") or filters.get("published_end"):
            sql += " AND published_time<=?"
            args.append(str(filters.get("pub_end") or filters.get("published_end")) + "T23:59:59")
        if filters.get("term"):
            sql += " AND term=?"
            args.append(filters["term"])
        if filters.get("mention_usable") is True:
            sql += " AND mention_usable=1"
        if filters.get("mention_usable") is False:
            sql += " AND mention_usable=0"
        if filters.get("decision_usable") is True:
            sql += " AND decision_usable=1"
        rows = [self._row_record(r) for r in self.conn.execute(sql, args).fetchall()]
        q = filters.get("query") or filters.get("q") or filters.get("search")
        if q:
            q = str(q)
            if q.startswith('"') and q.endswith('"'):
                needle = q[1:-1]
                rows = [r for r in rows if needle in r["text"]]
            else:
                rows = [r for r in rows if q.lower() in (r["text"] or "").lower() or q.lower() in (r["title"] or "").lower()]
        return rows

    def get_record(self, record_id, text_version=None):
        if self.read_down:
            return None
        r = self.conn.execute("SELECT * FROM records WHERE record_id=?", (record_id,)).fetchone()
        if not r:
            return None
        if text_version is not None:
            v = self.conn.execute(
                "SELECT * FROM record_versions WHERE record_id=? AND text_version=?",
                (record_id, text_version),
            ).fetchone()
            if not v:
                return None
            return self._row_record(r, dict(v))
        return self._row_record(r)

    def export_retrieval_set(self, **filters):
        rows = self.search(**filters)
        out = []
        for r in rows:
            item = {}
            for k in EXPORT_FIELDS:
                val = r.get(k)
                if k in ("event_time", "published_time") and val:
                    dt = _parse_dt(val)
                    val = dt.isoformat() if dt else val
                if k == "named_party":
                    val = val or ""
                    if r.get("kind") != "legal":
                        val = val or ""
                item[k] = val
            out.append(item)
        return out

    def list_artifacts(self, record_id=None, job_id=None):
        if record_id:
            rows = self.conn.execute("SELECT * FROM artifacts WHERE record_id=?", (record_id,)).fetchall()
        elif job_id:
            rows = self.conn.execute("SELECT * FROM artifacts WHERE job_id=?", (job_id,)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM artifacts").fetchall()
        return [dict(r) for r in rows]

    def records_for_job(self, job_id):
        rows = self.conn.execute("SELECT * FROM records WHERE job_id=?", (job_id,)).fetchall()
        return [self._row_record(r) for r in rows]

    def quarantine_for_job(self, job_id):
        rows = self.conn.execute("SELECT * FROM quarantine WHERE job_id=?", (job_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_preference(self, topic):
        if self.read_down:
            return None
        r = self.conn.execute("SELECT payload FROM preferences WHERE topic=?", (topic,)).fetchone()
        if not r:
            self._rebuild_preferences()
            r = self.conn.execute("SELECT payload FROM preferences WHERE topic=?", (topic,)).fetchone()
        if not r:
            return {"topic": topic, "supporting": [], "contradicting": [], "consistency": None, "terms": []}
        return json.loads(r["payload"])

    def _rebuild_preferences(self):
        self.conn.execute("DELETE FROM preferences")
        for topic in self.list_topics():
            recs = self.search(topic=topic)
            independent = []
            seen = set()
            for r in recs:
                key = (r.get("event_time"), r.get("occasion"))
                if key in seen and r["kind"] != "decision":
                    continue
                seen.add(key)
                independent.append(r)
            if len(independent) < 2:
                decisions = [r for r in recs if r["kind"] == "decision"]
                remarks = [r for r in recs if r["kind"] == "remark"]
                if decisions and remarks:
                    independent = [decisions[0], remarks[0]]
                else:
                    continue
            payload = {
                "topic": topic,
                "supporting": [r["record_id"] for r in independent],
                "contradicting": [],
                "consistency": "consistent",
                "terms": sorted({r.get("term") for r in independent if r.get("term")}),
            }
            self.conn.execute(
                "INSERT OR REPLACE INTO preferences (topic, payload) VALUES (?, ?)",
                (topic, json.dumps(payload)),
            )
        self.conn.commit()

    def delete_base(self, typed=""):
        if typed != "DELETE":
            return Result(ok=False, overlay="ov-delete", message=COPY["delete_base"])
        self.conn.execute("DELETE FROM records")
        self.conn.execute("DELETE FROM record_versions")
        self.conn.execute("DELETE FROM preferences")
        self.conn.commit()
        return Result(ok=True)

    def delete_clean_records(self, confirm=False):
        if not confirm:
            return Result(ok=False, message="Confirm required to delete clean records.")
        self.conn.execute("DELETE FROM records")
        self.conn.execute("DELETE FROM record_versions")
        self.conn.commit()
        return Result(ok=True)

    def _blocked(self, source):
        if source == "interviews" and not self.allowlist():
            return COPY["blocked_allowlist"]
        if source in ("x_personal", "truth_social") and not self.get_pin(source):
            return COPY["blocked_pin"]
        return None

    def _cadence_stale(self, source):
        cad = CADENCE.get(source)
        if cad is None:
            return False
        row = self.conn.execute("SELECT last_succeeded_at FROM sources WHERE id=?", (source,)).fetchone()
        last = _parse_dt(row["last_succeeded_at"] if row else None)
        if last is None:
            return True
        now = self.now()
        if cad == "daily":
            return weekdays_between(last, now) > 1
        if cad == "weekly":
            return (now - last) > timedelta(days=8)
        return False

    def _stale_24h(self, source):
        if CADENCE.get(source) is None:
            return False
        row = self.conn.execute("SELECT last_succeeded_at FROM sources WHERE id=?", (source,)).fetchone()
        last = _parse_dt(row["last_succeeded_at"] if row else None)
        if last is None:
            return True
        return (self.now() - last) > timedelta(hours=24)

    def source_health(self):
        out = {}
        for s in SOURCES:
            row = self.conn.execute("SELECT * FROM sources WHERE id=?", (s,)).fetchone()
            last = _parse_dt(row["last_succeeded_at"]) if row else None
            last_empty = _parse_dt(row["last_succeeded_empty_at"]) if row else None
            count = self.conn.execute("SELECT COUNT(*) n FROM records WHERE source=?", (s,)).fetchone()["n"]
            cad = CADENCE.get(s)
            if cad is None:
                cadence_age = None
                age_24h = None
            elif last is None:
                cadence_age = "never succeeded"
                age_24h = "never succeeded"
            else:
                now = self.now()
                if cad == "daily":
                    n = weekdays_between(last, now)
                    cadence_age = f"{n} weekday" + ("" if n == 1 else "s")
                else:
                    n = (now - last).days
                    cadence_age = f"{n} day" + ("" if n == 1 else "s")
                hours = int((now - last).total_seconds() // 3600)
                age_24h = f"{hours}h"
            out[s] = {
                "id": s,
                "enabled": bool(row["enabled"]) if row else True,
                "last_succeeded": last,
                "last_succeeded_empty": last_empty,
                "last_error": row["last_error"] if row else None,
                "blocked": self._blocked(s),
                "cadence": "none" if cad is None else cad,
                "cadence_stale": self._cadence_stale(s),
                "stale_24h": self._stale_24h(s),
                "cadence_age": cadence_age,
                "age_24h": age_24h,
                "clean_count": count,
            }
        return out

    def dashboard(self):
        kinds = {k: 0 for k in KINDS}
        newest = None
        for r in self.conn.execute("SELECT kind, created_at, event_time FROM records").fetchall():
            kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
            for cand in (r["created_at"], r["event_time"]):
                dt = _parse_dt(cand)
                if dt and (newest is None or dt > newest):
                    newest = dt
        jobs = self.list_jobs()
        queued = [j for j in jobs if j["status"] == "queued"]
        running = [j for j in jobs if j["status"] == "running"] if self.worker_available else []
        now = self.now()
        failed = []
        for j in jobs:
            if j["status"] != "failed":
                continue
            fin = _parse_dt(j.get("finished"))
            recent = fin and (now - fin) <= timedelta(hours=24)
            if recent or not j.get("acknowledged"):
                failed.append(j)
        qrows = [q for q in self.list_quarantine() if q.get("open")]
        ff = sum(1 for q in qrows if q["reason"] == "field-fail")
        oh = sum(1 for q in qrows if q["reason"] == "operator-hold")

        def fam(kinds_set):
            n = sum(kinds.get(k, 0) for k in kinds_set)
            return {"count": n, "flag": "gap" if n == 0 else "present"}

        families = {
            "remarks": fam(["remark", "interview"]),
            "decisions": fam(["decision", "legal", "staffing"]),
            "writings": fam(["writing", "social"]),
        }
        topic_channel = []
        health = self.source_health()
        for topic in self.list_topics():
            for ch in COUNTED_CHANNELS:
                recs = [r for r in self.search(topic=topic, channel=ch)]
                usable = [r for r in recs if r["mention_usable"]]
                present_term = [r for r in usable if r.get("term") == "2025_present"]
                raw = len(recs)
                failed_clause = "—"
                thin = False
                if len(usable) == 0:
                    thin = True
                    failed_clause = "zero usable"
                elif len(present_term) == 0:
                    thin = True
                    failed_clause = "thin: no 2025_present usable"
                elif len(usable) < 3:
                    thin = True
                    failed_clause = f"thin: {len(usable)} usable in {ch}"
                covers = COVERING[ch]
                all_stale = all(health[s]["cadence_stale"] for s in covers)
                if all_stale and failed_clause == "—":
                    failed_clause = "stale covering sources"
                elif all_stale and failed_clause != COPY["zero_usable"]:
                    failed_clause = failed_clause + "; stale covering sources"
                health_v = "not-ready" if (thin or all_stale) else "ready"
                topic_channel.append({
                    "topic": topic,
                    "channel": ch,
                    "usable": len(usable),
                    "failed_clause": failed_clause,
                    "raw_clean": raw,
                    "health": health_v,
                })
        return {
            "kinds": kinds,
            "newest": newest,
            "queued": queued,
            "running": running,
            "failed": failed,
            "quarantine_total": len(qrows),
            "quarantine_field_fail": ff,
            "quarantine_operator_hold": oh,
            "families": families,
            "sources": health,
            "topic_channel": topic_channel,
            "worker_available": self.worker_available,
        }
