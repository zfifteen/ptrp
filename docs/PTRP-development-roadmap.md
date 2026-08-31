# PTRP development roadmap

**Evidence layer for the later prediction framework**  
Date: 2026-08-31  
Repo: `zfifteen/ptrp`  
Status of tree: package 0.5.0. Consumable spec `docs/APPROVED_SPEC.md` (file header v8; code comments still say v7). Four chrome screens. One SQLite WAL knowledge base. No auth. In-process worker.

This file is the docs-tree copy of the planning document. It describes features, modifications, and enhancements required so PTRP can supply certified evidence to a later framework that accepts a prediction-market contract and returns a prediction about Trump remarks or decisions. It does not specify that framework. It specifies what PTRP must become so that framework has something honest to read.

**Standing constraint.** PTRP shall not pick a side, store a confidence, grade a call, or hide thin, stale, or quarantined evidence behind a probability. Every enhancement below is rejected if it requires those surfaces.

---

## 1. Role in the later framework

The later framework takes a market contract as input and must answer with a prediction. That answer is only as good as the records it is allowed to cite. PTRP is the certification mill in front of that answer. It is not the model.

| Consumer need | PTRP surface today | Must become |
| --- | --- | --- |
| Usable evidence rows | Search / GetRecord / ExportRetrievalSet | Stable, filter-faithful retrieval set with version + hash + usable flags |
| Topic stance evidence | GetPreference (supporting list only) | Preferences that cite support and contradiction, split by term, mark reversal |
| Permission to cite | Dashboard ready / not-ready + failed clause | Machine-readable health snapshot per topic × counted channel |
| Freshness | Cadence stale + 24h badge; 24h not automated | Export both ages; keep 24h outside automated not-ready |
| Provenance | artifact + job id on ov-record | Every exported row traces to artifact, job, source, fetch time |
| What not to use | Quarantine + discarded table | Consumer can ask “was this locator refused?” without opening the UI |

If the later framework ever collapses ready/not-ready into a probability, it has discarded the only product PTRP was built to emit. Roadmap items that would encourage that collapse are listed under “Do not build.”

---

## 2. What is already closed — do not reopen

These rules are product, not backlog. Enhancements must preserve them.

| Rule | Why the later framework depends on it |
| --- | --- |
| No side picker, no confidence field, no call loop | Predictor must bring its own decision rule. PTRP cannot launder a bet through ingest. |
| Clean vs quarantine hard split | Uncertified text must not appear in ExportRetrievalSet. |
| S7 legal (kind, channel) pairs | A WH remarks job cannot mint a social post. Off-pair is field-fail. |
| S6 stay-committed on stop | Partial jobs do not invent a silent drop bucket. In-flight is job_stopped. |
| S2 write mutex per source | Two writers cannot race the same locator into two current ids. |
| Thin is not-ready, not a third rank | One or two usable rows is the same health as zero. |
| Counted channels only spoken + written_social | Books and legal exist, but they do not make a mention bar ready. |
| Empty pin / empty allowlist block cleanliness, not enabled | Operator can keep a source on while the gate stays shut. |
| Named party on legal = Donald Trump only | “The administration” is not a legal clean row. |
| No wipe-to-empty-first-boot | Production instance is the instance. Factory is not a go-live ritual. |

---

## 3. Gap map — spec vs tree vs consumer

Three classes of gap. Spec-closed but code-thin. Spec-silent but consumer-blocking. Operational.

| Gap | Where it lives | Effect on later framework |
| --- | --- | --- |
| Export ignores current Records filters | `app.py` GET `/records/export` calls `export_retrieval_set()` with no kwargs | Consumer cannot request “this search.” Gets the whole clean base or nothing. |
| `re_extract` and `re_index` succeed without work | `Engine._work` returns succeeded immediately | Operator correction path is theater. Stale extracts stay. |
| Incremental is “latest page,” not since-last-success | `HttpFetch` returns ≤40 items from listing URLs | History holes. Freshness can flip on a thin scrape that missed the new item. |
| No cursor / etag / last-locator stored per source | `sources` table has success times only | Cannot prove “we fetched everything since job X.” |
| Raw artifact stores item text, not original bytes | `_store_artifact` writes `it["text"]` | Audit cannot replay the HTTP body that produced a clean row. |
| Topics/phrases/people not extracted from text | Adapters emit empty `topics[]`; gate requires vocab tags | Preferences stay empty unless Operator item or scripted tests plant tags. |
| Preferences never write contradicting or reversed | `_rebuild_preferences` sets `contradicting=[]` `consistency=consistent` | Predictor cannot see a flip. First-term vs current-term is a list of term labels only. |
| Connectors, probe clock, worker, read-down are RAM | Engine instance fields, not SQLite | True process restart loses QA and ops state. Scheduler tick key is persisted; the rest is not. |
| No out-of-app read API contract | HTML + ad-hoc JSON on POST | Later framework would scrape UI or copy SQLite. Neither is a contract. |
| No retrieval-set identity | Export is an anonymous JSON list | Cannot say “prediction P used set S at time T.” |
| Version label drift | Spec v8 / comments v7 / package 0.5.0 | Engineer and QA disagree about which file is consumable. |

---

## 4. Phased roadmap

Five phases. P0 is unpaid debt against the current spec. P1–P3 make the knowledge base actually usable as evidence. P4 is the only new surface the later framework is allowed to touch. P5 is operate-without-this-chat.

| Phase | Name | Outcome | Depends on | Risk if skipped |
| --- | --- | --- | --- | --- |
| P0 | Honor the spec that is already approved | Export, stubs, persistence, version pin match the tree | None | Consumer and QA test against a lie |
| P1 | Durable fetch | Incremental means since last succeeded fetched>0; artifacts are replayable | P0 labels | Ready flags on incomplete pages |
| P2 | Extract against closed vocab | Clean rows carry topics/phrases from text without minting tags | P1 items in base | Preferences stay empty; health stays zero usable |
| P3 | Preference integrity | Support, contradiction, reversal, term split are real records | P2 tags | Predictor averages a flip into a mush stance |
| P4 | Consumer read contract | Versioned retrieval + health snapshot, still no side | P0 export fix | Framework binds to UI HTML or raw SQLite |
| P5 | Operate the instance | Restart, backup, bind, connector persistence | P0 RAM state | Single-operator instance is fragile |

### P0 — Honor the approved spec

No new product. Make the tree do what the spec already claims. Do this before any “predictor API.”

**P0.1 Filter-faithful export.** GET `/records/export` must pass the same query params Search uses. Empty result keeps the disabled helper. Export fields stay the closed §6 list including `named_party`.

Acceptance: a Records filter for `kind=legal` returns only legal rows in the file. `named_party` is `Donald Trump` on those rows and empty on others.

**P0.2 Implement re_extract and re_index.** `re_extract` re-runs `_gate` + topic/occasion checks on stored records (source-scoped or global) and writes a new `text_version` only when extract fields change. `re_index` rebuilds whatever the search path uses. Today that is the records table; if a real index table is added, this job fills it. Do not no-op succeed.

Acceptance: A9/A17 still pass. After removing a topic from vocab and running `re_extract`, that tag is no longer on clean rows (it quarantines per R-EX-4).

**P0.3 Persist operator-control state.** Store connectors, records-reads, fail-next-load, probe clock, `worker_available` in `meta` (or a controls table). Restart the app and true process restart restore them except `worker_available`, which returns available per CR-QA-2.

Note: worker-available after Restart the app is specified as available. Do not persist “stopped” across Restart the app. Do persist “stopped” across an accidental process crash only if a later ops spec says so. Default: crash = `worker_lost` on running jobs, worker returns available.

**P0.4 Pin the consumable spec.** One label. README, engine docstring, constants header, package version notes, and `docs/APPROVED_SPEC.md` must name the same spec version. Freeze v7 as history if v8 is consumable.

**P0.5 S9 visible on every finished fetch job.** Keep the equation on `ov-job`. Add a test that a production `HttpFetch` empty listing is `succeeded_empty` and does not move `last_succeeded_at`.

### P1 — Durable fetch

The later framework will treat `last_succeeded_at` as “this covering source is current.” That is false if fetch only saw the first page of a listing.

**P1.1 Per-source fetch cursor.** Persist `last_locator`, `last_published_time`, and listing etag/hash per source. `incremental` uses them. `backfill` still uses the operator window. `succeeded_empty` still does not advance the cursor.

**P1.2 Replayable raw artifacts.** Store original bytes (or truncated-with-flag body), content-type, final URL, status code. Item text remains on the clean record. Force re-fetch writes a new artifact row. GetRecord provenance links the artifact that produced that `text_version`.

**P1.3 Window and query honored by adapters.** `backfill` date window and targeted Query are today ignored by `HttpFetch`. Adapters must filter or page until the window is covered or a named cap + “incomplete” job error is stored. Silent truncation is a failed job, not succeeded.

**P1.4 Source-class adapters, still public HTTP.**

- `whitehouse_remarks` / `whitehouse_actions`: official feeds first, HTML second.
- `federal_register`: existing JSON API, page through `per_page` until window covered.
- `app` / `books`: American Presidency Project document listing with dated filter.
- `factbase`: transcript pages only when official/APP text is missing or completeness=excerpt.
- `truth_social`: statuses pagination from the pinned account id, not a one-shot lookup.
- `x_personal`: do not treat nitter as the official pin. Pin match is still the gate. Document the public path actually used.
- `legal`: CourtListener (or successor) search constrained to `named_party` Donald Trump. “The administration” stays F27.
- `interviews`: still allowlist-only. Fetch may collect candidates; gate decides operator-hold vs clean.

**P1.5 Completeness honesty.** Do not label a listing teaser as `full_transcript`. Listing scrapes default to `excerpt`. A later fetch of the document body may write a new `text_version` and raise completeness. Mention-usable already excludes paraphrase; excerpt remains usable. The predictor needs to know which.

### P2 — Extract against the closed vocabulary

Spec already forbids minting topics from extract. That is correct. The hole is the opposite: extract writes nothing, so the topic × channel table stays zero usable after ingest.

**P2.1 Phrase inventory from text.** Exact strings plus plural/possessive, as specified. No synonym invention. Store on the clean record. `re_extract` refreshes phrases without changing `record_id`.

**P2.2 Topic and occasion attach, not invent.** Match operator topic/occasion lists as exact tokens or exact phrases in text. A tag not on the list never appears on a clean row; if the item was submitted with an unknown tag, field-fail `unknown_topic` stays. Adding a topic still creates dashboard rows before ingest (CR-QA-11).

**P2.3 People tags without a people editor.** Keep A2. No people-vocabulary screen in v0. Extract may store surface strings (names that appear). They are display-only. They do not drive ready/not-ready.

**P2.4 Decision extras.** For `federal_register` / `whitehouse_actions`, persist `act_type`, `direction`, `status` from the document type when present. Decision-usable already requires `act_type` and `direction`. Empty extras stay not decision-usable, not guessed.

**P2.5 Term assignment.** Already coded (`term_for`). Keep event_time/published_time → `pre_2017` / `2017_2021` / `2021_2024` / `2025_present`. Health already fails zero `2025_present` usable. Do not let extract override term from rhetoric (“back in 2018”) — term follows the record timestamp.

### P3 — Preference integrity

GetPreference is one of the four stranger-invokable reads. Today it is a supporting-id list. That is not a preference. The spec already describes the real object.

**P3.1 Independence rule in code.** Two locators of one utterance remain one preference record. Independence = different `event_time` + occasion, or one decision + one remark. Implement that as the write gate, not as a comment.

**P3.2 Contradiction and reversal.** Do not average. If later records negate an earlier cited record on the same topic, `consistency=reversed` and `contradicting` lists the later ids. No “middle stance.” No confidence.

**P3.3 Term-split evidence.** Preference payload already has `terms[]`. Make it first-class: `supporting_by_term` / `contradicting_by_term` so the later framework can refuse to treat `2017_2021` remarks as `2025_present` evidence.

**P3.4 refresh_preferences is the only rebuild.** Derived layer. Confirm before start. Global write lock. A fetch job may mark preferences stale; it does not silently rewrite them mid-mutex.

### P4 — Consumer read contract

This is the only phase that adds surface for the later framework. It is still PTRP. It still does not pick a side.

**P4.1 Versioned retrieval set.** ExportRetrievalSet gains an identity: `set_id`, `created_et`, filter digest, record count, list of `(record_id, text_version, text_hash)`. Persist that header so a later prediction can cite `set_id`. The file still has no confidence and no side.

**P4.2 Health snapshot read.** A Records or JSON read that returns the dashboard topic × channel table as data: topic, channel, usable, failed_clause, raw_clean, health, covering sources’ `cadence_stale` flags. This is the permission bit. Automated not-ready stays cadence-only. 24h ages are included as fields, not as a stored live-bet-window object.

**P4.3 Refusal lookup.** Given source+locator, return `clean` | `open field-fail` | `open operator-hold` | `discarded` | `unknown`. The later framework must be able to see that a quote was refused without scraping Quarantine HTML.

**P4.4 Keep §6 as the only stranger reads.** Do not add a fifth chrome screen. If JSON routes are added, they are the same four actions plus health snapshot and refusal lookup. No `/predict`. No `/side`.

**P4.5 Clock and timezone in the payload.** Keep A3. File times UTC ISO-8601. UI remains ET. Snapshot includes generated_at in both forms or UTC plus the ET label string. No UTC column on operator screens.

### P5 — Operate the instance

Production in the spec is “one Fate-operated running instance, reachable without this chat.” That is ops, not a second product.

- **Bind and exposure.** Default bind may stay `0.0.0.0` for a host firewall, but document `PTRP_HOST=127.0.0.1` for laptop use. Still no auth in v0 unless a later spec adds a single shared token. Do not add roles.
- **Backup.** Copy `data/ptrp.sqlite` (WAL + shm) on a schedule outside the app, or add a Control danger-zone “export sqlite” that is not typed DELETE.
- **Restart the app vs process.** CR-QA-2 is an in-process S5. Document how a real systemd/launchd restart should apply S5 then boot with worker available.
- **Fetch failure visibility.** Connector `network`/`auth`/`parse` already fail the job. Persist `last_error`. Do not add silent retry loops.
- **Spec/QA plan sync.** `docs/APPROVED_QA_PLAN.md` is large and older than some S10–S12 rules. After P0.4, mark which QA rows are still live.

---

## 5. Priority matrix

| ID | Item | Why the later framework needs it |
| --- | --- | --- |
| P0.1 | Filter-faithful export | Otherwise the handoff payload is the wrong set. |
| P0.2 | Real re_extract / re_index | Correction path is how Fate fixes a bad tag without editing clean text. |
| P1.1–P1.3 | Cursors, bytes, no silent truncation | Ready must mean “covering sources actually looked.” |
| P2.1–P2.2 | Phrase + topic attach | Without tags, usable counts stay zero and every topic is not-ready. |
| P3.2–P3.3 | Reversal + term split | A 2018 remark and a 2026 remark are not one stance. |
| P4.1–P4.3 | set_id, health snapshot, refusal lookup | Predictor can cite and can abstain without opening chrome. |
| P0.3 / P5 | Persisted controls + backup | The instance that exists is the instance that must survive. |

---

## 6. Do not build

These would look like “features” and would break the component boundary.

- A side picker, stake field, venue name (Kalshi, Polymarket) as a control, or confidence slider.
- A stored live-bet-window object that changes automated not-ready. 24h stale stays a badge and an exported field.
- In-place clean-text edit, or Accept that fills missing timestamps.
- A second hidden knowledge base “for the model.”
- Speech, synthetic Trump audio, leaked or private ingest.
- Auto-growing topic vocab from extract.
- Silent retry loops on network/auth/parse.
- Wipe-to-factory-empty as a go-live step.
- People-vocabulary editor in v0.
- Cron builder. Cadence stays read-only display of 09:00 ET defaults.
- Any route named `predict`, `grade`, `call`, or `resolve` inside `ptrp`.

---

## 7. Suggested sequence of work

A single-operator sequence that does not require the later framework to exist yet.

| Step | Work | Done when |
| --- | --- | --- |
| 1 | P0.4 version pin + P0.1 export filters + test | Export of a filtered Records view matches Search rows field-for-field. |
| 2 | P0.2 re_extract / re_index + P0.3 meta persistence | Restart keeps pins, enable, connectors; re_extract changes tags. |
| 3 | P1.2 artifact bytes + P1.5 completeness honesty | ov-record provenance opens the body that produced that version. |
| 4 | P1.1 cursor + P1.3 window/query in adapters, source by source | incremental on federal_register and whitehouse_remarks is not “first 20 links.” |
| 5 | P2 phrase + topic attach | After adding topic tariffs and ingesting a tariffs remark, spoken usable > 0 or failed clause is not zero usable for the wrong reason. |
| 6 | P3 preference rebuild | GetPreference on a topic with a later negation shows reversed + contradicting ids. |
| 7 | P4 set_id + health snapshot + refusal lookup | A stranger can pull JSON without chrome and still cannot ask for a side. |
| 8 | P5 bind/backup/restart note | Instance survives a host reboot with the same record_ids and ET instants. |

---

## 8. Interface freeze for the later framework

Until P4 ships, the later framework should treat these as the only legal reads, even if they are HTML-backed today:

- Search — filtered clean rows.
- GetRecord(record_id, text_version?) — one version, including `named_party`.
- GetPreference(topic) — derived object or empty.
- ExportRetrievalSet — closed field list.

After P4, add only:

- HealthSnapshot() — topic × counted channel rows + covering stale flags + both freshness ages.
- RefusalLookup(source, locator) — clean | field-fail | operator-hold | discarded | unknown.
- RetrievalSet identity header on export.

The later framework’s own problem — mapping a market contract text onto a topic + channel + term, then deciding whether to emit a prediction or abstain — stays outside PTRP. Abstain maps onto not-ready or onto refusal lookup, not onto a new PTRP status.

---

## 9. Success test for this roadmap

This roadmap is done when all of the following are true, without adding a side picker:

- A stranger can export the exact Records filter they see, and that file is citable by `set_id`.
- A covering source’s `last_succeeded_at` means the adapter walked from the cursor, not that twenty links came back.
- Adding topic X, ingesting public text that contains X, and opening Dashboard shows usable > 0 or a truthful failed clause (thin / no 2025_present / stale covering), not a permanent zero because extract never ran.
- GetPreference can show `reversed` instead of a single supporting list.
- A process that is not this chat can ask health and refusal without parsing chrome HTML.
- Walking all four screens still shows no call loop, no confidence, no in-place text edit.

---

## 10. Document control

- **Artifact.** Development roadmap for PTRP as evidence layer.
- **Date.** 2026-08-31.
- **Basis.** `github.com/zfifteen/ptrp` at main (tree SHA `44c3022…`), `docs/APPROVED_SPEC.md`, `ptrp/engine.py`, `ptrp/fetch.py`, `ptrp/app.py`, `ptrp/constants.py`, `tests/`.
- **Out of scope for this file.** Architecture of the later prediction framework, market-venue adapters, sizing, grading, and any change that would make PTRP recommend YES / NO / NO_CALL.
