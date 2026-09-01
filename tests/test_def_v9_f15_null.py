"""DEF-2 QA-F15: leftover NULL text_version on operator-item force re-fetch."""

from __future__ import annotations

from tests.test_spec_v7 import _form, _seed


def test_F15_operator_item_force_refetch_null_text_version(env):
    """Leftover NULL text_version must not skip versions on operator-item force re-fetch."""
    e, c = env.engine, env.client
    _seed(e)
    loc = "f15-op-null-ver"
    fields = dict(
        type="targeted",
        targeted_mode="operator_item",
        source="whitehouse_remarks",
        kind="remark",
        channel="spoken",
        locator=loc,
        event_time="2025-03-15T16:00:00+00:00",
    )
    r1 = _form(c, "/jobs", text="Old operator text.", **fields)
    assert r1.status_code != 500
    e.drain()
    rec = e.get_record(loc)
    assert rec is not None
    e.conn.execute("UPDATE records SET text_version=NULL WHERE record_id=?", (loc,))
    e.conn.execute("DELETE FROM record_versions WHERE record_id=?", (loc,))
    e.conn.commit()
    r2 = _form(c, "/jobs", text="New operator text.", force_refetch="on", **fields)
    assert r2.status_code != 500
    e.drain()
    cur = e.get_record(loc)
    assert cur is not None
    assert cur["text_version"] is not None
    vers = e.conn.execute(
        "SELECT * FROM record_versions WHERE record_id=? ORDER BY text_version",
        (loc,),
    ).fetchall()
    assert len(vers) >= 2
    prior = e.get_record(loc, text_version=1)
    assert prior is not None
    assert prior["text"] == "Old operator text."
    assert cur["text"] == "New operator text."
