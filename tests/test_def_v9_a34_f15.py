"""DEF-1 QA-A34 / DEF-3 QA-S11 and DEF-2 QA-F15 live holes (Spec v9)."""

from __future__ import annotations

from tests.test_spec_v7 import _form, _seed


def _schedule(e):
    return [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]


def test_A34_clean_env_monday_0800_0900_freeze_1000(env):
    """A34: Monday 08:00 extra=0; 09:00 enqueue once; freeze extra=0; 10:00 extra=0."""
    e, c = env.engine, env.client
    n0 = len(_schedule(e))

    r = _form(c, "/operator/probe-clock", value="2026-08-24T08:00")
    assert r.status_code != 500
    assert len(_schedule(e)) - n0 == 0

    r = _form(c, "/operator/probe-clock", value="2026-08-24T09:00")
    assert r.status_code != 500
    at9 = _schedule(e)
    assert len(at9) > n0
    ids9 = {j["id"] for j in at9}

    e.scheduler_tick()
    frozen = _schedule(e)
    assert {j["id"] for j in frozen} == ids9

    r = _form(c, "/operator/probe-clock", value="2026-08-24T10:00")
    assert r.status_code != 500
    after10 = _schedule(e)
    assert {j["id"] for j in after10} == ids9


def test_re_set_monday_0900_after_tuesday_tick_no_second_enqueue(env):
    """Live hole: after Monday 09:00 AND Tuesday 09:00, HTML re-Set Monday 09:00 extra=0.

    Tuesday tick still happened. Remaining frozen on that Monday instant does not
    enqueue again. Existing Wednesday-after-Monday coverage stays in
    tests/test_s11_wednesday_tick.py.
    """
    e, c = env.engine, env.client

    r = _form(c, "/operator/probe-clock", value="2026-08-31T09:00")  # Monday
    assert r.status_code != 500
    monday = _schedule(e)
    assert monday, "Monday 09:00 must be a tick"
    monday_ids = {j["id"] for j in monday}

    r = _form(c, "/operator/probe-clock", value="2026-09-01T09:00")  # Tuesday
    assert r.status_code != 500
    after_tue = _schedule(e)
    tue_new = [j for j in after_tue if j["id"] not in monday_ids]
    assert tue_new, "Tuesday 09:00 tick still happened"
    ids_after_tue = {j["id"] for j in after_tue}

    r = _form(c, "/operator/probe-clock", value="2026-08-31T09:00")  # re-Set already-ticked Monday
    assert r.status_code != 500
    after_reset = _schedule(e)
    extra = [j for j in after_reset if j["id"] not in ids_after_tue]
    last = e._meta_get("last_schedule_tick")
    assert extra == [], (
        "HTML re-Set of a Monday 09:00 that already ticked must not enqueue again; "
        f"extra={len(extra)} last_schedule_tick={last!r}"
    )

    e.scheduler_tick()
    frozen = _schedule(e)
    extra_freeze = [j for j in frozen if j["id"] not in ids_after_tue]
    assert extra_freeze == []


def test_F15_operator_item_html_force_refetch_versions_resolvable(env):
    """F15 live hole: Operator item HTML Run, same locator, new text, force_refetch.

    After drain: current text_version is not None; record_versions n>=2; v1 keeps
    old text; current has new text. Incremental F15 is not weakened.
    """
    e, c = env.engine, env.client
    _seed(e)
    loc = "f15-op-html-1"
    fields = dict(
        type="targeted",
        targeted_mode="operator_item",
        source="whitehouse_remarks",
        kind="remark",
        channel="spoken",
        locator=loc,
        event_time="2025-03-15T16:00:00+00:00",
    )
    r1 = _form(c, "/jobs", text="Version one of the operator remark.", **fields)
    assert r1.status_code != 500
    e.drain()
    r2 = _form(
        c,
        "/jobs",
        text="Version two of the operator remark.",
        force_refetch="on",
        **fields,
    )
    assert r2.status_code != 500
    e.drain()

    rec = e.get_record(loc)
    assert rec is not None, "operator item must write a clean record"
    assert rec["text_version"] is not None
    vers = e.conn.execute(
        "SELECT * FROM record_versions WHERE record_id=? ORDER BY text_version",
        (loc,),
    ).fetchall()
    assert len(vers) >= 2, f"record_versions n={len(vers)} expected >=2"
    prior = e.get_record(loc, text_version=1)
    assert prior is not None
    assert prior["text"] == "Version one of the operator remark."
    assert rec["text"] == "Version two of the operator remark."
