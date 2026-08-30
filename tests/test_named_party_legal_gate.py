"""S12 leftover clean-legal named_party gate (DEF-1 QA-F52, DEF-2 QA-A9, DEF-3 QA-S12, DEF-4 QA-CR-QA-8)."""

from __future__ import annotations


from fastapi.testclient import TestClient

from tests.conftest import book_item
from tests.test_spec_v7 import _legal_item, _operator_item_params, _seed


LEFTOVER_EMPTY = "lg-leftover-empty"
LEFTOVER_NULL = "lg-leftover-null"
SAMPLE_RULE = "missing named_party (legal)"


def _insert_leftover_legal(engine, record_id, named_party):
    """Bypass the ingest gate: a stored 'clean' legal row with empty or missing named_party."""
    src = engine.conn.execute("SELECT * FROM records WHERE kind='legal' LIMIT 1").fetchone()
    assert src is not None, "need one valid clean legal to copy leftover columns from"
    cols = [d[1] for d in engine.conn.execute("PRAGMA table_info(records)").fetchall()]
    values = []
    for col in cols:
        if col == "record_id":
            values.append(record_id)
        elif col == "locator":
            values.append(record_id)
        elif col == "named_party":
            values.append(named_party)
        elif col == "url":
            values.append("https://qa.example/" + record_id)
        elif col == "title":
            values.append("Leftover legal " + record_id)
        else:
            values.append(src[col])
    placeholders = ",".join("?" for _ in cols)
    engine.conn.execute(
        f"INSERT INTO records ({','.join(cols)}) VALUES ({placeholders})",
        values,
    )
    engine.conn.commit()


def _reopen(env):
    from ptrp.app import create_app
    from ptrp.engine import Engine

    e2 = Engine(db_path=env.db, fetch=env.fetch, clock=env.clock)
    e2.boot()
    c2 = TestClient(create_app(e2))
    return e2, c2


def test_leftover_empty_or_missing_named_party_legal_is_field_fail_after_open(env):
    e = env.engine
    _seed(e)
    e.fetch.script("legal", [_legal_item(locator="lg-ok")])
    e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    e.drain()
    e.fetch.script("books", [book_item()])
    e.enqueue_job(type="incremental", source="books", triggered_by="user")
    e.drain()
    assert e.search(source="legal")
    assert e.search(source="books")

    _insert_leftover_legal(e, LEFTOVER_EMPTY, "")
    _insert_leftover_legal(e, LEFTOVER_NULL, None)
    before = e.search(kind="legal")
    leftover_ids = {LEFTOVER_EMPTY, LEFTOVER_NULL}
    assert leftover_ids <= {r["record_id"] for r in before}

    e2, c2 = _reopen(env)

    for loc in leftover_ids:
        assert e2.get_record(loc) is None
        q = [
            i
            for i in e2.list_quarantine()
            if i.get("locator") == loc and i.get("open")
        ]
        assert q, loc
        assert q[0]["reason"] == "field-fail"
        assert q[0]["failed_rule"] == SAMPLE_RULE
        acc = e2.accept_quarantine(q[0]["id"], confirm=True)
        assert not acc.ok

    recs = e2.search(kind="legal")
    assert leftover_ids.isdisjoint({r["record_id"] for r in recs})
    assert recs
    for r in recs:
        assert r.get("named_party") == "Donald Trump"

    books = e2.search(source="books")
    assert books


def test_leftover_not_presented_as_clean_on_records_getrecord_export(env):
    e = env.engine
    _seed(e)
    e.fetch.script("legal", [_legal_item(locator="lg-ok")])
    e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    e.drain()
    _insert_leftover_legal(e, LEFTOVER_EMPTY, "")

    e2, c2 = _reopen(env)

    html = c2.get("/records").text
    assert LEFTOVER_EMPTY not in html
    html_kind = c2.get("/records?kind=legal").text
    assert LEFTOVER_EMPTY not in html_kind

    html_ov = c2.get("/records?record=" + LEFTOVER_EMPTY).text
    assert 'id="ov-record"' not in html_ov

    got = e2.get_record(LEFTOVER_EMPTY)
    assert got is None

    exp = e2.export_retrieval_set()
    assert LEFTOVER_EMPTY not in {row["record_id"] for row in exp}
    legal_exp = e2.export_retrieval_set(kind="legal")
    assert legal_exp
    assert all(row.get("named_party") == "Donald Trump" for row in legal_exp)
    assert all("named_party" in row for row in e2.export_retrieval_set())

    r = c2.get("/records/export")
    assert r.status_code == 200
    rows = r.json()
    assert LEFTOVER_EMPTY not in {row.get("record_id") for row in rows}
    for row in rows:
        assert "named_party" in row

    qhtml = c2.get("/quarantine?reason=field-fail").text
    assert SAMPLE_RULE in qhtml
    assert "field-fail" in qhtml


def test_remaining_clean_legal_ov_record_shows_donald_trump(env):
    e, c = env.engine, env.client
    _seed(e)
    e.fetch.script("legal", [_legal_item(locator="lg-ok")])
    e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    e.drain()
    _insert_leftover_legal(e, LEFTOVER_EMPTY, "")

    e2, c2 = _reopen(env)
    recs = e2.search(kind="legal")
    assert recs
    rec = recs[0]
    assert rec["named_party"] == "Donald Trump"
    html = c2.get("/records?record=" + rec["record_id"]).text
    assert 'id="ov-record"' in html
    assert 'id="rec-named-party"' in html
    assert "Donald Trump" in html
    assert e2.get_record(rec["record_id"])["named_party"] == "Donald Trump"
    payload = e2.export_retrieval_set(kind="legal")
    assert payload[0]["named_party"] == "Donald Trump"


def test_legal_ingested_with_named_party_donald_trump_stays_clean(env):
    e = env.engine
    _seed(e)
    e.fetch.script("legal", [_legal_item(locator="https://qa.example/legal-dt")])
    e.enqueue_job(type="incremental", source="legal", triggered_by="user")
    e.drain()
    recs = e.search(source="legal")
    assert recs
    assert recs[0]["named_party"] == "Donald Trump"
    e2, _ = _reopen(env)
    recs2 = e2.search(source="legal")
    assert recs2
    assert recs2[0]["locator"] == "https://qa.example/legal-dt"
    assert recs2[0]["named_party"] == "Donald Trump"
    assert e2.get_record(recs2[0]["record_id"])["named_party"] == "Donald Trump"


def test_named_party_the_administration_still_f27_not_clean(env):
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
    q = e.list_quarantine()
    assert q and q[0]["reason"] == "field-fail"
