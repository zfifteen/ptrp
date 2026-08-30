"""S11 / F51 / CR-QA-10: weekday 09:00 tick after an earlier weekday tick.

QA: Monday 09:00 ticked (enqueued). Wednesday 08:00 no enqueue (next-run that
day's 09:00). Wednesday 09:00 recorded last_schedule_tick with ZERO schedule
jobs for that instant. Recording last_schedule_tick without enqueue is a fail.
"""

from __future__ import annotations

from tests.conftest import ET
from tests.test_spec_v7 import _form


def test_wednesday_0900_after_earlier_weekday_tick_enqueues(env):
    """After a weekday 09:00 tick has already fired, Wednesday 09:00 must enqueue.

    Monday 09:00 tick once. Wednesday 08:00: no enqueue; next-run that day's
    09:00. Wednesday 09:00: enqueue incremental once per enabled non-exempt
    source due that day. Remaining frozen does not enqueue again. 10:00 no
    extra. books/legal (exempt) are not due. Weekly sources are not due on
    Wednesday.
    """
    e, c = env.engine, env.client

    r = _form(c, "/operator/probe-clock", value="2026-08-31T09:00")  # Monday
    assert r.status_code != 500
    monday_jobs = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    assert monday_jobs, "Monday 09:00 must be a tick"
    monday_ids = {j["id"] for j in monday_jobs}
    monday_created = {j["id"]: j.get("created") for j in monday_jobs}

    r = _form(c, "/operator/probe-clock", value="2026-09-02T08:00")  # Wednesday before 09:00
    assert r.status_code != 500
    after8 = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    assert {j["id"] for j in after8} == monday_ids
    nxt = e.next_scheduled_run("whitehouse_remarks")
    n = nxt.astimezone(ET)
    assert (n.year, n.month, n.day, n.hour, n.minute) == (2026, 9, 2, 9, 0)

    r = _form(c, "/operator/probe-clock", value="2026-09-02T09:00")  # Wednesday tick
    assert r.status_code != 500
    at9 = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    new = [j for j in at9 if j["id"] not in monday_ids]
    assert new, (
        "Wednesday 09:00 after an earlier weekday tick must enqueue; "
        f"last_schedule_tick={e._meta_get('last_schedule_tick')!r} new=0 "
        "is recording the tick without enqueue"
    )
    srcs = {j["source"] for j in new}
    daily = {
        "truth_social",
        "x_personal",
        "whitehouse_remarks",
        "whitehouse_actions",
        "interviews",
    }
    assert daily <= srcs
    assert "books" not in srcs
    assert "legal" not in srcs
    assert "app" not in srcs
    assert "campaign" not in srcs
    assert "factbase" not in srcs
    assert "federal_register" not in srcs
    for j in new:
        assert j["type"] == "incremental"
        assert j["triggered_by"] == "schedule"
    assert e._meta_get("last_schedule_tick") == "2026-09-02T09:00"

    e.scheduler_tick()
    frozen = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    assert {j["id"] for j in frozen} == {j["id"] for j in at9}

    r = _form(c, "/operator/probe-clock", value="2026-09-02T10:00")
    assert r.status_code != 500
    e.scheduler_tick()
    after10 = [j for j in e.list_jobs() if j["triggered_by"] == "schedule"]
    assert {j["id"] for j in after10} == {j["id"] for j in at9}

    # Monday jobs were a different instant; do not treat them as Wednesday's tick
    assert monday_created
