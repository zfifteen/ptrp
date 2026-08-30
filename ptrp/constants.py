"""Closed enums and copy bank from Approved Spec v7."""

from __future__ import annotations

SOURCES = [
    "whitehouse_remarks",
    "whitehouse_actions",
    "app",
    "factbase",
    "federal_register",
    "truth_social",
    "x_personal",
    "campaign",
    "books",
    "interviews",
    "legal",
]

JOB_TYPES = [
    "incremental",
    "backfill",
    "targeted",
    "re_extract",
    "re_index",
    "refresh_preferences",
]

STATUSES = ["queued", "running", "succeeded", "succeeded_empty", "failed", "cancelled"]
CHANNELS = ["spoken", "written_social", "written_official", "legal", "other"]
KINDS = ["remark", "decision", "writing", "interview", "social", "legal", "staffing"]
COMPLETENESS = ["full_transcript", "excerpt", "paraphrase"]
TRIGGERED_BY = ["user", "schedule", "retry"]
QUARANTINE_REASONS = ["field-fail", "operator-hold"]
TERMS = ["pre_2017", "2017_2021", "2021_2024", "2025_present"]
COUNTED_CHANNELS = ["spoken", "written_social"]

LEGAL_PAIRS = {
    "whitehouse_remarks": {("remark", "spoken")},
    "whitehouse_actions": {("decision", "written_official"), ("staffing", "written_official")},
    "app": {("remark", "spoken"), ("decision", "written_official"), ("writing", "written_official")},
    "factbase": {("remark", "spoken")},
    "federal_register": {("decision", "written_official")},
    "truth_social": {("social", "written_social")},
    "x_personal": {("social", "written_social")},
    "campaign": {("remark", "spoken"), ("writing", "other")},
    "books": {("writing", "other")},
    "interviews": {("interview", "spoken")},
    "legal": {("legal", "legal")},
}

CADENCE = {
    "truth_social": "daily",
    "x_personal": "daily",
    "whitehouse_remarks": "daily",
    "whitehouse_actions": "daily",
    "app": "weekly",
    "factbase": "weekly",
    "federal_register": "weekly",
    "campaign": "weekly",
    "interviews": "daily",
    "books": None,
    "legal": None,
}

COVERING = {
    "spoken": ["whitehouse_remarks", "app", "factbase", "campaign", "interviews"],
    "written_social": ["truth_social", "x_personal"],
}

EXEMPT = {"books", "legal"}
PIN_SOURCES = {"x_personal": "x", "truth_social": "truth_social"}

COPY = {
    "worker_banner": "Worker not available. New jobs sit queued. Nothing is executing.",
    "blocked_allowlist": "blocked: empty allowlist",
    "blocked_pin": "blocked: empty pin",
    "raw_clean": "raw clean (NOT the bar)",
    "accept_fieldfail": "Cannot accept. Fix source or extract, then run a new job.",
    "discard_helper": "Discarded items shall not reappear as clean on the next incremental run unless source content or locator changed, or Fate force re-fetches.",
    "dont_start": "Rejected: a job for this source is already queued or running (job {id}). A second job would write the same source.",
    "queue_behind": "Queued behind job {id} (same source). It will not run until that job leaves queued or running.",
    "third": "Rejected: source {source} already has a queued job waiting behind {id}.",
    "waiting": "waiting: same source as {id}",
    "force_refetch": "Force re-fetch — pull new raw artifacts; may write a new text_version (R-JOB-13)",
    "export": "Export retrieval set",
    "delete_base": "This deletes the clean base. Type DELETE to confirm.",
    "footnote": "Counted channels are spoken and written_social. Spoken covering: whitehouse_remarks, app, factbase, campaign, interviews. books and legal are exempt. This table is not a venue picker.",
    "correction": "Clean text is not editable. Fix source config or re-ingest / re-extract.",
    "src_required": "Source is required.",
    "backfill_window": "Backfill needs a date window.",
    "targeted_need": "Targeted needs a topic, query, or occasion.",
    "pick_source": "Pick a source or global.",
    "start_end": "Start must be on or before end.",
    "disabled_confirm": "This source is disabled. Scheduler will not run it. Manual Run still enqueues. Continue?",
    "not_scheduled": "not scheduled",
    "cancel_confirm": "Cancel job {id}? Clean records already written stay. In-flight items go to quarantine as job_stopped.",
    "equation": "fetched = written + updated + unchanged + quarantined + fetch_fail",
    "stopped_helper": "written + updated = stayed clean. quarantined includes job_stopped. fetched = written + updated + unchanged + quarantined + fetch_fail.",
    "job_stopped_accept": "Cannot accept. A later job for this locator may write clean if it then passes the gate. That later clean write is not also an open job_stopped item.",
    "no_records": "No clean records match.",
    "no_jobs": "No jobs match these filters.",
    "no_q": "No quarantined items.",
    "newest_none": "Newest clean record: none",
    "empty_topics": "No topic × channel rows. Add topics in Control → Vocabularies, then ingest.",
    "empty_snapshot": "No queued, running, or unacknowledged failed jobs.",
    "dashboard_fail": "Dashboard failed to load",
    "reindex_confirm": "Rebuild the index from all stored clean records. Confirm.",
    "refresh_confirm": "Rebuild derived preferences from current clean records. Confirm.",
    "books_helper": "Books are not mention-usable. Channel is other.",
    "nothing_export": "Nothing to export.",
    "cancel_toast": "Job cancelled. Stayed clean remain. In-flight quarantined as job_stopped.",
    "delete_records": "Delete clean records? Confirm. Cancel leaves records.",
    "stop_worker": "Stop the worker? Running jobs will fail with worker_lost.",
    "start_worker": "Start worker",
    "restart_app": "Restart the app? The knowledge base stays. Running jobs fail with worker_lost.",
    "search_cannot": "Search cannot run.",
    "getrecord_cannot": "GetRecord cannot run.",
    "getpref_cannot": "GetPreference cannot run.",
    "export_cannot": "Export cannot run.",
    "operator_item_need": "Operator item needs source, locator, text, kind, and channel.",
    "operator_item_pin": "A written_social Operator item is refused if no pin is set.",
    "zero_usable": "zero usable",
}

STATUS_PILLS = [
    "queued", "running", "succeeded", "succeeded_empty", "failed", "cancelled",
    "stale", "blocked", "field-fail", "operator-hold", "ready", "not-ready",
    "available", "not available", "enabled", "disabled", "unacknowledged",
]

FETCH_TYPES = {"incremental", "backfill", "targeted"}
GLOBAL_TYPES = {"re_index", "refresh_preferences"}
WRITE_TYPES = {
    "incremental", "backfill", "targeted", "re_extract", "re_index", "refresh_preferences"
}

EXPORT_FIELDS = [
    "record_id", "text_version", "text_hash", "channel", "event_time",
    "published_time", "completeness", "mention_usable", "decision_usable",
    "kind", "source", "text", "named_party",
]

