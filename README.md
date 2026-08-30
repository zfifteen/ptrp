# PTRP

PTRP is a standalone single-operator pipeline. Fate ingests public Trump records into one knowledge base and runs jobs from four screens: Dashboard, Control, Records, and Quarantine.

This tree implements **Approved Spec v5** (`docs/APPROVED_SPEC.md`). There is no first-run wizard. Factory boot enables all eleven sources. The schedule clock is 09:00 America/New_York.

## Requirements

- Python 3.13
- pip packages: `fastapi`, `uvicorn`, `httpx`, `jinja2` (tests also need `pytest`)

## Install

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Production instance

SQLite path (WAL): `data/ptrp.sqlite` by default. Override with `PTRP_DB`.

```bash
export PTRP_DB=data/ptrp.sqlite
python -m ptrp
```

Then open:

- Dashboard: http://127.0.0.1:8000/
- Control: http://127.0.0.1:8000/control
- Records: http://127.0.0.1:8000/records
- Quarantine: http://127.0.0.1:8000/quarantine

Host/port: `PTRP_HOST` (default `0.0.0.0`), `PTRP_PORT` (default `8000`).

No auth. Displayed times are America/New_York labeled ET. Stored times are UTC.

Fetch adapters talk to public HTTP for the eleven sources. Tests inject a scripted fetch port and never hit the live network.

On first boot of an empty database, all eleven sources are `enabled`. `enabled` is independent of `blocked` (`interviews` still `blocked: empty allowlist`; empty official pins still `blocked: empty pin`). Factory defaults are not reapplied on restart of a non-empty instance.

## Tests

```bash
pytest
```

or, from this directory:

```bash
python -m pytest
```

## Knowledge base

One SQLite file (WAL). Restart keeps record ids. Job history is append-only. Typed `DELETE` on Control → Sources danger zone removes clean records and derived preferences; jobs and raw artifacts remain.
