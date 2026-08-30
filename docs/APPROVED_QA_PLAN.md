# PTRP QA Plan Draft

**Artifact:** QA Plan Draft  
**State:** Approved  
**Version:** v5  
**Date:** 2026-08-30  
**Owner:** Quality Assurance Guru  
**Source:** Approved Spec v8, file `/workspace/ptrp-spec-approved-v8.md` (also `/workspace/ptrp-spec-draft.md`). Frozen Spec v7 is history.  
**Consumable source:** Approved Spec v8 only. Frozen Spec v7 at `/workspace/ptrp-spec-approved-v7.md` is history. Frozen QA Plan v4 at `/workspace/ptrp-qa-plan-approved-v4.md` is bound to Spec v7 and is not this Draft.  
**Dedicated checks:** 108. A1–A39 including A5b = 40. F1–F53 = 53. CR-QA-1 through CR-QA-11 = 11. CR-USER-1 = 1. S10, S11, S12 = 3. Plan v4 was 105; the +3 are QA-A39, QA-F53, QA-CR-USER-1. A23 and F36 are rewritten, not added.  
**Execution gate:** This plan is Approved. Execution against Approved Spec v8 is legal. Frozen Plan v4 must not be used. Do not implement product code. Pytest is not QA execution. This is not a ship.  
**This is not a ship.** QA does not ship. Ship-gate subset remains Spec stranger done-when: A1, A2, A3, A9, A11, A15, A16.

---

## 1. Header metadata

| Field | Value |
| --- | --- |
| Artifact | QA Plan Draft |
| State | Approved |
| Version | v5 |
| Date | 2026-08-30 |
| Owner | Quality Assurance Guru |
| Source Spec | Approved Spec v8, file `/workspace/ptrp-spec-approved-v8.md` (also `/workspace/ptrp-spec-draft.md`) |
| Frozen Spec | Spec v7 at `/workspace/ptrp-spec-approved-v7.md` is history |
| Frozen Plan | QA Plan v4 at `/workspace/ptrp-qa-plan-approved-v4.md` is bound to Spec v7 and is not this Draft |
| Dedicated checks | 108 |
| Execution | Legal against Approved Spec v8 |

This plan maps each Spec acceptance test (A1–A39 including A5b) and each failure case (F1–F53) to an executable check with a dedicated check id. CR-QA-1 through CR-QA-11, CR-USER-1, and S10, S11, S12 each have a dedicated check in addition to the A/F rows they map onto. Do not collapse two IDs into one check. Total dedicated checks = 108. Plan v4 was 105; the +3 are QA-A39, QA-F53, QA-CR-USER-1. A23 and F36 are rewritten, not added. Frozen Plan v4 is not the source. A prior plan at this path is replaced entirely.

Section 5–7 of the Spec win on conflict with section 8 packet copy. Packet display of a previously `running` job as `queued` is struck. Packet leftover “Global jobs are not this mutex” is struck by section 5.5 / A5b. Packet next-run copy `scheduler skip` is struck. Disabled-source and exempt next-run copy is the exact string `not scheduled`. Leftover section 6 list without `named_party` is struck; S12 wins. Q1 cancel copy remains: confirm `Cancel job {id}? Clean records already written stay. In-flight items go to quarantine as job_stopped.` toast `Job cancelled. Stayed clean remain. In-flight quarantined as job_stopped.` Fail if struck packet cancel copy appears. Q1 stays closed. Q2 is closed on this Draft: QA-A24 Sets a weekday after 09:00 ET, not at 09:00. Pass/fail does not treat S11 enqueue as an A24 fail. The tick, freeze, and no-second-enqueue stay on QA-A34, QA-F51, and QA-S11. Plan v4 Advisory A1 (next-run mapping) stays: QA-A24 step 3 wording is not the expected next-run value; chrome clock uses the probe instant; next-run display is the CR-E2 after-09:00 mapping, not the probe instant itself; do not fail a product that shows next weekday 09:00 after a Monday 10:00 Set. Spec v8 Advisory A1 (S12 wins leftover named_party omit) and Spec v8 Advisory A2 (global mutex struck) stay as Spec advisories, not Plan blockers. Empty first-boot observation is out of scope (CR-USER-1). Do not invent a wipe.

---

## 2. Pass condition

This artifact is **quality only**. It does not ship the product. QA does not ship.

**Ship-gate subset** (Spec stranger done-when): **A1, A2, A3, A9, A11, A15, A16**. Mapped here as QA-A1, QA-A2, QA-A3, QA-A9, QA-A11, QA-A15, QA-A16. The rest of A1–A39 including A5b and F1–F53, plus dedicated CR-QA-1 through CR-QA-11, CR-USER-1, and S10–S12 checks, are required for this Spec to be complete and are still executed when this plan is Approved. Total dedicated checks = 108.

G11 still requires User confirm + no open blockers. Passing the ship-gate subset in an Approved execution does not ship.

Pass of this plan (once Approved and executed): every dedicated check is run; specified behavior matches Expected observable; unspecified remainder is not treated as pass (it is a Change Request).

A failed check against specified behavior is a product defect (Engineer). A failed check that exposes unspecified behavior is a Change Request (Spec). Do not treat that as a pass.

**Result routing**

| Outcome | Route |
| --- | --- |
| Check run (after Approval); specified observable matches | Pass |
| Specified behavior missing or wrong | Defect (Engineer) |
| Run exposes a hole the Spec did not close; unspecified remainder hit | Change Request (Spec) |
| Unspecified remainder not exercised; specified observable held | Pass on the specified part only; do not treat the unexercised hole as pass of that hole |
| Draft/Blocked plan executed anyway | Illegal; not a pass |

**Out of plan**

- Execution is illegal while this plan is Draft or Blocked. Do not run checks until Approved.
- Product code is illegal under this plan. QA does not implement.
- Historical files are not in force: frozen Spec v7, frozen QA Plan v4 as a v8 execution source, frozen Spec v5, frozen QA Plan v2, pipeline requirements, v0-spec, standalone UI packet, mock HTML as a stack, review writeups, H-patch notes. The UI packet is absorbed into Spec section 8; this plan consumes only Approved Spec v8. Where section 8 conflicts with section 5–7, section 5–7 win.
- Language, framework, database, host, and vendor are not specified and are not in this plan. Checks do not name them.
- No hidden test harness the Spec does not grant.
- QA does not ship. G11 remains User confirm + no open blockers.

---

## 3. Coverage matrix

One row per Spec A and F. Related IDs may share setup; each ID still has its own check. Do not collapse two IDs into one check. The CR-QA / S column names the Change Request or named hole that maps onto that A/F; it does not replace the dedicated CR-QA, CR-USER-1, and S checks in the second matrix. Total dedicated checks = 108 (A1–A39 including A5b = 40; F1–F53 = 53; CR-QA-1 through CR-QA-11 = 11; CR-USER-1 = 1; S10, S11, S12 = 3). Plan v4 was 105; the +3 are QA-A39, QA-F53, QA-CR-USER-1. A23 and F36 are rewritten, not added.

### 3.1 Acceptance and failure rows

| Spec ID | Check ID | One-line expected | Related IDs | CR-QA / S |
| --- | --- | --- | --- | --- |
| A1 | QA-A1 | Dashboard with no job running shows kind totals, newest clean, source health, job snapshot, quarantine count, worker pill, Stop worker or Start worker, topic × counted channel ready/not-ready only | R-UI-1..6, A15 | CR-QA-1 |
| A2 | QA-A2 | Valid incremental on an enabled source appears and moves queued to running to terminal when a worker executes it | A3, F1 | |
| A3 | QA-A3 | Open job: params, stored status, log, S9 equation, error or em-dash, artifact/clean/quarantine links; in-flight in quarantined on stop | A2, A22, S9, F32, F35 | |
| A4 | QA-A4 | backfill with no window, or targeted **Query** with topic/query/occasion all empty: refused, no job row. Does not apply to Operator item (S10) | F2, A36, A37, F49 | S10 |
| A5 | QA-A5 | Second write-scoped job for truth_social while one is running: ov-dup queue-behind or do not start | F3, F4, A5b, R-JOB-9 | |
| A5b | QA-A5b | Global re_extract while any source write job is running: same overlay; queue-behind waits until every touched source is free | F3, F4, F24, R-JOB-9 | |
| A6 | QA-A6 | Cancel confirm and toast are Spec R-JOB-7 copy; queued or running becomes cancelled; S6 stayed/in-flight/index | F5, F32, F35, A22, R-JOB-7 | |
| A7 | QA-A7 | Retry failed: new job id, same params, pointer to failed job; failed job remains | F3, R-JOB-8 | |
| A8 | QA-A8 | CR-E2. Disabled source next run exact copy `not scheduled` even if it has a cadence; Manual Run still possible after confirm; scheduler does not enqueue | F23, F37, A24, CR-E2, R-UI-12 | |
| A9 | QA-A9 | Open clean record: current text, prior versions, extract, source, artifact, job, both timestamps, completeness, mention-usable, decision-usable, and named_party when kind is legal; no text edit; no confidence | A15, A17, A38, F19, F20, F52 | S12 |
| A10 | QA-A10 | Export retrieval set contains section 6 fields including named_party for each current search row (Donald Trump on legal; empty on other kinds; field not omitted) | A17, A38, F28, F52 | S12 |
| A11 | QA-A11 | Quarantine: field-fail vs operator-hold distinguishable; Accept disabled on field-fail; Accept on passing operator-hold promotes without editing; Discard holds F10 | F7, F8, F9, F10, F35 | |
| A12 | QA-A12 | Stop worker during running with some clean writes: ov-worker-stop; confirm applies S5 immediately; banner every screen; stored failed/worker_lost; display matches; S6; no running; returning worker does not resume; retry is new id. A switch that only paints not available is a fail | F1, F5, F38, F39, A25, S5, S6 | CR-QA-1 |
| A13 | QA-A13 | Empty interview allowlist: interviews shows blocked: empty allowlist; fetched=0 does not mark fresh | F12, CR-E1 | CR-QA-8 |
| A14 | QA-A14 | Topic with 0 or 1–2 usable rows in spoken is not-ready with failed thin clause; not a third rank; no venue. After Add topic, rows exist before ingest | F16, A35, F48 | CR-QA-11 |
| A15 | QA-A15 | Walk four screens: no call-loop, no side picker, no in-place clean-text edit, no confidence, no venue picker | F19, F20 | |
| A16 | QA-A16 | Restart the app: ov-restart; knowledge base stays; same record_ids resolve; same ET instants; enable/disable/topics/occasions/pins/allowlist persist; worker returns available. Typed DELETE is not restart | A26, A33, F40 | CR-QA-2, CR-QA-9 |
| A17 | QA-A17 | Records: Search, GetRecord (incl. prior version and named_party), GetPreference, ExportRetrievalSet; none starts a job or ingests; Records reads down shows F28 / F41 | A9, A10, A27, F28, F41 | CR-QA-3 |
| A18 | QA-A18 | Empty Save of official X pin or Truth Social pin: that source blocked: empty pin; no clean written_social from it | F31, F50, S4 | CR-QA-7 |
| A19 | QA-A19 | Operator item whitehouse_remarks kind social channel written_social is field-fail, not clean. fetched=1 | F33, F44, A30, S7 | CR-QA-6 |
| A20 | QA-A20 | Spoken not-ready from stale uses only whitehouse_remarks, app, factbase, campaign, interviews | F17, F34, S8 | |
| A21 | QA-A21 | books source health: last success if any; no cadence-stale clock; exempt; next scheduled run `not scheduled` | F34, F37, S8, CR-E2 | |
| A22 | QA-A22 | Cancel or fail a running fetch after some items fetched not yet clean: those items Quarantine job_stopped; equation has no leftover | F32, F35, S6, S9 | |
| A23 | QA-A23 | Current instance: no first-run wizard; blocked independent of enabled; interviews empty allowlist still blocked: empty allowlist; empty social pins still blocked: empty pin; not all eleven enabled; not empty first boot | F36, CR-E1, A16, A39, F53 | CR-USER-1 |
| A24 | QA-A24 | CR-E2 next-run display. Probe clock Set a weekday after 09:00 ET, not at 09:00. Daily: next weekday 09:00 ET. Weekly: following Monday 09:00 ET. books `not scheduled`. Display of next-run is not a tick. S11 enqueue is not an A24 fail; tick stays on QA-A34 / QA-F51 / QA-S11 | F37, A8, CR-E2, CR-QA-10 | CR-QA-10 |
| A25 | QA-A25 | Stop worker during a running job that already wrote some clean records: same pass as A12, induced by Stop worker | A12, F1, F38, F39 | CR-QA-1 |
| A26 | QA-A26 | Restart the app after a clean record_id exists: same record_id resolves; enable/disable and pins persist; worker returns available | A16, A33, F40 | CR-QA-2 |
| A27 | QA-A27 | Set Records reads to down, then use Search: copy `Search cannot run.` No invented records. Set available, Search runs | A17, F28, F41 | CR-QA-3 |
| A28 | QA-A28 | Set Fail next load to Dashboard, open Dashboard: copy `Dashboard failed to load` plus Retry. Retry loads Dashboard | F29, F42 | CR-QA-4 |
| A29 | QA-A29 | Set Connector auth on books, Run incremental books, worker available: job failed, error auth. S6 | F25, F43 | CR-QA-5 |
| A30 | QA-A30 | Operator item source whitehouse_remarks, kind social, channel written_social: field-fail, not clean, fetched=1 | A19, F33, F44 | CR-QA-6 |
| A31 | QA-A31 | Save a non-empty official X pin, then Operator item x_personal pin match lookalike: quarantined, not clean. Source is not blocked: empty pin | F11, F45, A18 | CR-QA-7 |
| A32 | QA-A32 | Operator item source legal, named_party the administration: not ingested as legal clean | F27, F46 | CR-QA-8 |
| A33 | QA-A33 | Displayed job created time after Restart the app: same ET instant as before restart. No UTC string on the screen | A16, CR-QA-9 | CR-QA-9 |
| A34 | QA-A34 | Probe clock Set Monday 08:00 ET, then Set Monday 09:00 ET, leave frozen, then Set Monday 10:00 ET: Spec named instants (S11) | F47, F51, A24 | CR-QA-10, S11 |
| A35 | QA-A35 | Add topic tariffs with no ingest: Dashboard shows tariffs × spoken and tariffs × written_social, usable 0, not-ready, zero usable | A14, F16, F48 | CR-QA-11 |
| A36 | QA-A36 | Targeted Operator item with topic, query, and occasion empty, and source, locator, text, kind, and channel filled: job is created. Query copy is not shown | A4, A37, F2, F49 | S10 |
| A37 | QA-A37 | Targeted Operator item missing locator: refused. Copy `Operator item needs source, locator, text, kind, and channel.` No job. Not A4 | A4, A36, F49 | S10 |
| A38 | QA-A38 | Open a clean legal record: ov-record shows named_party Donald Trump. GetRecord includes named_party. Export of that row includes named_party Donald Trump | A9, A10, F52 | S12, CR-QA-8 |
| A39 | QA-A39 | no wipe; Restart the app present and is not a wipe | A15, A23, F53, F21 | CR-USER-1 |
| F1 | QA-F1 | Worker not available via Stop worker: banner every screen; stored running becomes failed/worker_lost; display matches; new Run queued; no running; S6; mutex released; returning worker does not resume | A12, A25, F38, F39, S5, S6 | CR-QA-1 |
| F2 | QA-F2 | Incremental/backfill/targeted **Query** missing required params: Run refused in place; no job row. Does not apply to Operator item | A4, F49, A36, A37 | S10 |
| F3 | QA-F3 | Second write-scoped job when source already has one queued or running, including global occupant: queue-behind or do not start; visible reason | A5, A5b, F4, F24 | |
| F4 | QA-F4 | Third write-scoped job while one running and one queued-behind: rejected only; no third job | A5, F3 | |
| F5 | QA-F5 | failed / cancelled / worker_lost: S6 only — stayed clean remain; in-flight not clean; index = stayed set; that job id writes nothing further; earlier succeeded records stay | A6, A12, A22, F32, F35 | |
| F6 | QA-F6 | Fetch returns nothing in-scope while Connector is ok: succeeded_empty; freshness clocks do not move | A13, A29 | CR-QA-5 |
| F7 | QA-F7 | Item fails clean gate: Quarantine field-fail; not clean; Accept disabled | A11, F9, F33 | |
| F8 | QA-F8 | Item passes fields but needs Fate: operator-hold; Accept promotes only if field gate still passes; Accept does not edit or fill. Operator item outlet not on allowlist is a named path | A11, F9, F12 | CR-QA-8 |
| F9 | QA-F9 | Accept on field-fail: refused; item stays quarantined; failed rule stays visible | A11, F7 | |
| F10 | QA-F10 | Discard then incremental same locator unchanged content: does not reappear as clean | A11, R-UI-17 | |
| F11 | QA-F11 | written_social lookalike (Operator item pin match lookalike, or a public mismatch): quarantined, not clean | A18, A31, F31, F45, S4 | CR-QA-7 |
| F12 | QA-F12 | Interview outlet not on allowlist (Operator item outlet off-list, or allowlist empty): not clean; empty shows blocked: empty allowlist; empty jobs do not make it fresh | A13, F46 | CR-QA-8 |
| F13 | QA-F13 | Extract tag not on topic or occasion list: quarantined; list is not auto-grown | R-UI-18, section 5.3 | |
| F14 | QA-F14 | Same locator run twice: same record_id; unchanged or new text_version; no second current id | F15, A9 | |
| F15 | QA-F15 | Force re-fetch: new raw artifact; may new text_version on same id; prior version stays resolvable | F14, A9, A17 | |
| F16 | QA-F16 | Topic × counted channel is thin: Dashboard not-ready with failed thin clause; not a healthier third rank; no venue | A14, A35, F48 | CR-QA-11 |
| F17 | QA-F17 | Every covering source in the S8 set for that counted channel is cadence-stale: Dashboard not-ready; sources not hidden; exempt ignored | A20, F34, S8 | |
| F18 | QA-F18 | Books row: channel = other; mention_usable = false; filter value other; never written_other | A15, A21 | |
| F19 | QA-F19 | In-place clean-text edit control absent on every screen and named overlay | A9, A15 | |
| F20 | QA-F20 | Side picker, call, ledger, confidence, place-a-call, venue picker absent on every screen | A15 | |
| F21 | QA-F21 | Delete the base: typed confirm required; Cancel leaves the base. Typed DELETE is not restart | R-UI-11, ov-delete, F40 | CR-QA-2 |
| F22 | QA-F22 | Delete clean records: confirm required | R-UI-11 | |
| F23 | QA-F23 | Manual Run of a disabled source: confirm required; next run remains exact copy `not scheduled`; scheduler does not enqueue | A8, F37, CR-E2 | |
| F24 | QA-F24 | Global re_index or refresh_preferences: confirm required; same global write lock as global re_extract | A5b, F3, F4 | |
| F25 | QA-F25 | Job-level network/auth/parse via Connector: failed, readable error exactly network or auth or parse, no silent retry loop; S6 applies | F5, A7, A29, F43 | CR-QA-5 |
| F26 | QA-F26 | Source not on the configured list: job cannot target it; adding a source is not a job side effect | section 5.3, section 5.4 | |
| F27 | QA-F27 | Legal item whose named party is only the administration (Operator item named_party the administration): not ingested as legal clean | A32, F46, section 2, section 5.4 | CR-QA-8 |
| F28 | QA-F28 | A section 6 read action cannot run because Records reads is down: that Records control shows its cannot-run copy; app does not invent records | A17, A27, F41 | CR-QA-3 |
| F29 | QA-F29 | Load error on a screen induced by Fail next load: inline error + Retry; data already shown stays until replaced | A28, F42 | CR-QA-4 |
| F30 | QA-F30 | Filter matches nothing: empty copy; no marketing illustration. Topic empty copy only when the topic list is empty | Records/Jobs/Quarantine/Dashboard empty copy, A35 | CR-QA-11 |
| F31 | QA-F31 | Empty official X pin or empty official Truth Social pin (Empty Save): blocked: empty pin; no clean written_social; fetched items field-fail (pin required); freshness does not move; empty pin is not match-all. written_social Operator item refused if no pin | A18, F11, F50, S4, CR-E1 | CR-QA-7 |
| F32 | QA-F32 | failed/cancelled/worker_lost after some clean writes: stayed clean resolvable under that job id; in-flight quarantined/job_stopped, absent from clean and index; counts add up (S9) | A12, A22, F5, F35 | |
| F33 | QA-F33 | Write whose (kind, channel) is not in the S7 set for that source, including Operator item off-S7: field-fail; not clean | A19, A30, F44, S7 | CR-QA-6 |
| F34 | QA-F34 | books or legal cadence-stale for not-ready: they never participate; spoken not-ready-from-stale uses only the S8 spoken covering set | A20, A21, F17, S8 | |
| F35 | QA-F35 | In-flight item with no other gate fail when the job stops: field-fail job_stopped; counts as quarantined; Accept disabled; not a silent drop | A22, F32, S6, S9 | |
| F36 | QA-F36 | Restart after disable persists; empty first boot is not this case | A23, A16, CR-E1, A39 | CR-QA-2, CR-USER-1 |
| F37 | QA-F37 | CR-E2. books or legal next scheduled run, or a disabled source: exact copy `not scheduled`; scheduler does not enqueue them; Manual Run remains | A8, A21, A24, F23, CR-E2 | CR-QA-10 |
| F38 | QA-F38 | Fate chooses Stop worker while a job is running: ov-worker-stop. Confirm applies S5. Pill not available. Banner. Stored failed / worker_lost. No running row | A12, A25, F1, F39 | CR-QA-1 |
| F39 | QA-F39 | Fate chooses Start worker: pill available. Banner gone. worker_lost jobs are not resumed. Next queued job may run | A12, A25, F1, F38 | CR-QA-1 |
| F40 | QA-F40 | Fate chooses Restart the app: ov-restart. Confirm applies S5, then instance returns with same record_id values and same enable/disable, topics, pins, and allowlist. Worker available. Typed DELETE is not this path | A16, A26, A33 | CR-QA-2 |
| F41 | QA-F41 | Records reads is down: each section 6 control shows its cannot-run copy. No invented records | A17, A27, F28 | CR-QA-3 |
| F42 | QA-F42 | Fail next load is set for a screen, then Fate opens that screen: `{Screen} failed to load` plus Retry. Retry loads and clears the fail | A28, F29 | CR-QA-4 |
| F43 | QA-F43 | Connector is network, auth, or parse on a source, then a worker executes a fetch job for that source: job stored failed with that exact readable error. S6. No silent retry loop. Setting back to ok does not resume | A29, F25 | CR-QA-5 |
| F44 | QA-F44 | Operator item (kind, channel) is not in the S7 set for that source: field-fail F33. Not clean. fetched = 1 | A19, A30, F33 | CR-QA-6 |
| F45 | QA-F45 | Operator item pin match lookalike on truth_social or x_personal with a set pin: F11. Quarantined, not clean | A31, F11 | CR-QA-7 |
| F46 | QA-F46 | Operator item named_party is the administration: F27. Not ingested as legal clean | A32, F27 | CR-QA-8 |
| F47 | QA-F47 | Probe clock is Saturday or Sunday: next-run Monday 09:00 ET. Scheduler does not enqueue | A24, A34, F51 | CR-QA-10, S11 |
| F48 | QA-F48 | Fate Adds a topic while the counted-channel table is empty of rows: one spoken row and one written_social row appear immediately, usable 0, not-ready, failed clause zero usable. Ingest is not required | A14, A35, F16 | CR-QA-11 |
| F49 | QA-F49 | Targeted Operator item missing source, locator, text, kind, or channel: refused in place. Copy `Operator item needs source, locator, text, kind, and channel.` No job row. Not F2 | A4, A36, A37, F2 | S10 |
| F50 | QA-F50 | Targeted Operator item written_social, or source truth_social / x_personal, with no pin set: refused in place. Copy `A written_social Operator item is refused if no pin is set.` No job row. Not F2 | A18, A31, F31 | CR-QA-7, S10 |
| F51 | QA-F51 | Probe clock Set to a weekday 09:00 ET instant: tick: enqueue incremental once for each enabled non-exempt source due that day, then advance next-run. Remaining frozen on that instant does not enqueue again | A34, A24, F47 | CR-QA-10, S11 |
| F52 | QA-F52 | Would-be legal item with named_party absent: field-fail. Not clean. Not a silent drop. Operator can read named_party on clean legal via ov-record, GetRecord, and Export | A9, A10, A38 | S12, CR-QA-8 |
| F53 | QA-F53 | wipe/return-to-empty absent; Restart not a wipe; typed DELETE is not factory-empty go-live | A39, A23, F21, F36 | CR-USER-1 |

Matrix A/F IDs present: A1, A2, A3, A4, A5, A5b, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15, A16, A17, A18, A19, A20, A21, A22, A23, A24, A25, A26, A27, A28, A29, A30, A31, A32, A33, A34, A35, A36, A37, A38, A39, F1 through F53 inclusive.

### 3.2 CR-QA and named-hole rows

Each CR-QA, CR-USER-1, and each of S10, S11, S12 has a dedicated check id. Primary A/F checks still exist and are not collapsed into these rows.

| Named ID | Dedicated check | Primary A/F checks | One-line expected |
| --- | --- | --- | --- |
| CR-QA-1 | QA-CR-QA-1 | QA-A12, QA-A25, QA-F1, QA-F38, QA-F39 | Stop worker / Start worker. ov-worker-stop copy `Stop the worker? Running jobs will fail with worker_lost.` Confirm applies S5 immediately. A switch that only paints not available is a fail |
| CR-QA-2 | QA-CR-QA-2 | QA-A16, QA-A26, QA-F40 | Control Sources danger Restart the app. ov-restart copy `Restart the app? The knowledge base stays. Running jobs fail with worker_lost.` Confirm applies S5 then instance returns with worker available, same KB, same record_ids, Fate enable/disable/topics/occasions/pins/allowlist. Typed DELETE is not restart. Restart the app is not a wipe |
| CR-QA-3 | QA-CR-QA-3 | QA-A17, QA-A27, QA-F28, QA-F41 | Control Operator tab Records reads available\|down. Copy: `Search cannot run.` `GetRecord cannot run.` `GetPreference cannot run.` `Export cannot run.` |
| CR-QA-4 | QA-CR-QA-4 | QA-A28, QA-F29, QA-F42 | Fail next load: choice Dashboard/Control/Records/Quarantine + Set. Next open `{Screen} failed to load` plus Retry. Retry loads and clears |
| CR-QA-5 | QA-CR-QA-5 | QA-A29, QA-F25, QA-F43 | Connector ok\|network\|auth\|parse on each source row. Next fetch job worker executes, if not ok, stored failed with exact error network\|auth\|parse. S6. No silent retry. Setting back to ok does not resume. Fetch nothing while ok is succeeded_empty |
| CR-QA-6 | QA-CR-QA-6 | QA-A19, QA-A30, QA-F33, QA-F44 | Targeted modes Query vs Operator item. Off-S7: Operator item source whitehouse_remarks, kind social, channel written_social is field-fail F33 not clean. fetched=1 |
| CR-QA-7 | QA-CR-QA-7 | QA-A18, QA-A31, QA-F11, QA-F31, QA-F45, QA-F50 | Pin Save + lookalike. Empty Save is F31. Operator item truth_social/x_personal pin match match\|lookalike. lookalike is F11. written_social or those sources refused if no pin. Not F2 |
| CR-QA-8 | QA-CR-QA-8 | QA-A32, QA-A38, QA-F12, QA-F27, QA-F46, QA-F52 | named_party Donald Trump required on legal; absence field-fail. Operator item named_party the administration is F27. outlet not on allowlist is F12. Add/Remove allowlist |
| CR-QA-9 | QA-CR-QA-9 | QA-A33, QA-A16 | No UTC on screens. After Restart, same record_ids and same ET instants. No UTC column |
| CR-QA-10 | QA-CR-QA-10 | QA-A24, QA-A34, QA-F37, QA-F47, QA-F51 | Probe clock. Empty = wall clock ET. Set datetime ET. Clear probe clock. Display of next-run is not a tick. S11 tick is Set to weekday 09:00 ET |
| CR-QA-11 | QA-CR-QA-11 | QA-A14, QA-A35, QA-F16, QA-F48 | Add topic: empty copy only when topic list empty. After Add, one row per counted channel immediately, usable 0, not-ready, failed clause `zero usable`. Ingest not required. Removing last topic returns empty copy |
| CR-USER-1 | QA-CR-USER-1 | QA-A23, QA-A39, QA-F36, QA-F53 | Empty first-boot observation is out of scope and is not a go-live requirement. No operator wipe. Quality shall not obtain or invent an empty first boot. Remaining CR-E1: no first-run wizard on the current instance; enabled independent of blocked; Fate’s disable/enable persists across Restart the app; factory is not reapplied on restart of a non-empty instance |
| S10 | QA-S10 | QA-A4, QA-A36, QA-A37, QA-F2, QA-F49 | Query-only targeted require. Operator item required fields source, locator, text, kind, channel. Missing any: Operator item copy. Not F2. Query empty topic/query/occasion still F2/A4. A36: Operator item with those three empty and five required filled creates a job |
| S11 | QA-S11 | QA-A34, QA-F51, QA-F47 | Probe-clock 09:00 tick: enqueue incremental once for each enabled non-exempt source due that day, then advance next-run. Remaining frozen does not enqueue again. Weekday before 09:00 does not enqueue. Saturday/Sunday never enqueue |
| S12 | QA-S12 | QA-A9, QA-A10, QA-A38, QA-F52 | named_party on ov-record when kind legal (read-only), GetRecord, Export (empty on non-legal). Absence on a would-be legal item is field-fail, not a silent drop |

CR-QA IDs present: CR-QA-1, CR-QA-2, CR-QA-3, CR-QA-4, CR-QA-5, CR-QA-6, CR-QA-7, CR-QA-8, CR-QA-9, CR-QA-10, CR-QA-11. CR-USER-1 present: QA-CR-USER-1. Named holes present: S10, S11, S12. Total dedicated checks = 108.

---

## 4. Executable checks

Checks are operator-visible on Dashboard, Control, Records, Quarantine, named overlays, and section 6 read actions, or by observing stored status, job counts, banners, and record fields the Spec names.

**Shared Spec facts used by many checks (do not invent):**

- Count equation (S9): `fetched = written + updated + unchanged + quarantined + fetch_fail`. No sixth term. In-flight with no other gate fail is quarantined as field-fail `job_stopped`. `written` and `updated` are the S6 stayed set only. ov-job shows the equation and counts `fetched`, `written`, `updated`, `unchanged`, `quarantined`, `fetch fail`.
- S6 commit on stop (`failed` / `cancelled` / `worker_lost`): stayed clean remain under that job id; in-flight not clean; index equals stayed set; that job id writes nothing further; earlier `succeeded` jobs’ records stay.
- S5 worker down: banner every screen; stored `running` becomes `failed` with readable error `worker_lost`; display matches stored status; new Run creates `queued`; no running; mutex released for `failed`; a `queued` job still occupies the mutex; returning worker does not resume; retry is new job id. Packet copy that displayed `running` as `queued` is struck by Spec section 5.1. Encode section 5.1. Stop worker (`#worker-stop`) / Start worker (`#worker-start`) is the operator path (CR-QA-1). A switch that only paints `not available` and does not apply S5 is a fail.
- Write mutex (S2 / R-JOB-9): per source. Write-scoped: `incremental`, `backfill`, `targeted` (including Operator item), source-scoped `re_extract`. Global `re_extract` / `re_index` / `refresh_preferences` occupy every source. Second write-scoped job: queue-behind or don’t-start. No third job (F4). Packet leftover “Global jobs are not this mutex” is struck by section 5–7 / A5b.
- Display timezone America/New_York; stored times UTC; operator view never raw UTC; clock labeled `ET`. No UTC column on any operator screen (CR-QA-9).
- Job types: `incremental`, `backfill`, `targeted`, `re_extract`, `re_index`, `refresh_preferences`. Targeted has two modes: **Query** and **Operator item** (`#targeted-mode`). Query-only targeted require is S10. Operator item is write-scoped.
- Channels closed: `spoken` | `written_social` | `written_official` | `legal` | `other`. Never `written_other`. Books are `other`. Books `mention_usable = false`.
- Clean record fields closed: `record_id`, `kind`, `title`, `event_time`, `published_time`, `text`, `text_version`, `text_hash`, `completeness`, `url`, `source`, `occasion`, `audience`, `delivery`, `channel`, `topics`, `people`, `phrases`, `term`, `mention_usable`, `decision_usable`, `named_party`. No `confidence` field. No venue object. Leftover section 6 list without `named_party` is struck; S12 wins.
- Eleven sources: `whitehouse_remarks`, `whitehouse_actions`, `app`, `factbase`, `federal_register`, `truth_social`, `x_personal`, `campaign`, `books`, `interviews`, `legal`.
- S7 legal `(kind, channel)` per source is closed. A write whose pair is not in the set is field-fail, not clean. Operator item is the Spec path to command an off-S7 pair.
- S8 covering sources: `spoken` covering is `whitehouse_remarks`, `app`, `factbase`, `campaign`, `interviews`. `written_social` covering is `truth_social`, `x_personal`. `whitehouse_actions`, `federal_register`, `books`, and `legal` do not cover a counted channel. Cadence: daily for `truth_social`, `x_personal`, `whitehouse_remarks`, `whitehouse_actions`, `interviews`; weekly for `app`, `factbase`, `federal_register`, `campaign`; none (exempt) for `books`, `legal`.
- CR-E1 / CR-USER-1: Observing first boot of an empty instance is out of scope and is not a go-live requirement. There is no operator wipe and no control that returns a used instance to empty first boot. On the current instance there is no first-run wizard. `enabled` is independent of `blocked`: `interviews` still shows `blocked: empty allowlist` when the allowlist is empty; `x_personal` and `truth_social` still show `blocked: empty pin` while those pins are empty. A blocked reason does not force `disabled`. Fate’s disable/enable persists across Restart the app. Factory is not reapplied on restart of a non-empty instance. Quality shall not obtain or invent an empty first boot. Typed DELETE of the base is not first-boot and is not a go-live path to factory-empty first boot.
- CR-E2 default schedule clock: 09:00 America/New_York only. No other hour. No operator-added schedule. No cron builder. Daily: next weekday 09:00 ET that is not in the past. Weekly: next Monday 09:00 ET that is not in the past. Saturday and Sunday never receive a scheduled run. Exempt `books` and `legal`: exact copy `not scheduled`. Disabled source: exact copy `not scheduled`, even if it has a cadence. Display of `next scheduled run` is that datetime in America/New_York, or the exact copy `not scheduled`. Closed two-value display. Packet `scheduler skip` as next-run copy is struck. Display of next-run is not a scheduler tick. S11 tick is Probe clock Set to a weekday 09:00 ET instant.
- Production: one Fate-operated instance. Four chrome screens only: Dashboard, Control, Records, Quarantine. Control inner tabs: `Run job` | `Jobs` | `Sources` | `Vocabularies` | `Operator`. Operator is not a fifth chrome screen. Section 6 four read actions on Records: `Search`, `GetRecord`, `GetPreference`, `ExportRetrievalSet`.
- Named overlays: `ov-run`, `ov-disabled`, `ov-reindex`, `ov-refresh`, `ov-delete`, `ov-dup`, `ov-job`, `ov-record`, `ov-q-fieldfail`, `ov-q-hold`, `ov-worker-stop`, `ov-restart`.
- Named operator controls: `#worker-stop`, `#worker-start`, `#btn-restart`, `#tab-operator`, `#records-reads`, `#fail-next-load`, `#fail-next-load-set`, `#probe-clock`, `#probe-clock-set`, `#probe-clock-clear`, `#connector-{source}`, `#pin-x-save`, `#pin-ts-save`, `#allowlist-add`, `#targeted-mode`, `#named-party-page`, `#pin-match-page`, `#rec-named-party`.
- Copy bank (exact, from Spec section 14 and CR-QA blocks):
  - Worker available: `available`
  - Worker down banner: `Worker not available. New jobs sit queued. Nothing is executing.`
  - Stop worker confirm: `Stop the worker? Running jobs will fail with worker_lost.`
  - Start worker: `Start worker`
  - Restart the app: `Restart the app? The knowledge base stays. Running jobs fail with worker_lost.`
  - Records reads down: `Search cannot run.` `GetRecord cannot run.` `GetPreference cannot run.` `Export cannot run.`
  - Load error: `{Screen} failed to load` plus Retry.
  - Operator item missing required: `Operator item needs source, locator, text, kind, and channel.`
  - Pin refuse: `A written_social Operator item is refused if no pin is set.`
  - Query targeted require: `Targeted needs a topic, query, or occasion.`
  - Topic row before ingest failed clause: `zero usable`
  - Empty topic table: `No topic × channel rows. Add topics in Control → Vocabularies, then ingest.`
  - Connector values: `ok` `network` `auth` `parse`
  - Cancel confirm: `Cancel job {id}? Clean records already written stay. In-flight items go to quarantine as job_stopped.`
  - Cancel toast: `Job cancelled. Stayed clean remain. In-flight quarantined as job_stopped.`
  - Interviews blocked: `blocked: empty allowlist`
  - Empty pin blocked: `blocked: empty pin`
  - Thin raw column header: `raw clean (NOT the bar)`
  - Field-fail accept helper: `Cannot accept. Fix source or extract, then run a new job.`
  - Discard helper: `Discarded items shall not reappear as clean on the next incremental run unless source content or locator changed, or Fate force re-fetches.`
  - Duplicate don’t-start: `Rejected: a job for this source is already queued or running (job {id}). A second job would write the same source.`
  - Queue behind: `Queued behind job {id} (same source). It will not run until that job leaves queued or running.`
  - Third write-scoped job: `Rejected: source {source} already has a queued job waiting behind {id}.`
  - Waiting reason: `waiting: same source as {id}`
  - Force re-fetch label: `Force re-fetch — pull new raw artifacts; may write a new text_version (R-JOB-13)`
  - Export button: `Export retrieval set`
  - Base delete prompt: `This deletes the clean base. Type DELETE to confirm.`
  - Counted-channel footnote: `Counted channels are spoken and written_social. Spoken covering: whitehouse_remarks, app, factbase, campaign, interviews. books and legal are exempt. This table is not a venue picker.`
  - Stopped-job helper: `written + updated = stayed clean. quarantined includes job_stopped. fetched = written + updated + unchanged + quarantined + fetch_fail.`
  - job_stopped accept helper: `Cannot accept. A later job for this locator may write clean if it then passes the gate. That later clean write is not also an open job_stopped item.`
  - Correction helper: `Clean text is not editable. Fix source config or re-ingest / re-extract.`
  - Pin helper: `Clean written_social attribution must match these pins. A lookalike is quarantined.`
  - Allowlist helper: `Empty allowlist blocks the interviews source. Empty jobs do not make it fresh.`
  - Worker-down Run helper: `Worker not available. This job will sit queued until a worker executes it.`

**Standard on-fail (every check):** If specified observable is missing or wrong: Defect (Engineer). If the run exposes a hole the Spec did not close: Change Request (Spec). Do not treat unspecified behavior as pass.

**Induction note:** Spec v8 names operator controls for CR-QA-1 through CR-QA-11. Use those controls. Do not leave a public-item mint as an open hole when Operator item is the Spec path. Empty first-boot observation is out of scope (CR-USER-1). QA-A23 is the current instance. Typed DELETE is not first-boot, is not a wipe control, and is not a fail of QA-A39 / QA-F53. Do not invent a wipe. Do not invent hosting, stack, or unstated controls. A missing branch is not a pass.

---

### 4.1 Acceptance checks

#### QA-A1

1. **ID:** QA-A1 (ship-gate)
2. **Spec trace:** A1; section 0 Done-when; section 7 R-UI-1, R-UI-2, R-UI-3, R-UI-4, R-UI-5, R-UI-6; section 5.6 counted channels `spoken`, `written_social`; section 8 Dashboard layout (absorbs UI; section 5–7 win on conflict); CR-QA-1 chrome Stop worker / Start worker
3. **Preconditions:** Fate is the operator on the one production instance. No job is `running` (job snapshot Running is `0`).
4. **Steps:**
   1. Open Dashboard (`screen-dashboard`) without opening a job.
   2. Read chrome: product name, worker pill, Stop worker (`#worker-stop`) while `available` or Start worker (`#worker-start`) while `not available`, quarantine badge, four nav items, clock.
   3. Read Strip A kind tiles and Newest clean record.
   4. Read Strip B job snapshot, quarantine split, family coverage flags.
   5. Read source health table: one row per source id. Confirm no source is hidden for stale, disabled, blocked, or empty.
   6. Read topic × counted channel table: health pills and columns. Confirm no venue column.
5. **Expected observable:**
   - Chrome: `PTRP`; worker pill `available` or `not available`; Stop worker or Start worker as matching the pill; quarantine badge integer; nav Dashboard / Control / Records / Quarantine; clock current time in ET labeled `ET`. No UTC timestamp.
   - Strip A: seven kind tiles `remark` · `decision` · `writing` · `interview` · `social` · `legal` · `staffing` with counts (zero is shown). `Newest clean record` + ET timestamp, or `Newest clean record: none` if empty.
   - Strip B: Queued / Running / Failed counts. Running is `0`. Quarantine split `field-fail N` · `operator-hold N`. Family flags remarks / decisions / writings as `gap` or `present`. Binding: remarks = clean `remark` + `interview`; decisions = clean `decision` + `legal` + `staffing`; writings = clean `writing` + `social`.
   - Source health (every source listed, none hidden): `whitehouse_remarks`, `whitehouse_actions`, `app`, `factbase`, `federal_register`, `truth_social`, `x_personal`, `campaign`, `books`, `interviews`, `legal`. Columns: enabled/disabled, last `succeeded` (fetched > 0) ET or `never`, last `succeeded_empty` ET or `none`, freshness (cadence-age + 24h wall-clock age with badges if true; exempt `books` and `legal` show `no cadence` and no 24h badge), clean-record count, last error or `—`, blocked reason if any.
   - Topic × counted channel: counted channels `spoken` and `written_social` only. Health `ready` or `not-ready` only. Column `raw clean (NOT the bar)`. Footnote exact copy: `Counted channels are spoken and written_social. Spoken covering: whitehouse_remarks, app, factbase, campaign, interviews. books and legal are exempt. This table is not a venue picker.` No venue column. Two channels are not collapsed into one topic row. Empty copy `No topic × channel rows. Add topics in Control → Vocabularies, then ingest.` appears only when the topic list is empty (CR-QA-11).
6. **Pass / fail:** Pass if all of the above are present and health is only `ready`/`not-ready`. Fail if a required strip/table/pill is missing, a third health rank appears, a venue column/picker is present, Stop worker / Start worker is missing from chrome, or a UTC timestamp appears.
7. **On fail:** Defect (Engineer) for missing/wrong specified UI. Change Request (Spec) if a displayed control has no Spec name.

#### QA-A2

1. **ID:** QA-A2 (ship-gate)
2. **Spec trace:** A2; section 5.5 `incremental`; statuses `queued` → `running` → `succeeded` | `succeeded_empty` | `failed` | `cancelled`; R-UI-7; R-JOB-6
3. **Preconditions:** Fate. At least one source `enabled`. Worker pill `available` (the `running` to terminal segment requires a worker executing the job). If worker is `not available`, do not call queued-only a pass of A2; that state is QA-F1 / QA-A12. Connector for that source is `ok`.
4. **Steps:**
   1. Control, Run job (`#tab-run` / `ov-run`).
   2. Type `incremental`. Source = one enabled source. Force re-fetch default off. Run.
   3. Control, Jobs: find the new row (id, type `incremental`, source, `triggered_by` `user`).
   4. Watch status until terminal. Open the job (`ov-job`). Confirm stored status matches the list pill.
5. **Expected observable:** Job appears. Status moves `queued` → `running` → a terminal status (`succeeded` | `succeeded_empty` | `failed` | `cancelled`) when a worker executes it. Stored status in `ov-job` matches display. Nothing is shown as `running` before a worker is actually executing it. Fate shall not have to run a source outside the app.
6. **Pass / fail:** Pass if the job appears and the status path matches when the worker executes. Fail if the job does not appear, skips `queued`, is shown `running` with no worker, or never reaches a specified terminal status while worker is available.
7. **On fail:** Defect (Engineer). If worker availability cannot be observed as `available` and the job never leaves `queued`, do not pass A2; route worker-down to QA-F1 (specified). Use Start worker (`#worker-start`) if the pill is `not available` and then continue A2; do not invent a pass.

#### QA-A3

1. **ID:** QA-A3 (ship-gate)
2. **Spec trace:** A3; R-UI-9; section 5.1 S9; section 5.5 job stores; ov-job counts
3. **Preconditions:** The job from QA-A2 exists (or any fetch job Fate started).
4. **Steps:**
   1. Control, Jobs. Open that job (`ov-job`).
   2. Read header (id, type, source, status pill, `triggered_by`), params, times, counts, error, log, artifacts, clean records, quarantine links.
   3. On a finished fetch job, add the counts and compare to `fetched`. Confirm the equation is shown.
   4. Confirm stored status matches the status pill.
   5. If the job is terminal after a stop (`failed`/`cancelled`/`worker_lost`), open Quarantine links from this job and confirm in-flight items are in `quarantined` with `job_stopped` where S6 applied.
5. **Expected observable:**
   - Params (including force re-fetch flag and window if any; Operator item fields if that was the job).
   - Stored status; display matches.
   - Log: live if `queued`/`running`; completed if terminal.
   - Counts: `fetched`, `written`, `updated`, `unchanged`, `quarantined`, `fetch fail`. Equation shown: `fetched = written + updated + unchanged + quarantined + fetch_fail`. No sixth term. On stop, in-flight is in `quarantined`. Stopped-job helper: `written + updated = stayed clean. quarantined includes job_stopped. fetched = written + updated + unchanged + quarantined + fetch_fail.`
   - Error readable or `—`.
   - Links to artifacts / clean writes or updates / quarantined items from that job.
   - Times shown ET, not raw UTC in the operator view.
6. **Pass / fail:** Pass if every named block is present and the equation holds on a finished fetch job. Fail if counts do not add up, equation missing, stored status mismatches display, in-flight is absent from `quarantined` on stop, or a UTC timestamp appears.
7. **On fail:** Defect (Engineer) for specified mismatch. Change Request (Spec) if a count label exists that the Spec does not name (extra sixth term).

#### QA-A4

1. **ID:** QA-A4
2. **Spec trace:** A4; F2; S10; section 5.5 `backfill` requires a date window; targeted **Query** requires a topic, query, or occasion; Control validation copy. Does not apply to Operator item.
3. **Preconditions:** Fate on Control, Run job. No need for an existing job.
4. **Steps:**
   1. Type `backfill`. Pick a source. Leave date window start/end empty. Run.
   2. Observe inline error. Control, Jobs: confirm no new row.
   3. Type `targeted`. Mode **Query** (`#targeted-mode`). Pick a source. Leave topic, query, and occasion all empty. Run.
   4. Observe inline error. Confirm no new job row.
   5. Do not treat Operator item with those three empty as this check. That is QA-A36. Dedicated Operator item missing-required is QA-A37 / QA-F49.
5. **Expected observable:** Run refused in place. Copy: `Backfill needs a date window.` and `Targeted needs a topic, query, or occasion.` No queued row appears. Query-only targeted require applies only to mode Query (S10).
6. **Pass / fail:** Pass if both Query-path refusals occur and no job is created. Fail if a job row appears, the refuse copy/control is absent, or Operator item is refused with the Query copy.
7. **On fail:** Defect (Engineer).

#### QA-A5

1. **ID:** QA-A5
2. **Spec trace:** A5; R-JOB-9; F3; `ov-dup`; chrome copy bank
3. **Preconditions:** Fate. Worker available enough that a write-scoped job for `truth_social` can be `running` (or remain `queued`/`running` as occupant). `truth_social` is a configured source. Official Truth Social pin is set if the occupant is a fetch that would otherwise refuse.
4. **Steps:**
   1. Start a write-scoped job for `truth_social` (`incremental`, `backfill`, `targeted` Query or Operator item, or source-scoped `re_extract`) so it is `running`.
   2. Start another write-scoped job for `truth_social`.
   3. On `ov-dup`, read named blocking job id, type, and source.
   4. Choose Don’t start. Observe toast. Confirm no new job.
   5. Start the second job again. Choose Queue behind. Observe toast and Jobs list.
   6. Confirm the queued-behind job does not become `running` until the first leaves `queued`/`running`.
5. **Expected observable:**
   - Overlay `ov-dup` (not a silent start).
   - Don’t start: no new job. Toast: `Rejected: a job for this source is already queued or running (job {id}). A second job would write the same source.`
   - Queue behind: new job `queued` with reason `waiting: same source as {id}`. Toast: `Queued behind job {id} (same source). It will not run until that job leaves queued or running.`
   - Queued-behind job does not run until the first leaves `queued`/`running`. Incremental and backfill must not write the same source at once. Operator item is write-scoped; same-source mutex applies. A skip of `ov-dup` on Operator item is a fail.
6. **Pass / fail:** Pass if overlay, both choices, copy, and wait behavior match. Fail if a second job runs concurrently, overlay is skipped, or Don’t start still creates a job.
7. **On fail:** Defect (Engineer).

#### QA-A5b

1. **ID:** QA-A5b
2. **Spec trace:** A5b; section 5.5 global `re_extract` write-scoped against every source; R-JOB-9; F3; F24. Packet leftover “Global jobs are not this mutex” is struck.
3. **Preconditions:** A source write-scoped job is `running` for any one source. Fate.
4. **Steps:**
   1. Control, Run job. Type `re_extract`. Source = `global`. Run.
   2. Observe `ov-dup` (same overlay class as QA-A5).
   3. Choose Don’t start. Confirm no job created.
   4. Repeat. Choose Queue behind.
   5. Observe the global job stays `queued` until every touched source is free (the running source write job leaves `queued`/`running`).
5. **Expected observable:** Same overlay. Don’t-start creates no job. Queue-behind waits until every touched source is free. Global `re_extract` occupies every source. Packet leftover “Global jobs are not this mutex” is struck.
6. **Pass / fail:** Pass if overlay and wait-until-every-touched-source-is-free hold. Fail if global `re_extract` starts writing while any source write job is `queued` or `running`, if Don’t-start creates a job, or if the product treats global jobs as outside this mutex.
7. **On fail:** Defect (Engineer).

#### QA-A6

1. **ID:** QA-A6
2. **Spec trace:** A6; R-JOB-7; section 5.1 S6; section 5.2 Row actions; section 5.5 Fate can cancel `queued` or `running`; section 8 copy bank; F5; F32; F35. Q1 cancel copy remains.
3. **Preconditions:** A job in `queued` or `running`. Prefer a `running` fetch that has already written some clean records if such a job exists (also covers stayed set). A `queued` cancel is valid for the terminal-status half.
4. **Steps:**
   1. Control, Jobs. Cancel on the `queued` or `running` row. The confirm dialog copy must be exactly `Cancel job {id}? Clean records already written stay. In-flight items go to quarantine as job_stopped.` This check does not require, and fails on, `Cancel job {id}? Queued/running work from this job will not commit new clean records.`
   2. Confirm Cancel. The toast copy must be exactly `Job cancelled. Stayed clean remain. In-flight quarantined as job_stopped.`
   3. Open `ov-job`. Read stored status, counts, equation.
   4. Records Search: stayed clean records written under that job id still resolve; producing job is that id.
   5. Quarantine: in-flight items from that job are field-fail `job_stopped`; they do not appear as clean in Records Search (index equals stayed set). Accept disabled on those items.
   6. Observe: no further clean records, index rows, or preference rows appear with that job id as producer.
   7. Confirm clean records from earlier `succeeded` jobs still resolve.
5. **Expected observable:** Confirm copy is the Spec R-JOB-7 string `Cancel job {id}? Clean records already written stay. In-flight items go to quarantine as job_stopped.` Toast is `Job cancelled. Stayed clean remain. In-flight quarantined as job_stopped.` Status `cancelled` (terminal). Cancel disabled after terminal. S6: stayed clean remain under that job id; in-flight not clean (quarantined `job_stopped`); index equals stayed set; that job id writes nothing further; earlier succeeded records stay. Counts add up (S9). Accept disabled on `job_stopped` items. No never-committed bucket.
6. **Pass / fail:** Pass if confirm copy, toast copy, and all S6 observables hold. Fail if confirm or toast uses `will not commit new clean records` or any other non-Spec copy, if in-flight became clean, if stayed clean vanished, if index contains quarantined items, or if the job keeps writing after leaving `running`.
7. **On fail:** Defect (Engineer).

#### QA-A7

1. **ID:** QA-A7
2. **Spec trace:** A7; section 5.5 Retry creates a new job id with the same params and a pointer to the failed job; history kept; Retry on `failed` only; R-JOB-9 still applies
3. **Preconditions:** A job in `failed` (from a real fail, Connector fail, or `worker_lost`). Fate.
4. **Steps:**
   1. Control, Jobs. Retry enabled only on `failed`.
   2. Retry. If `ov-dup` appears (mutex), that is F3 — complete Don’t start or Queue behind as specified; this check still requires that a successful Retry creates a new id.
   3. Open the new job and the old job.
5. **Expected observable:** New job id. Same params. Pointer: new job `retry of {failed_job_id}`; failed job `retried as {new_id}` once retried. Failed job remains in history (append-only). `triggered_by` `retry` on the new job. Retry does not delete the failed job.
6. **Pass / fail:** Pass if new id, same params, pointer, history kept. Fail if retry mutates/deletes the failed job, reuses the same id, or Retry is offered on non-`failed`.
7. **On fail:** Defect (Engineer).

#### QA-A8

1. **ID:** QA-A8
2. **Spec trace:** A8; CR-E2; R-UI-12; F23; F37; `ov-disabled`; section 5.6 Default schedule clock; section 5.4 A disabled source is not enqueued by the scheduler
3. **Preconditions:** Fate. A source that has a cadence (not `books`/`legal` exempt). Currently `enabled`. Chrome clock shows America/New_York. Prefer a daily source and a weekly source in turn so cadence does not hide the disable copy. Probe clock may be used to fix now (CR-QA-10); display of next-run is not a tick.
4. **Steps:**
   1. Control, Sources. Read Next scheduled run while the source is `enabled`: it is a datetime in America/New_York at 09:00 ET per CR-E2, not `not scheduled`. Cadence display is read-only. There is no cron builder and no operator-added schedule control.
   2. Disable that source. No extra confirm on disable/enable.
   3. Read Next scheduled run for that row: exact copy `not scheduled`. Not `scheduler skip`. Not a leftover 09:00 datetime. This holds even though the source has a cadence.
   4. Dashboard source health: that source remains listed, `disabled`. Do not require a next-run token other than the closed Control copy `not scheduled`. Packet `scheduler skip` as next-run copy is struck by section 5–7.
   5. Do not require waiting for a schedule tick if next-run already reads `not scheduled` (Spec allows inspect next-run). If a schedule tick is observed (Probe clock Set to weekday 09:00 ET per S11), the scheduler does not enqueue `incremental` for that disabled source.
   6. Run job `incremental` for that disabled source. Overlay `ov-disabled` copy: `This source is disabled. Scheduler will not run it. Manual Run still enqueues. Continue?`
   7. Cancel the confirm: no job. Confirm: job may enqueue (then R-JOB-9 if applicable). Manual Run never waits for the schedule.
5. **Expected observable:** Next run is the exact copy `not scheduled`. Closed two-value display elsewhere in this plan still applies: datetime in America/New_York, or `not scheduled`. A disabled source uses `not scheduled` even if it has a cadence. Manual Run still possible after confirm. Scheduler does not enqueue a disabled source. No cron builder.
6. **Pass / fail:** Pass if next-run is exact `not scheduled` (not `scheduler skip`, not a 09:00 datetime) and Manual Run requires `ov-disabled`. Fail if scheduler still shows a next-run datetime for the disabled source, if the copy is `scheduler skip`, or if Manual Run enqueues without confirm.
7. **On fail:** Defect (Engineer).

#### QA-A9

1. **ID:** QA-A9 (ship-gate)
2. **Spec trace:** A9; R-UI-14; R-UI-15; section 5.2 clean record fields including `named_party`; section 6 GetRecord; S12; F19; A38
3. **Preconditions:** At least one clean record exists. If none, this check cannot pass until ingest or Operator item has written clean (do not invent records). Prefer at least one clean `legal` record for the `named_party` branch; that branch is also QA-A38.
4. **Steps:**
   1. Records. Open a clean row (`ov-record`).
   2. Read header, current text, version switcher, extract, source, artifact, producing job, `event_time` ET, `published_time` ET, completeness, mention-usable, decision-usable.
   3. If kind is `legal`, read `named_party` (read-only, `#rec-named-party`). Clean legal shows `Donald Trump`. If kind is not `legal`, `named_party` is hidden on `ov-record`.
   4. If more than one `text_version`, pick a prior version (GetRecord).
   5. Walk the drawer for a text edit field, contenteditable, Save text, pencil on `text`, and a `confidence` field.
   6. If kind=`decision`, read `act_type`, `direction`, `status`, linked remarks.
   7. If channel=`other` and source=`books`, read helper: `Books are not mention-usable. Channel is other.`
5. **Expected observable:** Current text read-only. Prior versions listed and resolvable if any. Extract, source, artifact, job, both timestamps, completeness, mention-usable, decision-usable present. When kind is `legal`, `named_party` is shown read-only as `Donald Trump` (S12). Closed fields only; no `confidence`. Helper: `Clean text is not editable. Fix source config or re-ingest / re-extract.` Correction actions: `Open source config`, `Start re_extract`, `Start re-ingest` — no textarea for clean text. Leftover omit of `named_party` on legal is a fail.
6. **Pass / fail:** Pass if named blocks are present, legal `named_party` is shown when kind is `legal`, and text/confidence edit are absent. Fail if text is editable, `confidence` is shown, or a clean legal record omits `named_party`.
7. **On fail:** Defect (Engineer).

#### QA-A10

1. **ID:** QA-A10
2. **Spec trace:** A10; section 6 ExportRetrievalSet; R-UI-14; export field list; S12; A38; F52
3. **Preconditions:** Records search result count > 0. If empty, Export is disabled (`Nothing to export.`) — that is F30/empty, not an A10 pass. Prefer a mix that includes at least one `legal` row and one non-legal row when such rows exist.
4. **Steps:**
   1. Records. Apply search/filters so results > 0.
   2. `Export retrieval set`.
   3. Open the file/list. For each row, list keys/fields. Read `named_party` on legal and non-legal rows.
5. **Expected observable:** Immediate download, no confirm. Toast: `Exported N records.` Each record: `record_id`, `text_version`, `text_hash`, `channel`, `event_time`, `published_time`, `completeness`, `mention_usable`, `decision_usable`, `kind`, `source`, `text`, `named_party`. No `confidence`. `named_party` is `Donald Trump` on kind `legal`. It is empty on other kinds. The field is not omitted (S12). Not a call. UI times remain ET; file times may be UTC (storage) — do not fail solely because the file uses UTC ISO-8601. Do not implement a leftover section 6 list without `named_party`.
6. **Pass / fail:** Pass if the export contains the section 6 fields including `named_party` (no `confidence`) for current rows, legal is `Donald Trump`, and other kinds keep the field empty rather than omitted. Fail if fields missing, extra `confidence`, the field is omitted, legal is not `Donald Trump`, or export starts a job.
7. **On fail:** Defect (Engineer) for specified field mismatch. Change Request (Spec) if file shape beyond UTC-vs-ET is unspecified and blocks judging the field list — still fail missing named fields.

#### QA-A11

1. **ID:** QA-A11 (ship-gate)
2. **Spec trace:** A11; R-UI-16; R-UI-17; F7; F8; F9; F10
3. **Preconditions:** Quarantine has at least one field-fail item and, if present, one operator-hold item. Operator item off-S7, missing `named_party` on legal, lookalike, or job_stopped are named field-fail producers. Operator item `outlet` not on the allowlist is a named path for operator-hold / F12. If only one reason exists, run the half that exists; missing reason type when items of that reason should exist is a fail of distinguishability only when such items were produced.
4. **Steps:**
   1. Open Quarantine. Filter `all` / `field-fail` / `operator-hold`.
   2. Open a field-fail row (`ov-q-fieldfail`). Observe Accept disabled, helper, Discard enabled, fields read-only, named failed rule visible.
   3. Open an operator-hold row (`ov-q-hold`) if any. Accept enabled. Confirm: `Promote this item to clean? Fields will not be edited.` Confirm promote. Item leaves quarantine and appears clean only if field gate still passes.
   4. Confirm Accept does not present a field editor and does not fill fields.
   5. Discard is available. Persistent helper: `Discarded items shall not reappear as clean on the next incremental run unless source content or locator changed, or Fate force re-fetches.` Dedicated F10 is QA-F10.
5. **Expected observable:** Two reasons distinguishable by pills and filter. Accept disabled on field-fail (control present, disabled): `Cannot accept. Fix source or extract, then run a new job.` Accept on passing operator-hold promotes without editing fields. Discard holds F10 (verified in QA-F10).
6. **Pass / fail:** Pass if reasons are distinguishable and Accept/Discard rules match. Fail if Accept works on field-fail, edits fields, or reasons are a single blob.
7. **On fail:** Defect (Engineer).

#### QA-A12

1. **ID:** QA-A12
2. **Spec trace:** A12; CR-QA-1; section 5.1 S5; S6; F1; F5; F38; A25; packet A8 struck by section 12
3. **Preconditions:** A job is `running` and has already written some clean records. Worker pill is `available`. Stop worker (`#worker-stop`) is the named operator path.
4. **Steps:**
   1. Note the running job id and the clean `record_id`s already written under it (Records / job clean links).
   2. Chrome: Stop worker (`#worker-stop`). Overlay `ov-worker-stop` copy must be exactly `Stop the worker? Running jobs will fail with worker_lost.`
   3. Confirm. Walk Dashboard, Control, Records, Quarantine immediately.
   4. Open the job (`ov-job`). Read stored status and error. Compare to list pill.
   5. Job snapshot Running count. Jobs list: no `running` row.
   6. Records Search: those clean records still resolve and remain findable (index). Quarantine: in-flight not clean, `job_stopped`.
   7. Control, Run: new Run. Observe created status.
   8. Start worker (`#worker-start`). Confirm the `worker_lost` job is not resumed (`running` again). Retry that failed job; observe new id.
5. **Expected observable:**
   - Confirm applies S5 immediately. Banner on every screen, copy: `Worker not available. New jobs sit queued. Nothing is executing.`
   - Stored status `failed` with readable error `worker_lost`. Display matches stored status. No row is `running`.
   - S6: those clean records stay and remain in the index. In-flight not clean.
   - New Run creates `queued`. Nothing stored or shown as `running` while the worker is down.
   - `failed` does not occupy the write mutex.
   - Returning worker does not resume. Retry is a new job id (same params, pointer to the failed job).
   - A switch that only paints `not available` and does not apply S5 is a fail.
6. **Pass / fail:** Pass if S5+S6 observables hold when Stop worker is confirmed. Fail if display shows `queued` for a previously `running` job (struck packet A8), if it stays `running`, if stayed clean vanish, if the returning worker resumes the same id, or if Stop worker only paints the pill.
7. **On fail:** Defect (Engineer) against section 5.1 / CR-QA-1.

#### QA-A13

1. **ID:** QA-A13
2. **Spec trace:** A13; section 5.4 interviews; R-SRC-7; F12; CR-E1 `enabled` independent of `blocked`; CR-QA-8 Add/Remove allowlist
3. **Preconditions:** Interview-outlet allowlist is empty (default, or Fate cleared it on Control, Vocabularies with Remove). Empty first-boot observation is out of scope and is not this check. `interviews` may still be `enabled` (remaining CR-E1: enabled independent of blocked).
4. **Steps:**
   1. Control, Vocabularies. Confirm allowlist empty. Helper: `Empty allowlist blocks the interviews source. Empty jobs do not make it fresh.`
   2. Dashboard source health: `interviews` row. Confirm Enabled is `enabled` unless Fate later disabled it (CR-E1). Status extra: `blocked: empty allowlist`.
   3. Note last `succeeded` (fetched > 0) ET and freshness badges.
   4. Run `interviews` (Manual Run; confirm if disabled) such that fetched = 0, or observe an existing `succeeded_empty` for `interviews`, or run while Connector is `ok` and nothing is in-scope.
   5. Re-read last `succeeded` (fetched > 0) and freshness.
5. **Expected observable:** `interviews` shows `blocked: empty allowlist`. `enabled` is independent of `blocked`. A job that fetches 0 is `succeeded_empty` and does not mark it fresh: neither cadence nor 24h clock moves; last `succeeded` with fetched > 0 unchanged. Empty jobs do not make it fresh. No clean interview records from outlets (allowlist empty). A covering source that is blocked and has never `succeeded` with fetched > 0 is cadence-stale. Off-list mint is QA-F12 via Operator item `outlet`.
6. **Pass / fail:** Pass if blocked pill is present, enabled is not forced off by empty allowlist, and fetched=0 does not refresh. Fail if `interviews` looks fresh after empty, blocked pill is absent while allowlist is empty, or empty allowlist silently disables the source.
7. **On fail:** Defect (Engineer).

#### QA-A14

1. **ID:** QA-A14
2. **Spec trace:** A14; F16; section 5.6 Thin; R-UI-4; R-FR-3; CR-QA-11; A35; F48
3. **Preconditions:** Fate may Add a topic in Control, Vocabularies. After Add, Dashboard immediately shows one row per counted channel with usable 0 (CR-QA-11). That zero-usable row is a valid thin row. A (topic × `spoken`) row with 1 or 2 mention-usable rows is also valid if ingest produced it.
4. **Steps:**
   1. If the topic list is empty, Dashboard empty copy is `No topic × channel rows. Add topics in Control → Vocabularies, then ingest.`
   2. Control, Vocabularies. Add a topic (for example `tariffs`). Ingest is not required.
   3. Dashboard topic × counted channel table. Filter channel `spoken` if needed.
   4. Find that topic with usable count 0 in `spoken` (and the matching `written_social` row). Read Health, Failed clause, `raw clean (NOT the bar)`.
   5. Confirm there is no venue column and no third health rank.
5. **Expected observable:** Health `not-ready`. Failed clause visible (`zero usable` on the Add-topic path; or `thin: 2 usable in spoken`, `thin: no 2025_present usable` if those clauses exist). Thin is not a separate healthier rank. No venue column. One or two usable rows same rank as zero (`not-ready`). Raw clean is labeled not the bar. Ingest is not required to create the rows.
6. **Pass / fail:** Pass if health is `not-ready` with failed clause and no venue / no third rank, and Add topic yields the rows immediately. Fail if a `thin` health pill exists as a third rank, venue is a column, or adding a topic does not create rows until ingest.
7. **On fail:** Defect (Engineer). Do not pass A14 by treating the empty-table copy as a thin row; empty copy is only when the topic list is empty.

#### QA-A15

1. **ID:** QA-A15 (ship-gate)
2. **Spec trace:** A15; section 0 Done-when; section 2 Out of scope; section 8 hard exclusions; F19; F20
3. **Preconditions:** Fate on the production instance.
4. **Steps:** Walk Dashboard, Control (tabs Run job, Jobs, Sources, Vocabularies, Operator), Records (filters, result table, `ov-record`), Quarantine (filters, `ov-q-fieldfail`, `ov-q-hold` if present), and named overlays that are openable without deleting the base: `ov-run`, `ov-job` if a job exists, `ov-worker-stop` (Cancel, do not confirm Stop unless that is a dedicated check), `ov-restart` (Cancel, do not confirm Restart unless that is a dedicated check). On each surface look for forbidden controls listed below.
5. **Expected observable:** Absent on every screen and named overlay: call-loop (ledger, grading, call history, place-a-call, resolution, `no_call`); side picker (Yes/No/NO_CALL, stake/size); in-place clean-text edit (contenteditable, Save text, pencil on `text`); `confidence` field or confidence UI; venue picker / venue names as primary controls. Counted-channel footnote is not a venue picker. No second knowledge base. No user switcher. No timezone control. No cron builder. Operator is a Control tab, not a fifth chrome screen. Four chrome screens only.
6. **Pass / fail:** Pass if all are absent. Fail if any forbidden control exists or Operator is a fifth chrome nav item.
7. **On fail:** Defect (Engineer).

#### QA-A16

1. **ID:** QA-A16 (ship-gate)
2. **Spec trace:** A16; CR-QA-2; CR-QA-9; section 0 Production; A26; A33; F40
3. **Preconditions:** At least one clean `record_id` known (write it down from Records). Note enable/disable, topics, occasions, pins, and allowlist. Note a displayed job created time as an ET instant if a job exists. The instance is the one Fate-operated production instance, reachable without this chat. Restart the app (`#btn-restart`) is the named operator path. Typed DELETE of the base is not a restart.
4. **Steps:**
   1. Records: note `record_id`s (and a prior `text_version` if any) and the ET instants shown for those records and jobs.
   2. Control, Sources danger zone: **Restart the app**. Overlay `ov-restart` (not typed) copy must be exactly `Restart the app? The knowledge base stays. Running jobs fail with worker_lost.`
   3. Confirm. If a job was `running`, S5 applies first.
   4. Open the four screens without this chat. Worker pill is `available`.
   5. Search / GetRecord those same `record_id`s (and prior version if noted). Read the same ET instants. Confirm enable/disable, topics, occasions, pins, and allowlist are as they were.
5. **Expected observable:** Knowledge base is still there. Same `record_id`s resolve. Same ET instants display. Four screens plus section 6 read actions still exposed. Worker returns `available`. Fate’s enable/disable, topics, occasions, pins, and allowlist persist. Not a second knowledge base. No UTC column. This check is persistence of the base (and CR-QA-2 / CR-QA-9). No wizard and enabled independent of blocked are QA-A23. Persistence of Fate disable across Restart the app is QA-F36. No wipe is QA-A39 / QA-F53. Empty first boot is out of scope (CR-USER-1). Typed DELETE is not this path.
6. **Pass / fail:** Pass if ids resolve after Restart the app, ET instants match, worker is `available`, and config persists. Fail if the base is empty, ids do not resolve, UTC appears, worker does not return `available`, or typed DELETE was used as a substitute for Restart. Do not pass by skipping Restart the app.
7. **On fail:** Defect (Engineer).

#### QA-A17

1. **ID:** QA-A17
2. **Spec trace:** A17; section 6 Search, GetRecord, GetPreference, ExportRetrievalSet; F28; F41; A27; R-UI-13, R-UI-14, R-UI-19; CR-QA-3; S12
3. **Preconditions:** Records screen. Prefer at least one clean record and at least one topic. Empty preference is allowed (`or empty`). Records reads default `available`.
4. **Steps:**
   1. Search: Records search box and filters (`channel`, `event_time` window, `published_time` window, `kind`, `topic`, `occasion`, `mention_usable`, `decision_usable`, `source`). Apply. Observe matching clean rows. Confirm Jobs list / Dashboard job snapshot did not gain a new job.
   2. GetRecord: Open a record row (current). Pick a prior `text_version` if any. Observe one record at that version: `record_id`, `text_version`, `text_hash`, `channel`, `event_time`, `published_time`, `completeness`, `mention_usable`, `decision_usable`, `kind`, `source`, `text`, `named_party`. No `confidence`.
   3. GetPreference: Choose a topic, Open preference. Current derived preference (supporting and contradicting record ids, consistency, terms) or empty. Not a fifth chrome screen. No new job.
   4. ExportRetrievalSet: Export on current search result (QA-A10 fields including `named_party`). No new job.
   5. Control, Operator (`#tab-operator`). Set Records reads (`#records-reads`) to `down`. On Records, use each of the four actions. Dedicated down copies are QA-A27 / QA-F28 / QA-F41. Set Records reads back to `available` and confirm Search runs.
5. **Expected observable:** Each of the four section 6 actions returns the named fields or empty, including `named_party` on GetRecord and Export. None starts a job or ingests. While Records reads is `down`, each control shows its cannot-run copy and the app does not invent records. This app shall not write, store, or grade calls.
6. **Pass / fail:** Pass if all four run as read-only named actions when available, and down shows F28/F41. Fail if any starts a job/ingest, invents records, or omits named fields including `named_party`.
7. **On fail:** Defect (Engineer).

#### QA-A18

1. **ID:** QA-A18
2. **Spec trace:** A18; section 5.4 Empty official pins (S4); F31; F50; CR-QA-7 pin Save
3. **Preconditions:** Fate. Control, Vocabularies. Official X pin and official Truth Social pin each have a text field and **Save** (`#pin-x-save`, `#pin-ts-save`).
4. **Steps:**
   1. Official X pin: clear the text field and Save (`#pin-x-save`). Empty Save is F31.
   2. Dashboard / source health: `x_personal`. Confirm Enabled remains Fate’s enable/disable (CR-E1: `enabled` independent of `blocked`). Pill `blocked: empty pin`.
   3. Run a fetch job for `x_personal` (Manual Run after confirms if needed). Open the job. Open Quarantine for that job. Records filter source=`x_personal` channel=`written_social`.
   4. Control, Run, type `targeted`, mode Operator item, source `x_personal` (or `written_social` channel) with the five required fields filled. Observe refuse copy `A written_social Operator item is refused if no pin is set.` No job row. That refuse is not F2. Dedicated F50 is QA-F50.
   5. Restore the X pin if needed, then Empty Save the official Truth Social pin (`#pin-ts-save`) and repeat for `truth_social`.
   6. Note freshness clocks before and after a fetch with empty pin.
5. **Expected observable:** That source shows `blocked: empty pin`. A job does not write clean `written_social` from it. Fetched items are field-fail (pin required). Freshness does not move. Empty pin is match-none, not match-all. Empty pin does not itself flip `enabled`. Empty Save is F31. Operator item refuse when no pin is F50, not F2.
6. **Pass / fail:** Pass if blocked pill, no clean `written_social`, field-fail on fetched, freshness unchanged, and Operator item refuse copy appears with no job. Fail if empty pin match-all writes clean `written_social`, if clearing the pin disables the source as a substitute for `blocked`, or if the Operator item path uses Query copy F2.
7. **On fail:** Defect (Engineer).

#### QA-A19

1. **ID:** QA-A19
2. **Spec trace:** A19; CR-QA-6; S7; F33; F44; A30; section 5.7 clean gate
3. **Preconditions:** Fate. Control, Run job. Type `targeted`. Mode **Operator item**. Worker available. Connector for `whitehouse_remarks` is `ok`.
4. **Steps:**
   1. Mode Operator item. Source `whitehouse_remarks`. Fill locator, text, kind `social`, channel `written_social`. Submit.
   2. Open the job. Read `fetched`. Open Quarantine for that job. Records filter source=`whitehouse_remarks`.
   3. Also run an ordinary `incremental` or Query targeted for `whitehouse_remarks` if desired and inspect every clean `(kind, channel)` from that source.
5. **Expected observable:** Operator item creates a `targeted` job that processes exactly that one item (`fetched` = 1). The off-S7 pair `(social, written_social)` for `whitehouse_remarks` is field-fail F33, not clean. Accept disabled. Legal pair for `whitehouse_remarks` is only `(remark, spoken)`. Any write whose pair is off the S7 set is field-fail, not clean. Operator item is write-scoped; `ov-dup` applies if the source is occupied.
6. **Pass / fail:** Pass if the Operator item job is `fetched` = 1, the item is field-fail not clean, and no clean `whitehouse_remarks` row is off `(remark, spoken)`. Fail if the off-S7 item is clean, if no job is created when the five required fields are filled, or if Query copy F2 is shown.
7. **On fail:** Defect (Engineer). Operator item is the Spec path; do not leave forcing an off-S7 pair as an open hole.

#### QA-A20

1. **ID:** QA-A20
2. **Spec trace:** A20; section 5.6 S8 covering sources; F17; F34; automated `not-ready` from staleness uses cadence stale only
3. **Preconditions:** Dashboard topic × counted channel table has at least one `spoken` row (Add a topic if the table is empty — CR-QA-11), or source health can be read for covering vs non-covering sources.
4. **Steps:**
   1. Dashboard source health: for each source, note cadence-stale badge vs 24h stale badge.
   2. Spoken covering set (only): `whitehouse_remarks`, `app`, `factbase`, `campaign`, `interviews`.
   3. Non-covering for this clause: `books`, `legal`, `whitehouse_actions`, `federal_register`.
   4. Observe a `spoken` health row. Read Failed clause and Health.
   5. Case A: every spoken covering source is cadence-stale → `spoken` `not-ready` with stale covering clause, even if `books`/`legal`/`whitehouse_actions`/`federal_register` are fresh.
   6. Case B: at least one spoken covering source is not cadence-stale (may still show `24h stale`) → automated stale-for-not-ready clause does not fire from 24h or from books/legal. Thin may still make `not-ready`; read the failed clause.
5. **Expected observable:** Spoken not-ready from stale uses only `whitehouse_remarks`, `app`, `factbase`, `campaign`, `interviews`. `books` / `legal` / `whitehouse_actions` / `federal_register` do not decide it. 24h stale is shown but does not drive automated `not-ready`. One fresh covering source is enough to fail the all-stale clause. Sources not hidden.
6. **Pass / fail:** Pass if covering set and cadence-only rule match the failed clause. Fail if books/legal/actions/FR decide spoken stale-not-ready, or 24h stale alone drives automated `not-ready`.
7. **On fail:** Defect (Engineer).

#### QA-A21

1. **ID:** QA-A21
2. **Spec trace:** A21; section 5.6 S8 `books` cadence none (exempt), stale-for-not-ready no; R-UI-2; R-UI-12; CR-E2 exempt copy `not scheduled`
3. **Preconditions:** Source `books` visible on Dashboard and Control, Sources.
4. **Steps:**
   1. Dashboard `books` row: last `succeeded` ET if any, else `never`. Freshness: `no cadence`; never cadence-stale. 24h stale is for sources with a cadence only — `books` is exempt and has no 24h badge.
   2. Control, Sources: Cadence `none`. Next scheduled run exact copy `not scheduled`. Last success if any. Run still opens `ov-run` prefilled incremental (Manual Run remains). Connector `#connector-books` is present (CR-QA-5) and does not create a cadence.
   3. Confirm `books` is still listed (not hidden). Confirm there is no cron builder and no operator-added schedule for `books`.
   4. Dedicated next-run copy and scheduler-enqueue for `books`/`legal`/disabled is QA-F37. This check is source health / exempt clock.
5. **Expected observable:** Shows last success if any. No cadence-stale clock. Exempt. Cadence `none`. Next scheduled run `not scheduled`. v0 UI has no cron builder. There is no operator-added schedule.
6. **Pass / fail:** Pass if exempt/no cadence-stale/last success shown and next-run is `not scheduled`. Fail if `books` shows `cadence stale`, participates as a covering source, or shows a 09:00 next-run datetime.
7. **On fail:** Defect (Engineer).

#### QA-A22

1. **ID:** QA-A22
2. **Spec trace:** A22; section 5.1 S9; S6; F32; F35
3. **Preconditions:** A fetch job (`incremental`/`backfill`/`targeted`) is `running` and has fetched some items not yet written as clean. Fate can Cancel, Stop worker (`worker_lost`), or the job `failed`.
4. **Steps:**
   1. Note fetched progress from `ov-job` live counts/log if visible.
   2. Cancel or Stop worker or observe fail before those items are clean.
   3. Open `ov-job`: counts and equation.
   4. Quarantine: items from this job with named rule `job_stopped`, reason field-fail. Accept disabled. Helper: `Cannot accept. A later job for this locator may write clean if it then passes the gate. That later clean write is not also an open job_stopped item.`
   5. Records Search: those items absent from clean. Index equals stayed clean set only.
5. **Expected observable:** Those items appear in Quarantine as `job_stopped`. `quarantined` in the job equation equals that set plus any other gate-fails. `fetched = written + updated + unchanged + quarantined + fetch_fail`. No leftover. No never-committed bucket. Accept disabled on `job_stopped`.
6. **Pass / fail:** Pass if equation holds and in-flight are `job_stopped` field-fail, not clean, Accept disabled. Fail if items silently drop, a sixth count term appears, or they are clean.
7. **On fail:** Defect (Engineer).

#### QA-A23

1. **ID:** QA-A23
2. **Spec trace:** A23; CR-USER-1; remaining CR-E1 (no first-run wizard on the current instance; `enabled` independent of `blocked`); section 5.4 Factory `enabled` (CR-E1, CR-USER-1); F36; A39; F53; no first-run wizard
3. **Preconditions:** The production instance as it sits (non-empty is expected). Do not require first boot. Do not require all eleven sources enabled. Do not treat campaign left disabled (or any Fate disable) as an A23 fail. Typed DELETE is not first-boot and is not this check. Empty first-boot observation is out of scope.
4. **Steps:**
   1. Walk the four screens (Dashboard, Control, Records, Quarantine). Confirm there is no first-run wizard and no extra chrome screen that must be completed before those four.
   2. Control, Sources. Confirm `enabled` is independent of `blocked`. A blocked reason does not force `disabled`.
   3. If the interview-outlet allowlist is empty, confirm `interviews` may be `enabled` and still shows `blocked: empty allowlist`. Do not fail because Fate left `interviews` (or `campaign`, or any other source) disabled.
   4. If official X pin and/or official Truth Social pin are empty, confirm `x_personal` and/or `truth_social` still show `blocked: empty pin` without forcing `disabled`.
   5. Confirm no wizard is required. Do not require all eleven sources `enabled`.
5. **Expected observable:** No first-run wizard on the current instance. A blocked reason does not force `disabled`. `interviews` may be `enabled` and still `blocked: empty allowlist` when the allowlist is empty. Empty social pins still show `blocked: empty pin` without forcing `disabled`. This test does not require an empty first boot and does not require all eleven sources `enabled`. CR-USER-1. Typed DELETE is not this check.
6. **Pass / fail:** Pass if there is no wizard and blocked does not force disabled. Fail if a wizard is required or blocked silently disables. Do not fail because a source Fate disabled is disabled. Do not Block this check for missing empty first-boot. Empty first-boot observation is out of scope.
7. **On fail:** Defect (Engineer) if a wizard is required or blocked silently disables. Do not raise a Change Request to invent a wipe or to obtain an empty first boot. Persistence of later disable across Restart the app is QA-F36. Absence of wipe is QA-A39 / QA-F53. This check is not collapsed into those.

#### QA-A24

1. **ID:** QA-A24
2. **Spec trace:** A24; CR-E2; CR-QA-10; section 5.6 Default schedule clock; R-UI-12; F37; A8. S11 / F51 / A34 are related and are not this check.
3. **Preconditions:** Fate. Control, Sources. Control, Operator, Probe clock (`#probe-clock`). Chrome clock shows time in America/New_York labeled `ET`. Sources under test are `enabled` except where a step names disable. No cron builder is offered. There is no operator-added schedule. Empty Probe clock means the wall clock in America/New_York. Display of next-run is not a scheduler tick. This check must not Set Probe clock to a weekday 09:00 ET instant.
4. **Steps:**
   1. Control, Sources. Confirm cadence display is read-only. Confirm there is no cron builder and no control that adds a schedule or an hour other than 09:00.
   2. Control, Operator. Probe clock empty: chrome clock is wall clock ET. **Set a weekday after 09:00 ET, not at 09:00.** Use a weekday instant strictly later than 09:00 America/New_York (for example Monday 10:00 ET, or Friday 15:00 ET). Do not Set exactly 09:00. The S11 tick is Probe clock Set to a weekday 09:00 ET instant and stays on QA-A34, QA-F51, and QA-S11.
   3. Chrome clock and next-run use that after-09:00 instant.
   4. Pick an enabled daily source (`truth_social`, `x_personal`, `whitehouse_remarks`, `whitehouse_actions`, or `interviews`). Read Next scheduled run.
   5. Pick an enabled weekly source (`app`, `factbase`, `federal_register`, or `campaign`). Read Next scheduled run.
   6. Read Next scheduled run for `books`. Dedicated copy/enqueue for exempt and disabled is also QA-F37.
   7. Confirm display is only a datetime in America/New_York, or the exact copy `not scheduled`. Closed two-value display.
   8. Clear probe clock. Chrome returns to the wall clock.
5. **Expected observable (CR-E2, next-run display when now is a weekday after 09:00 ET):**
   - Spec A24 weekday-at-or-after-09:00 branch, observed from after 09:00: enabled daily source next scheduled run is the next weekday 09:00 ET (not today 09:00). Enabled weekly source: the following Monday 09:00 ET. `books` is `not scheduled`.
   - Friday after 09:00: daily next-run is Monday 09:00 ET, not Saturday. Weekly, if the source is weekly, following Monday 09:00 ET.
   - Exempt `books` and `legal`: exact copy `not scheduled`.
   - Hour is 09:00 only. No other hour appears as next scheduled run.
   - Display of `next scheduled run` is that datetime in America/New_York, or the exact copy `not scheduled`. Display of next-run is not a tick.
   - This check is next-run display. It does not require enqueue, and it does not forbid enqueue that S11 requires at weekday 09:00. S11 enqueue, freeze, and no-second-enqueue are QA-A34, QA-F51, and QA-S11.
6. **Pass / fail:** Pass if, after Set of a weekday after 09:00 ET (not at 09:00), next-run maps to the matching CR-E2 after-09:00 value, hour is only 09:00, `books` is `not scheduled`, display is the closed two-value set, and there is no cron builder. Fail if next-run uses another hour, if Saturday or Sunday receive a scheduled run, if a weekday after 09:00 still shows today 09:00, if Friday after 09:00 shows Saturday, if weekly uses a day other than Monday, if `books` shows a datetime, or if an operator-added schedule exists. **Do not fail A24 because the product enqueued at a weekday 09:00 Set.** That enqueue is S11 and is required on QA-A34, QA-F51, and QA-S11. If this check was mistakenly Set to 09:00, that is a setup error: re-Set after 09:00 and judge display only. Unobserved clock branches are not a pass of those branches; weekday 09:00 tick is QA-A34 / QA-F51 / QA-S11; weekend is QA-F47; weekday before 09:00 is QA-A34.
7. **On fail:** Defect (Engineer) against CR-E2 display. Do not route a correct S11 tick as an A24 defect.

#### QA-A25

1. **ID:** QA-A25
2. **Spec trace:** A25; CR-QA-1; A12; F38; F1; section 5.9 Stop worker
3. **Preconditions:** A job is `running` and has already written some clean records. Worker pill `available`. Chrome shows Stop worker (`#worker-stop`).
4. **Steps:**
   1. Note the running job id and stayed clean `record_id`s.
   2. Stop worker. Overlay `ov-worker-stop` copy: `Stop the worker? Running jobs will fail with worker_lost.`
   3. Confirm. This is the induction of A12. Repeat the A12 observations on this same stop: banner every screen; stored `failed` / `worker_lost`; display matches; S6 stayed/in-flight/index; no `running`; new Run is `queued`.
   4. Start worker. Confirm the `worker_lost` job is not resumed. Retry is a new id.
5. **Expected observable:** Same pass as A12, induced by Stop worker. Confirm applies S5 immediately. Pill `not available`. Banner. Stored `failed` / `worker_lost`. No `running` row. A switch that only paints `not available` is a fail.
6. **Pass / fail:** Pass if Stop worker induces the A12 observables. Fail if Stop worker is missing, copy is wrong, S5 is not applied, or only the pill changes.
7. **On fail:** Defect (Engineer). This check is not collapsed into QA-A12.

#### QA-A26

1. **ID:** QA-A26
2. **Spec trace:** A26; CR-QA-2; A16; F40; section 5.9 Restart the app
3. **Preconditions:** A clean `record_id` exists. Note Fate’s enable/disable and pins. Worker may be `available`. Control Sources danger zone shows **Restart the app** (`#btn-restart`).
4. **Steps:**
   1. Note the `record_id` and pin/enable state.
   2. Restart the app. Overlay `ov-restart` copy: `Restart the app? The knowledge base stays. Running jobs fail with worker_lost.` Not typed.
   3. Confirm. If a job was `running`, S5 applies first.
   4. After return: GetRecord the same `record_id`. Read enable/disable and pins. Read worker pill.
5. **Expected observable:** Same `record_id` resolves. Enable/disable and pins persist. Worker returns `available`. Typed DELETE is not this path. Empty first boot is out of scope (CR-USER-1). Restart of a non-empty instance is this path. Typed DELETE is not a wipe control (QA-A39 / QA-F53).
6. **Pass / fail:** Pass if the record resolves, config persists, and worker is `available`. Fail if Restart is typed DELETE, the record is gone, pins reset, or worker stays `not available`.
7. **On fail:** Defect (Engineer). This check is not collapsed into QA-A16.

#### QA-A27

1. **ID:** QA-A27
2. **Spec trace:** A27; CR-QA-3; F28; F41; A17
3. **Preconditions:** Records reads default `available`. At least one clean record so Search would otherwise return rows. Control, Operator tab (`#tab-operator`).
4. **Steps:**
   1. Control, Operator. Records reads (`#records-reads`) = `down`.
   2. Records. Use Search. Read the inline error.
   3. Confirm no invented rows appear.
   4. Set Records reads to `available`. Use Search. Matching clean rows return as specified.
5. **Expected observable:** While `down`, copy `Search cannot run.` No invented records. While `available`, Search runs as specified. Dedicated all-four-controls copy is QA-F41.
6. **Pass / fail:** Pass if Search cannot-run copy appears while down, no invented records, and Search runs when available. Fail if Search invents rows, fails silently, or stays down after `available`.
7. **On fail:** Defect (Engineer).

#### QA-A28

1. **ID:** QA-A28
2. **Spec trace:** A28; CR-QA-4; F29; F42
3. **Preconditions:** Fate on the instance. Control, Operator. Fail next load (`#fail-next-load`) with choice Dashboard / Control / Records / Quarantine and **Set** (`#fail-next-load-set`). Data may already be shown on Dashboard.
4. **Steps:**
   1. Control, Operator. Choice Dashboard. Set.
   2. Open Dashboard.
   3. Read the error and Retry.
   4. If data was already shown, confirm it stays until replaced.
   5. Retry. Confirm Dashboard loads and the fail is cleared (a further open of Dashboard is not the error unless Set again).
5. **Expected observable:** Copy `Dashboard failed to load` plus Retry. Retry loads Dashboard and clears the fail. Data already shown stays until replaced. This is the only operator way to induce F29. Dedicated all-four-screens is QA-F42.
6. **Pass / fail:** Pass if Dashboard copy, Retry, load, and clear hold. Fail if the screen wipes without Retry, copy is wrong, or Retry does not clear.
7. **On fail:** Defect (Engineer).

#### QA-A29

1. **ID:** QA-A29
2. **Spec trace:** A29; CR-QA-5; F25; F43; S6
3. **Preconditions:** Worker available. Control, Sources. Connector on `books` (`#connector-books`) default `ok`. `books` may be enabled or Fate may Manual Run after `ov-disabled`.
4. **Steps:**
   1. Set Connector on `books` to `auth`.
   2. Run job type `incremental`, source `books`. Confirm overlays as specified.
   3. Worker executes the job. Open `ov-job`.
   4. Confirm S6. Confirm no silent extra job with the same params.
   5. Set Connector back to `ok`. Confirm the failed job is not resumed.
5. **Expected observable:** Job stored `failed` with readable error exactly `auth`. S6 applies. No silent retry loop. Setting Connector back to `ok` does not resume the failed job. Retry is a new job id if Fate retries.
6. **Pass / fail:** Pass if failed / error `auth` / S6 / no silent retry / no resume. Fail if the job succeeds, error is not exactly `auth`, a silent retry appears, or setting `ok` resumes the same id.
7. **On fail:** Defect (Engineer).

#### QA-A30

1. **ID:** QA-A30
2. **Spec trace:** A30; CR-QA-6; A19; F33; F44; S7
3. **Preconditions:** Control, Run job. Type `targeted`. Mode Operator item. Worker available. Connector `whitehouse_remarks` is `ok`.
4. **Steps:**
   1. Operator item: source `whitehouse_remarks`, kind `social`, channel `written_social`, locator filled, text filled. Submit.
   2. Open the job. Read fetched. Open Quarantine. Records Search source=`whitehouse_remarks` for that locator.
5. **Expected observable:** Field-fail. Not clean. `fetched` = 1. Named failed rule is the off-S7 pair. Accept disabled. Query copy is not shown.
6. **Pass / fail:** Pass if field-fail, not clean, fetched=1. Fail if the item is clean or no job is created.
7. **On fail:** Defect (Engineer). This check is not collapsed into QA-A19.

#### QA-A31

1. **ID:** QA-A31
2. **Spec trace:** A31; CR-QA-7; F11; F45; A18; S4
3. **Preconditions:** Control, Vocabularies. Official X pin text field plus Save (`#pin-x-save`). Worker available. Connector `x_personal` is `ok`.
4. **Steps:**
   1. Save a non-empty official X pin. Dashboard: `x_personal` is not `blocked: empty pin`.
   2. Control, Run, type `targeted`, mode Operator item. Source `x_personal`. Fill locator, text, kind `social`, channel `written_social`. Pin match `lookalike` (`#pin-match-page`). Submit.
   3. Open the job. Records and Quarantine for that locator.
5. **Expected observable:** Quarantined, not clean. Source is not `blocked: empty pin`. F11 applies: lookalike means attribution does not equal the saved pin. `fetched` = 1. Accept disabled on the field-fail lookalike.
6. **Pass / fail:** Pass if lookalike is quarantined not clean and the source is not empty-pin blocked. Fail if the lookalike is clean or Empty Save was still in effect.
7. **On fail:** Defect (Engineer).

#### QA-A32

1. **ID:** QA-A32
2. **Spec trace:** A32; CR-QA-8; F27; F46
3. **Preconditions:** Control, Run, type `targeted`, mode Operator item. Worker available. Connector `legal` is `ok`.
4. **Steps:**
   1. Operator item: source `legal`, kind `legal`, channel `legal`, locator filled, text filled, `named_party` `the administration` (`#named-party-page`). Submit.
   2. Open the job. Records filter kind=`legal`. Quarantine for that locator.
5. **Expected observable:** Not ingested as `legal` clean. F27. Field-fail, not a silent drop. Clean legal requires `named_party` equal to `Donald Trump`.
6. **Pass / fail:** Pass if no clean `legal` record is `the administration`. Fail if one is, or if the item is silently dropped with no quarantine.
7. **On fail:** Defect (Engineer).

#### QA-A33

1. **ID:** QA-A33
2. **Spec trace:** A33; CR-QA-9; A16; F40
3. **Preconditions:** At least one job exists so a created time is displayed. Note that ET instant (label `ET`). Restart the app is available.
4. **Steps:**
   1. Control, Jobs. Read the created time for a known job id as displayed (ET).
   2. Walk chrome, tables, drawers, overlays, banners for any UTC timestamp or UTC column.
   3. Restart the app (`ov-restart`). Confirm.
   4. After return, open the same job. Read created time. Walk screens again for UTC.
5. **Expected observable:** Same ET instant as before restart. No UTC string on the screen. No UTC column. Every displayed time is America/New_York with label `ET`. Persistence of `record_id` is QA-A16; this check is the ET instant and the no-UTC rule.
6. **Pass / fail:** Pass if the ET instant matches and no UTC appears. Fail if the instant changes, a UTC column exists, or a UTC timestamp is shown on chrome, table, drawer, overlay, or banner.
7. **On fail:** Defect (Engineer).

#### QA-A34

1. **ID:** QA-A34
2. **Spec trace:** A34; CR-QA-10; S11; F51; F47; A24
3. **Preconditions:** Fate. Control, Operator, Probe clock. At least one weekly source (`app`, `factbase`, `federal_register`, or `campaign`) is `enabled` and not exempt. Prefer daily sources also `enabled` so the Monday 09:00 tick is visible for sources due that day. Worker available enough that enqueued `incremental` jobs can appear as `queued` (or `running`). No write-scoped occupant that would block enqueue; if mutex rejects, that is not a pass of “did not enqueue” for this check.
4. **Steps:**
   1. Probe clock **Set** Monday 08:00 ET. Read weekly next-run. Confirm no new `incremental` rows with `triggered_by` `schedule`.
   2. Probe clock **Set** Monday 09:00 ET. This is the tick. Observe enqueue of `incremental` once for each enabled non-exempt source due that day. Then next-run advances (weekly: the following Monday 09:00).
   3. Leave frozen at that Monday 09:00 instant. Confirm no second enqueue.
   4. Probe clock **Set** Monday 10:00 ET. Confirm no enqueue. Weekly next-run remains the following Monday 09:00.
   5. Dedicated Saturday/Sunday is QA-F47. Dedicated weekday-09:00 tick statement is also QA-F51.
5. **Expected observable:**
   - Monday 08:00: weekly next-run is this Monday 09:00. No enqueue.
   - Set Monday 09:00: the tick. Enqueue `incremental` once for each enabled non-exempt source due that day, then advance next-run (weekly following Monday 09:00; daily next weekday 09:00).
   - Remaining frozen at Monday 09:00: no second enqueue.
   - Set Monday 10:00: no enqueue.
   - Display of next-run is not that tick. Exempt and disabled are not enqueued.
6. **Pass / fail:** Pass if the four named instants match enqueue and next-run. Fail if Monday 08:00 or 10:00 enqueues, if Monday 09:00 does not enqueue sources due that day, if remaining frozen enqueues again, or if display of next-run itself enqueues.
7. **On fail:** Defect (Engineer).

#### QA-A35

1. **ID:** QA-A35
2. **Spec trace:** A35; CR-QA-11; A14; F16; F48
3. **Preconditions:** Control, Vocabularies. Topic list may be empty or not; this check Adds `tariffs`. Ingest is not performed for this check.
4. **Steps:**
   1. If the topic list is empty, Dashboard copy is `No topic × channel rows. Add topics in Control → Vocabularies, then ingest.`
   2. Add topic `tariffs`. Do not ingest.
   3. Open Dashboard. Find `tariffs` × `spoken` and `tariffs` × `written_social`.
   4. Read usable count, health, failed clause.
5. **Expected observable:** Dashboard shows `tariffs` × `spoken` and `tariffs` × `written_social`, usable 0, health `not-ready`, failed clause `zero usable`. Ingest is not required to create those rows. Empty copy is gone once a topic exists.
6. **Pass / fail:** Pass if both rows appear immediately with those values. Fail if ingest is required, a single collapsed row appears, health is a third rank, or empty copy remains after Add.
7. **On fail:** Defect (Engineer).

#### QA-A36

1. **ID:** QA-A36
2. **Spec trace:** A36; S10; A4; A37; F2; F49
3. **Preconditions:** Control, Run job. Type `targeted`. Mode **Operator item**. The five required fields can be filled. Topic, query, and occasion can be empty or hidden.
4. **Steps:**
   1. Mode Operator item. Leave topic, query, and occasion empty (or hidden). Fill source, locator, text, kind, and channel with a legal S7 pair (for example source `whitehouse_remarks`, kind `remark`, channel `spoken`). Submit.
   2. Observe whether Query copy appears. Control, Jobs: confirm a job row is created.
5. **Expected observable:** Job is created. Query copy `Targeted needs a topic, query, or occasion.` is not shown (S10). Operator item may submit with those three fields empty or hidden.
6. **Pass / fail:** Pass if the job is created and Query copy is not shown. Fail if Query copy refuses the run or no job is created when the five required fields are filled.
7. **On fail:** Defect (Engineer).

#### QA-A37

1. **ID:** QA-A37
2. **Spec trace:** A37; S10; F49; A4; A36
3. **Preconditions:** Control, Run job. Type `targeted`. Mode **Operator item**.
4. **Steps:**
   1. Mode Operator item. Fill source, text, kind, and channel. Leave locator empty. Submit.
   2. Observe inline error. Control, Jobs: confirm no new row.
5. **Expected observable:** Refused. Copy `Operator item needs source, locator, text, kind, and channel.` No job. Not A4. Query copy is not used. This refuse is not F2.
6. **Pass / fail:** Pass if Operator item copy appears and no job is created. Fail if a job row appears, if Query copy is shown, or if the refuse is treated as F2/A4.
7. **On fail:** Defect (Engineer).

#### QA-A38

1. **ID:** QA-A38
2. **Spec trace:** A38; S12; A9; A10; F52; CR-QA-8
3. **Preconditions:** A clean `legal` record exists with `named_party` `Donald Trump`. If none, Operator item source `legal`, kind `legal`, channel `legal`, `named_party` `Donald Trump`, plus required locator and text, is the Spec path to mint one that can pass the ordinary clean gate. Absence of `named_party` is F52, not this pass path.
4. **Steps:**
   1. Records. Open the clean `legal` record (`ov-record`). Read `named_party` (`#rec-named-party`).
   2. GetRecord current version (opening the row is GetRecord). Confirm `named_party` is included.
   3. Export retrieval set on a search that includes that row. Read `named_party` on that row in the file.
5. **Expected observable:** `ov-record` shows `named_party` `Donald Trump` (read-only). GetRecord includes `named_party`. Export of that row includes `named_party` `Donald Trump`. Field not omitted. Hidden on non-legal `ov-record`; Export still includes the field empty on non-legal rows (QA-A10).
6. **Pass / fail:** Pass if all three surfaces show `Donald Trump` for that legal row. Fail if `named_party` is missing on any of the three, or if it is editable.
7. **On fail:** Defect (Engineer).

#### QA-A39

1. **ID:** QA-A39
2. **Spec trace:** A39; CR-USER-1; CR-QA-2 Restart the app is not a wipe; section 2 Out of scope (operator wipe); section 5.4; F53; F21; A15 is related and is not this check
3. **Preconditions:** Fate on the production instance as it sits. Walk all four screens and Control Sources danger zone. Do not send typed DELETE. Confirming typed DELETE is not a step of A39. Empty first-boot observation is out of scope.
4. **Steps:**
   1. Walk Dashboard, Control (tabs Run job, Jobs, Sources, Vocabularies, Operator), Records, Quarantine.
   2. Control Sources danger zone: confirm **Restart the app** is present (`#btn-restart`, `ov-restart`).
   3. Look for a wipe control or a return-to-empty-first-boot control on every screen and named overlay that is openable without confirming a destructive action. Cancel `ov-restart` if opened; do not confirm Restart unless a dedicated restart check is sharing setup.
   4. Confirm Restart the app is not a wipe (CR-USER-1). Confirm typed DELETE of the base, if present, is the existing F21 control (packet 9.10 / Assumption A4: removes clean records and derived preferences; job history and raw artifacts remain) and is not a wipe control.
   5. Do not send typed DELETE. Do not invent a wipe.
5. **Expected observable:** Restart the app is present. No wipe control. No return-to-empty-first-boot control. Restart the app is not a wipe (CR-USER-1).
6. **Pass / fail:** **Advisory (DTM, bind into pass/fail):** typed DELETE is not a fail of A39. Presence of typed DELETE is not a wipe control and is not a fail of A39. Confirming typed DELETE is not a step of A39. Do not send typed DELETE. Restart the app is not a wipe. Pass if Restart the app is present and no wipe / return-to-empty-first-boot control exists. Fail if a wipe or return-to-empty control exists (other than typed DELETE, which is not that control). Do not fail A39 because typed DELETE exists. Do not collapse this into QA-A15 or QA-A23.
7. **On fail:** Defect (Engineer) if a wipe or return-to-empty-first-boot control exists (other than typed DELETE). Do not invent a wipe to exercise this check. Absence is the pass.

---

### 4.2 Failure checks

#### QA-F1

1. **ID:** QA-F1
2. **Spec trace:** F1; CR-QA-1; section 5.1 S5 Worker down; S6; R-UI-6; section 8 2.1 banner copy; packet A8 struck; A12; A25; F38; F39
3. **Preconditions:** Worker pill can be made `not available` by Stop worker (`#worker-stop`). Prefer at least one job that is `running` when Stop worker is confirmed, plus ability to Run.
4. **Steps:**
   1. Stop worker. Confirm `ov-worker-stop`. Walk all four screens: banner present.
   2. Jobs list and `ov-job` for any job that had stored `running`: stored `failed` / `worker_lost`; display matches; no `running` anywhere including snapshot Running = `0`.
   3. S6 on that job: stayed clean remain; in-flight not clean; index equals stayed set.
   4. New Run: creates `queued`, helper on form: `Worker not available. This job will sit queued until a worker executes it.`
   5. Attempt a write-scoped job for a source whose only occupant was the now-`failed` job: mutex released (no `ov-dup` naming the failed id as occupant). A still-`queued` job still occupies the mutex.
   6. Start worker: it does not resume the `worker_lost` job; it executes the next `queued` job if any.
5. **Expected observable:** Banner every screen: `Worker not available. New jobs sit queued. Nothing is executing.` Stored `running` becomes `failed` with `worker_lost`. Display matches. New Run `queued`. No stored or shown `running`. S6. Mutex released for `failed`. Returning worker does not resume. A switch that only paints `not available` is a fail.
6. **Pass / fail:** Pass if all F1 bullets hold. Fail if previously `running` is shown as `queued` (struck), stays `running`, is resumed, or Stop worker does not apply S5.
7. **On fail:** Defect (Engineer). Do not pass F1 by skipping Stop worker.

#### QA-F2

1. **ID:** QA-F2
2. **Spec trace:** F2; A4; S10; Control validation; section 5.5 required params. Does not apply to Operator item.
3. **Preconditions:** Control, Run job.
4. **Steps:**
   1. Type `incremental`. Leave source empty. Run. Copy: `Source is required.` No job row.
   2. Type `backfill`. Source set, window missing. Copy: `Backfill needs a date window.` No job row. Window start after end: `Start must be on or before end.` No job row.
   3. Type `targeted`. Mode **Query**. Source set, topic/query/occasion all empty. Copy: `Targeted needs a topic, query, or occasion.` No job row.
   4. Type `re_extract`. Neither source nor global: `Pick a source or global.` No job row.
   5. Do not treat Operator item missing fields as this check (QA-F49 / QA-A37). Do not treat Operator item with topic/query/occasion empty as this check (QA-A36).
5. **Expected observable:** Run refused in place. No job row. Query-only targeted require applies only to mode Query (S10).
6. **Pass / fail:** Pass if all listed Query-path refusals create no job. Fail if any missing-params Run creates a queued row, or if Operator item is refused with this Query copy.
7. **On fail:** Defect (Engineer).

#### QA-F3

1. **ID:** QA-F3
2. **Spec trace:** F3; R-JOB-9; section 5.5 global lock; A5; A5b; F24. Packet leftover “Global jobs are not this mutex” is struck.
3. **Preconditions:** Fate. Ability to start write-scoped and global jobs. Operator item is write-scoped.
4. **Steps:**
   1. Occupant = source write-scoped `queued` or `running` for source S. Second write-scoped for S (including Operator item): `ov-dup` Queue behind / Don’t start. Incremental and backfill cannot write S at once.
   2. Occupant = global `re_extract` `queued` or `running`. Start source write-scoped for any source: same choice.
   3. Occupant = global `re_index` (after `ov-reindex` confirm) `queued` or `running`. Start source write-scoped: same choice.
   4. Occupant = global `refresh_preferences` (after `ov-refresh` confirm) `queued` or `running`. Start source write-scoped: same choice.
   5. Visible reason names blocking job id, type, and source (global jobs source = `global`).
5. **Expected observable:** Fate chooses queue-behind or don’t-start. Visible reason. Incremental and backfill cannot write that source at once. Global `re_extract` / `re_index` / `refresh_preferences` occupy every source. Operator item does not skip `ov-dup`.
6. **Pass / fail:** Pass if each occupant class produces `ov-dup` (or equivalent specified choice) and never concurrent writes. Fail if a second write-scoped job runs concurrently with any named occupant, or if global jobs are treated as outside this mutex.
7. **On fail:** Defect (Engineer).

#### QA-F4

1. **ID:** QA-F4
2. **Spec trace:** F4; R-JOB-9 third-job reject; copy bank
3. **Preconditions:** For a source, one write-scoped job `running` and one queued-behind (including a waiting global job occupying that source).
4. **Steps:**
   1. Submit a further write-scoped job for that source (Run, Operator item, or Retry).
   2. Observe there is no overlay choice.
   3. Count jobs for that source in `{queued, running}`.
5. **Expected observable:** Rejected only. No third job. No overlay choice. Copy: `Rejected: source {source} already has a queued job waiting behind {id}.`
6. **Pass / fail:** Pass if no third job and reject copy. Fail if a third job is created or `ov-dup` offers Queue behind again.
7. **On fail:** Defect (Engineer).

#### QA-F5

1. **ID:** QA-F5
2. **Spec trace:** F5; S6 only, one rule for `failed`, `cancelled`, `worker_lost`; no other branch
3. **Preconditions:** Three terminal stop kinds as available: a `cancelled` job (QA-A6), a `failed` job (including Connector `auth`/`network`/`parse`), a `worker_lost` job (Stop worker, QA-A12). Run the S6 observations on each kind that exists. Missing a kind because it never occurred is not a pass of that branch; induce `worker_lost` with Stop worker and `failed` with Connector.
4. **Steps:** For each stop kind present:
   1. Open `ov-job`: stored status; `written`+`updated` = stayed set; in-flight in `quarantined`.
   2. Records: stayed clean under that job id resolve; producing job = that id.
   3. Records Search does not return in-flight items (not in index).
   4. Confirm no later clean/index/preference row produced by that same job id after it left `running`.
   5. Earlier `succeeded` jobs’ records still resolve.
5. **Expected observable:** S6 only. Stayed clean remain. In-flight not clean. Index equals stayed set. No further writes from that job id. Earlier succeeded records stay.
6. **Pass / fail:** Pass if S6 holds for each observed stop kind. Fail if any other commit branch appears (silent drop, resume writes, strip stayed).
7. **On fail:** Defect (Engineer).

#### QA-F6

1. **ID:** QA-F6
2. **Spec trace:** F6; section 5.3 fetch returns nothing in-scope is `succeeded_empty` (fetched = 0); does not move freshness; `succeeded_empty` does not reset either clock; CR-QA-5 fetch nothing while Connector is `ok` is `succeeded_empty`
3. **Preconditions:** Note Dashboard last `succeeded` (fetched > 0) ET and freshness badges for a source. Connector for that source is `ok`. Fate can start a fetch that returns nothing in-scope (for example targeted **Query** with a topic/query/occasion that matches nothing in-scope, or `incremental` when nothing new).
4. **Steps:**
   1. Record last `succeeded` fetched>0, last `succeeded_empty`, cadence-age, 24h age.
   2. Confirm Connector is `ok`. Run the empty-in-scope fetch. Open `ov-job`.
   3. Re-read source health.
5. **Expected observable:** Status `succeeded_empty`. `fetched = 0`. Pill is success-with-zero: not red. Freshness clocks do not move. Last `succeeded` (fetched > 0) unchanged. Last `succeeded_empty` visible (ET). Empty jobs do not make it fresh. Connector not-ok is F43, not this check.
6. **Pass / fail:** Pass if `succeeded_empty` and clocks unchanged. Fail if empty fetch is `succeeded`, moves freshness, is shown as a red fail, or is stored `failed` while Connector is `ok`.
7. **On fail:** Defect (Engineer).

#### QA-F7

1. **ID:** QA-F7
2. **Spec trace:** F7; section 5.7 Gate fail → quarantine with the failed rule named; R-UI-16 field-fail; Accept disabled
3. **Preconditions:** At least one item that failed the clean gate. Named producers: empty-pin fetch (QA-A18), Operator item off-S7 (QA-A19 / QA-A30), Operator item lookalike (QA-A31), Operator item missing `named_party` on legal (QA-F52), `job_stopped`.
4. **Steps:**
   1. Quarantine filter `field-fail`. Open item. Read named failed rule. Fields read-only.
   2. Confirm item is not in Records Search as clean.
   3. Accept is disabled. Helper: `Cannot accept. Fix source or extract, then run a new job.`
5. **Expected observable:** Quarantine field-fail. Not clean. Accept disabled. Failed rule named.
6. **Pass / fail:** Pass if field-fail, not clean, Accept disabled, rule visible. Fail if gate-fail is stored clean or Accept is enabled.
7. **On fail:** Defect (Engineer).

#### QA-F8

1. **ID:** QA-F8
2. **Spec trace:** F8; R-UI-16 operator-hold; section 8 9.6 Accept flow; Accept does not fill or edit; CR-QA-8 Operator item `outlet` not on allowlist is F12 and a named path
3. **Preconditions:** An operator-hold item exists (fields pass; Fate has not accepted — disputed attribution, source not yet on an allowlist, connector mislabel). Named path: Operator item source `interviews`, kind `interview`, channel `spoken`, `outlet` not on the allowlist (F12). Interview item from an outlet not on the allowlist is operator-hold, not silently stored clean.
4. **Steps:**
   1. Open `ov-q-hold`. Fields read-only. Accept enabled. No field editor.
   2. Confirm: `Promote this item to clean? Fields will not be edited.` Cancel: stays quarantined.
   3. Confirm Accept. If field gate still passes: item leaves quarantine and is clean in Records. If not: stays quarantined, failed rule visible, inline `Accept refused: still fails {rule}.`
5. **Expected observable:** Quarantine operator-hold. Accept promotes only if field gate still passes. Accept does not edit or fill.
6. **Pass / fail:** Pass if promote-only and no field edit. Fail if Accept fills timestamps/text or promotes a field-fail. Do not invent a public item; use Operator item `outlet` if no operator-hold yet exists.
7. **On fail:** Defect (Engineer).

#### QA-F9

1. **ID:** QA-F9
2. **Spec trace:** F9; R-UI-16; section 8 9.7; Accept control present but disabled on field-fail
3. **Preconditions:** A field-fail item (including `job_stopped`, off-S7 Operator item, lookalike, missing `named_party`).
4. **Steps:**
   1. Open field-fail item. Accept disabled (not missing).
   2. If Fate can still invoke accept somehow, observe refuse: item stays quarantined, failed rule stays visible, inline `Accept refused: still fails {rule}.`
5. **Expected observable:** Refused. Item stays quarantined. Failed rule stays visible.
6. **Pass / fail:** Pass if Accept cannot promote field-fail. Fail if field-fail becomes clean via Accept.
7. **On fail:** Defect (Engineer).

#### QA-F10

1. **ID:** QA-F10
2. **Spec trace:** F10; R-UI-17; discard helper copy
3. **Preconditions:** A quarantined item with a known locator. Fate discards it. Then an `incremental` for that source with same locator and unchanged content (force re-fetch off).
4. **Steps:**
   1. Discard. Confirm: `Discard this item?` After discard, copy on the item and in the persistent helper (R-UI-17 sentence).
   2. Run `incremental` for that source, force re-fetch off.
   3. Records Search: that locator content does not appear as clean.
5. **Expected observable:** Does not reappear as clean. (Unless source content or locator changed, or Fate force re-fetches — those exceptions are out of this check pass path.)
6. **Pass / fail:** Pass if incremental does not resurrect the discarded item as clean. Fail if it reappears clean without content/locator change or force re-fetch.
7. **On fail:** Defect (Engineer).

#### QA-F11

1. **ID:** QA-F11
2. **Spec trace:** F11; S4; CR-QA-7; F45; A31; helper `Clean written_social attribution must match these pins. A lookalike is quarantined.`
3. **Preconditions:** Official X pin and/or Truth Social pin is set (not empty) via Save. Operator item pin match `lookalike` is the Spec path. Public lookalike fetch may also appear; do not require it when Operator item lookalike is used.
4. **Steps:**
   1. Confirm pin is set (Vocabularies Save).
   2. Operator item source `truth_social` or `x_personal`, pin match `lookalike`, five required fields filled. Submit.
   3. Records: the item is not clean `written_social`. Quarantine: lookalike is quarantined, not clean, field-fail.
   4. If a public fetch also returns a mismatch, the same rule applies.
5. **Expected observable:** Lookalike quarantined, not clean. Empty pin is a different check (QA-F31). Set pin is match-pin, not match-all. Operator item lookalike is F45 and this check.
6. **Pass / fail:** Pass if the Operator item lookalike is quarantined not clean. Fail if a lookalike is clean.
7. **On fail:** Defect (Engineer). Do not leave lookalike as an open hole; Operator item pin match is the Spec path.

#### QA-F12

1. **ID:** QA-F12
2. **Spec trace:** F12; section 5.4 interviews ingest only outlets on the allowlist; default empty; R-SRC-7; A13; CR-QA-8 Add/Remove and Operator item `outlet`
3. **Preconditions:** Two branches. (1) Allowlist empty. (2) Allowlist has at least one outlet (Add), and Operator item `outlet` not on the list.
4. **Steps:**
   1. Empty allowlist: Dashboard `blocked: empty allowlist`. Job fetched=0 does not mark fresh (QA-A13). Items not clean. Source remains Fate’s `enabled`/`disabled` (CR-E1).
   2. Add one outlet (`#allowlist-add`, text plus Add). Run `interviews` or inspect clean interview rows: source outlets are on the list.
   3. Operator item source `interviews`, kind `interview`, channel `spoken`, `outlet` not on the list. Submit. The item is not clean (operator-hold per section 8 7.1, not silently stored clean). Empty jobs still do not make it fresh.
   4. Remove the added outlet (`#allowlist-remove`). Empty allowlist returns `blocked: empty allowlist`.
5. **Expected observable:** Not clean when outlet not on list or allowlist empty. Empty → `blocked: empty allowlist`. Empty jobs do not make it fresh. Add/Remove are the named controls.
6. **Pass / fail:** Pass if both empty-allowlist observables hold and off-list Operator item is not clean. Fail if off-list or empty-allowlist interviews are clean, or empty jobs refresh the source.
7. **On fail:** Defect (Engineer). Operator item `outlet` is the Spec path; do not leave off-list as an open hole.

#### QA-F13

1. **ID:** QA-F13
2. **Spec trace:** F13; section 5.3 Extract writes topics and occasions only from operator lists; a tag not on the list is quarantined, not a new vocabulary entry; R-UI-18 remove does not edit clean records
3. **Preconditions:** Fate can edit topic and occasion lists. A later `re_extract` or fetch will extract a tag that is no longer on the list (remove a tag that previously appeared on records, then Start `re_extract`).
4. **Steps:**
   1. Control, Vocabularies: note topic list. Remove a topic that existing text would extract, or run extract when text contains a tag not on the list.
   2. Start `re_extract` (source or global; confirms/mutex as specified).
   3. Vocabularies: confirm the list was not auto-grown.
   4. Quarantine: items with that tag named as failed rule, not a new vocabulary entry. Clean records are not silently given the removed tag as a new list entry. No fuzzy similarity control — none is offered.
5. **Expected observable:** Quarantined. List is not auto-grown. “Like the last time this occasion happened” means the same occasion tag. No fuzzy similarity.
6. **Pass / fail:** Pass if off-list tag quarantines and the list does not gain the tag. Fail if extract adds a vocabulary entry or writes the off-list tag clean.
7. **On fail:** Defect (Engineer).

#### QA-F14

1. **ID:** QA-F14
2. **Spec trace:** F14; section 5.5 Re-running the same source and window shall not duplicate clean records for the same locator; section 5.3 same locator collapses to one `record_id`
3. **Preconditions:** A fetch job for a source/window that already wrote at least one clean locator. Fate runs the same source and window again (force re-fetch off). Operator item for the same locator is also a same-locator run.
4. **Steps:**
   1. Note `record_id` and locator/url for a clean record.
   2. Run the same source and window again, or Operator item with the same locator.
   3. Open the new job counts (`unchanged` or new `text_version`). Records Search that locator: one current `record_id`.
5. **Expected observable:** Same `record_id`. `unchanged` or new `text_version`. No second current id.
6. **Pass / fail:** Pass if one current id. Fail if two current ids for one locator.
7. **On fail:** Defect (Engineer).

#### QA-F15

1. **ID:** QA-F15
2. **Spec trace:** F15; section 5.5 Force re-fetch pulls new raw artifacts and may write a new `text_version` on the same `record_id`; shall not invent a second current id; shall not destroy the prior version; GetRecord resolves `record_id` + `text_version` + `text_hash`
3. **Preconditions:** A clean record with artifact and at least the current `text_version`. Fate runs a fetch job with Force re-fetch on: label `Force re-fetch — pull new raw artifacts; may write a new text_version (R-JOB-13)`. Hidden on Operator item.
4. **Steps:**
   1. Note `record_id`, current `text_version`, `text_hash`, artifact link.
   2. Run incremental/backfill/targeted Query with Force re-fetch on (mutex as specified).
   3. Open `ov-job` artifacts: new raw artifact (re-fetch creates a new artifact).
   4. GetRecord current and prior `text_version` in `ov-record` version switcher.
5. **Expected observable:** New raw artifact. May new `text_version` on same id. Prior version stays resolvable. No second current id. Prior version not destroyed.
6. **Pass / fail:** Pass if new artifact, same current id, prior version resolvable. Fail if second current id or prior version gone.
7. **On fail:** Defect (Engineer).

#### QA-F16

1. **ID:** QA-F16
2. **Spec trace:** F16; A14; A35; F48; section 5.6 Thin; health two states only; CR-QA-11
3. **Preconditions:** Same as QA-A14: a thin (topic × counted channel), including the Add-topic usable-0 rows.
4. **Steps:** Dashboard row for that topic × counted channel. Read Health and Failed clause. Confirm no venue.
5. **Expected observable:** Dashboard `not-ready` with the failed thin clause. Not a healthier third rank. No venue.
6. **Pass / fail:** Pass if `not-ready` + clause, no third rank, no venue. Fail otherwise.
7. **On fail:** Defect (Engineer).

#### QA-F17

1. **ID:** QA-F17
2. **Spec trace:** F17; S8; A20; a covering source that is blocked (empty allowlist or empty pin) and has never `succeeded` with fetched > 0 is cadence-stale
3. **Preconditions:** For a counted channel, every covering source in the S8 set is cadence-stale (including blocked-never-succeeded as cadence-stale). Exempt sources may be anything. Add a topic if the table has no rows (CR-QA-11).
4. **Steps:**
   1. Spoken covering: `whitehouse_remarks`, `app`, `factbase`, `campaign`, `interviews`. Written_social covering: `truth_social`, `x_personal`.
   2. Confirm each covering source shows cadence stale (or blocked never succeeded).
   3. Dashboard topic × that counted channel: Health `not-ready`. Sources still listed (not hidden).
   4. Confirm `books` and `legal` are ignored for this clause (QA-F34).
5. **Expected observable:** Dashboard `not-ready`. Sources not hidden. Exempt sources are ignored for this clause.
6. **Pass / fail:** Pass if all-covering-cadence-stale implies `not-ready` and rows not hidden. Fail if health stays `ready` while all covering are cadence-stale (and not thin-exception — thin also `not-ready`).
7. **On fail:** Defect (Engineer). Arranging all covering cadence-stale may use Probe clock so cadence-age exceeds one weekday (daily) or eight days (weekly). Do not invent a faster control than Probe clock.

#### QA-F18

1. **ID:** QA-F18
2. **Spec trace:** F18; section 1 books `channel = other` not mention-usable; section 5.2 channel enum; section 2 never `written_other`; Records channel filter
3. **Preconditions:** Prefer at least one clean `books` row. Absence of `written_other` is still checked with zero books rows. Operator item source `books`, kind `writing`, channel `other` is a named path if no books row exists yet and the ordinary clean gate can pass.
4. **Steps:**
   1. Records channel filter values: `spoken` `written_social` `written_official` `legal` `other` + all. Confirm `written_other` is not a value.
   2. Walk four screens and overlays for the token `written_other` as a channel control or clean channel value.
   3. If a books row exists: channel `other`, mention-usable no. Helper on `ov-record` when channel is `other`: `Books are not mention-usable. Channel is other.`
5. **Expected observable:** `channel = other`. `mention_usable = false`. Filter value is `other`, never `written_other`.
6. **Pass / fail:** Pass if books (when present) match and `written_other` is absent. Fail if books are `spoken`/`written_social`/`written_other` or mention-usable yes, or if `written_other` exists as a control.
7. **On fail:** Defect (Engineer).

#### QA-F19

1. **ID:** QA-F19
2. **Spec trace:** F19; R-UI-15; Records 6.7 NOT; hard exclusions
3. **Preconditions:** None beyond operator access to the four screens and named overlays, including Operator tab and `ov-record` legal extras.
4. **Steps:** Walk Dashboard, Control (all tabs including Operator), Records, Quarantine, `ov-record`, `ov-qitem`, `ov-job`, `ov-run`, `ov-worker-stop`, `ov-restart`. Look for in-place clean-text edit: contenteditable, Save text, inline pencil on `text`, textarea for clean text.
5. **Expected observable:** Absent on every screen. Correction is Open source config / Start re_extract / Start re-ingest only. `named_party` on legal is read-only.
6. **Pass / fail:** Pass if absent. Fail if the forbidden control exists.
7. **On fail:** Defect (Engineer).

#### QA-F20

1. **ID:** QA-F20
2. **Spec trace:** F20; section 2 Out of scope; section 8 hard exclusions; A15
3. **Preconditions:** Four screens + named overlays.
4. **Steps:** Walk every screen and overlay for: side picker, call, ledger, confidence, place-a-call, venue picker, Yes/No/NO_CALL, stake/size, Kalshi/Polymarket as primary controls, live-bet-window object/toggle.
5. **Expected observable:** Absent on every screen. Ready/not-ready are health flags, not a side. No confidence field. Venue footnote is not a picker.
6. **Pass / fail:** Pass if all absent. Fail if any exists.
7. **On fail:** Defect (Engineer).

#### QA-F21

1. **ID:** QA-F21
2. **Spec trace:** F21; R-UI-11; `ov-delete`; copy `This deletes the clean base. Type DELETE to confirm.` Typed DELETE is not Restart the app (CR-QA-2).
3. **Preconditions:** Fate. Control, Sources danger zone. Do not confirm typed DELETE in a Draft execution (execution illegal until Approved). When Approved and executed, Cancel path is required; Confirm path is specified and destructive. Restart the app is a different control.
4. **Steps:**
   1. Confirm **Restart the app** is a separate control from `Delete the base…`.
   2. `Delete the base…` → `ov-delete`. Confirm disabled until the field matches `DELETE` (exact).
   3. Type a mismatch. Confirm stays disabled.
   4. Cancel. Records: clean records still resolve. Base remains.
   5. (Approved execution only, operator-intended) Type `DELETE` and Confirm: clean base deleted. That outcome is specified; do not treat leftover clean records as pass. That emptied store is not empty first boot (CR-USER-1). Typed DELETE is not a fail of QA-A39 or QA-F53. Typed DELETE is not a go-live path to factory-empty first boot.
5. **Expected observable:** Typed confirm required. Cancel leaves the base. Failed jobs never delete the base (this is an operator action only). Typed DELETE is not restart.
6. **Pass / fail:** Pass if typed confirm is required, Cancel leaves the base, and Restart is not this overlay. Fail if delete proceeds without exact `DELETE`, Cancel deletes, or Restart the app uses typed DELETE.
7. **On fail:** Defect (Engineer).

#### QA-F22

1. **ID:** QA-F22
2. **Spec trace:** F22; R-UI-11; delete of clean records: confirm, not typed
3. **Preconditions:** At least one clean record if testing the confirm-and-cancel path.
4. **Steps:**
   1. Control Sources (or footer): `Delete clean records…`.
   2. Confirm overlay (not typed); copy names the filter/selection. Cancel.
   3. Records: those records still resolve.
5. **Expected observable:** Confirm required. Cancel leaves records. Not the same overlay as base delete (`ov-delete` typed) and not Restart the app (`ov-restart`).
6. **Pass / fail:** Pass if confirm required and Cancel does not delete. Fail if silent delete or typed DELETE is required for subset (Spec: not typed).
7. **On fail:** Defect (Engineer).

#### QA-F23

1. **ID:** QA-F23
2. **Spec trace:** F23; A8; CR-E2; `ov-disabled`; section 5.6 Disabled source: `not scheduled`, even if it has a cadence
3. **Preconditions:** A source `disabled`. Prefer a source that has a cadence so disable is not confused with exempt.
4. **Steps:**
   1. Manual Run for that source. `ov-disabled` required even if params valid. Copy: `This source is disabled. Scheduler will not run it. Manual Run still enqueues. Continue?`
   2. Cancel: no job. Confirm: enqueues (then R-JOB-9). Manual Run never waits for the schedule. Fate can run any source on demand the same day.
   3. Next scheduled run remains the exact copy `not scheduled`. Not `scheduler skip`. Not a 09:00 datetime. Scheduler does not enqueue it, including when Probe clock is Set to weekday 09:00 ET.
5. **Expected observable:** Confirm required. Scheduler still skips it (does not enqueue). Next-run copy is `not scheduled`. Manual Run never waits for the schedule.
6. **Pass / fail:** Pass if confirm + next-run exact `not scheduled` + scheduler does not enqueue. Fail if Manual Run skips confirm, if next-run copy is `scheduler skip` or a datetime, or if scheduler enqueues disabled.
7. **On fail:** Defect (Engineer).

#### QA-F24

1. **ID:** QA-F24
2. **Spec trace:** F24; R-UI-11; section 5.5 `re_index` and `refresh_preferences` take the same global write lock as global `re_extract`; `ov-reindex`; `ov-refresh`
3. **Preconditions:** Fate.
4. **Steps:**
   1. Run job type `re_index`. Source hidden; value `global`. Overlay `ov-reindex`: `Rebuild the index from all stored clean records. Confirm.` Cancel: no job. Confirm: job created `queued`/`running` as worker allows.
   2. Run type `refresh_preferences`. Overlay `ov-refresh`: `Rebuild derived preferences from current clean records. Confirm.` Cancel: no job.
   3. While global `re_index` or `refresh_preferences` is `queued` or `running`, start a source write-scoped job: `ov-dup` (same global write lock). Queue-behind waits until every touched source is free.
5. **Expected observable:** Confirm required. Same global write lock as global `re_extract`. Packet leftover “Global jobs are not this mutex” is struck.
6. **Pass / fail:** Pass if both confirms exist and global lock occupies every source. Fail if they start without confirm or do not block source writes.
7. **On fail:** Defect (Engineer).

#### QA-F25

1. **ID:** QA-F25
2. **Spec trace:** F25; CR-QA-5; A29; F43; section 5.8 Job-level network/auth/parse failure: `failed`, readable error, no silent retry loop; S6
3. **Preconditions:** Control, Sources, Connector `#connector-{source}` with values `ok`, `network`, `auth`, `parse`. Worker available. Pick a source and a fetch type.
4. **Steps:**
   1. Set Connector to `network`. Run a fetch job for that source. Worker executes. Open `ov-job`: status `failed`, error exactly `network`. S6. No silent retry loop. Setting Connector to `ok` does not resume.
   2. Repeat for `auth` and for `parse` (may use the same source or another; A29 is `auth` on `books`).
   3. Jobs history: no additional job ids created with same params without Fate Retry. Clean base still present.
5. **Expected observable:** `failed`, readable error exactly `network` or `auth` or `parse` as set. No silent retry loop. S6 applies. Connector is the only operator way to take this class.
6. **Pass / fail:** Pass if each not-ok Connector value stores `failed` with that exact error, no silent retry, S6. Fail if silent new jobs appear, error is missing or not exact, the base is deleted, or setting `ok` resumes the same id.
7. **On fail:** Defect (Engineer). Do not leave network/auth/parse induction as an open hole.

#### QA-F26

1. **ID:** QA-F26
2. **Spec trace:** F26; section 5.3 Sources not on the configured list are refused; adding a source is operator configuration, not a job side effect; configured ids in section 5.4
3. **Preconditions:** Control, Run job source control, including Operator item source.
4. **Steps:**
   1. Open source select on incremental/backfill/targeted Query / Operator item / `re_extract`. List must be exactly: `whitehouse_remarks`, `whitehouse_actions`, `app`, `factbase`, `federal_register`, `truth_social`, `x_personal`, `campaign`, `books`, `interviews`, `legal` (plus `global` where `re_extract` allows).
   2. Confirm there is no Run-job control that adds a twelfth source as a job side effect.
   3. Control, Sources lists the same ids; enable/disable is configuration, not a job type.
5. **Expected observable:** Job cannot target a source not on the configured list. Adding a source is configuration, not a job side effect.
6. **Pass / fail:** Pass if only configured ids are targetable. Fail if a job can be started for an unlisted source id.
7. **On fail:** Defect (Engineer).

#### QA-F27

1. **ID:** QA-F27
2. **Spec trace:** F27; CR-QA-8; A32; F46; section 2 The administration as a legal named party out of scope; section 5.4 `legal` named party is Donald Trump, or a presidential action already stored under `whitehouse_actions` / Federal Register; S12 `named_party` is a closed clean field
3. **Preconditions:** Operator item is the Spec path. Control, Run, targeted Operator item. Optional field `named_party`.
4. **Steps:**
   1. Operator item source `legal`, kind `legal`, channel `legal`, locator and text filled, `named_party` `the administration`. Submit.
   2. Records filter kind=`legal`. Confirm none is ingested as `legal` clean whose named party is only the administration.
   3. Quarantine: the item is not a clean `legal` row. `named_party` is readable as a closed field on clean legal records (QA-A38); it is not missing from the closed field list.
5. **Expected observable:** Not ingested as `legal` clean. F46 is the Operator item primary. Closed field `named_party` is how named party is observed.
6. **Pass / fail:** Pass if no clean `legal` record is only the administration. Fail if one is, or if the item is silently dropped.
7. **On fail:** Defect (Engineer). Do not leave named party as an open hole; `named_party` is a closed field and Operator item is the Spec path.

#### QA-F28

1. **ID:** QA-F28
2. **Spec trace:** F28; CR-QA-3; A17; A27; F41; section 6 If a read action cannot run (control down or data unavailable): that control shows an inline error; the app does not invent records
3. **Preconditions:** Control, Operator, Records reads (`#records-reads`). Default `available`. This is the only operator way to take section 6 down.
4. **Steps:**
   1. Set Records reads to `down`.
   2. On Records, use Search, open record / prior version (GetRecord), Open preference (GetPreference), and Export retrieval set.
   3. Read each control inline error. Confirm no invented rows. Confirm no out-of-app failure surface is required by this Spec.
   4. Set `available` and confirm the four actions run as specified.
5. **Expected observable:** Each Records control shows its cannot-run copy (exact strings on QA-F41). App does not invent records.
6. **Pass / fail:** Pass if the down control errors inline and does not invent records. Fail if it invents records or fails silently with fake rows. Do not pass by skipping Records reads down.
7. **On fail:** Defect (Engineer).

#### QA-F29

1. **ID:** QA-F29
2. **Spec trace:** F29; CR-QA-4; A28; F42; section 8 2.2 Load error: Inline error + Retry. Data already on screen stays until replaced. Induced only by Fail next load
3. **Preconditions:** Control, Operator, Fail next load (`#fail-next-load`) choice plus Set. This is the only operator way to induce F29.
4. **Steps:**
   1. Set Fail next load to a screen (A28 uses Dashboard). Open that screen.
   2. Read the error and Retry control.
   3. If data was already shown, confirm it stays until replaced.
   4. Retry loads the screen and clears the fail.
5. **Expected observable:** Inline error `{Screen} failed to load` + Retry. Data already shown stays until replaced. Dashboard-specific copy when Dashboard fails: `Dashboard failed to load` + Retry.
6. **Pass / fail:** Pass if those hold when Fail next load is set and the screen is opened. Fail if the screen wipes data without Retry or shows a marketing empty. Do not pass if Fail next load is unused.
7. **On fail:** Defect (Engineer).

#### QA-F30

1. **ID:** QA-F30
2. **Spec trace:** F30; empty copy per screen; never a marketing illustration; CR-QA-11 empty topic copy only when the topic list is empty
3. **Preconditions:** Fate can set filters that match nothing. Topic list may be emptied by Remove.
4. **Steps:**
   1. Control, Jobs: filters that match nothing. Copy: `No jobs match these filters.`
   2. Records: filters that match nothing. Copy: `No clean records match.` Export disabled, helper `Nothing to export.`
   3. Quarantine: filter with no items. `No quarantined items.` or `No {reason} items.`
   4. Dashboard topic × channel with topic list empty: `No topic × channel rows. Add topics in Control → Vocabularies, then ingest.` After Add, that copy is gone (QA-A35).
   5. Confirm no marketing illustration on these empties.
5. **Expected observable:** Empty copy. No marketing illustration. Topic empty copy only when the topic list is empty.
6. **Pass / fail:** Pass if specified empty copy appears and no marketing illustration. Fail if illustration, missing empty copy, or empty topic copy remains after a topic is Added.
7. **On fail:** Defect (Engineer).

#### QA-F31

1. **ID:** QA-F31
2. **Spec trace:** F31; S4; A18; F50; CR-QA-7 Empty Save; empty pin is match-none, not match-all; CR-E1 `enabled` independent of `blocked`
3. **Preconditions:** Official X pin empty and/or official Truth Social pin empty via Empty Save (`#pin-x-save` / `#pin-ts-save`).
4. **Steps:**
   1. Vocabularies: Empty Save a pin. Helper: `Clean written_social attribution must match these pins. A lookalike is quarantined.`
   2. Dashboard: `x_personal` and/or `truth_social` pill `blocked: empty pin`. Enabled is still Fate’s enable/disable, not auto-disabled by empty pin.
   3. Note freshness. Run fetch for that source. Job counts / Quarantine: fetched items field-fail (pin required). Records: no clean `written_social` from that source.
   4. Freshness clocks unchanged.
   5. Operator item `written_social` or source `truth_social` / `x_personal` while no pin is set: refuse copy `A written_social Operator item is refused if no pin is set.` No job. Not F2 (QA-F50).
5. **Expected observable:** `blocked: empty pin`. No clean `written_social` from it. Fetched items field-fail (pin required). Freshness does not move. Empty pin is not match-all. Empty Save is this path.
6. **Pass / fail:** Pass if all hold. Fail if empty pin writes clean `written_social` (match-all), or if Operator item proceeds without a pin.
7. **On fail:** Defect (Engineer).

#### QA-F32

1. **ID:** QA-F32
2. **Spec trace:** F32; S6; S9; A12; A22
3. **Preconditions:** A fetch job reaches `failed` / `cancelled` / `worker_lost` after some clean writes and with in-flight remaining. Stop worker is a named `worker_lost` path.
4. **Steps:**
   1. `ov-job`: equation; `written`+`updated` stayed set; in-flight in `quarantined`.
   2. GetRecord stayed `record_id`s; provenance producing job = that job id.
   3. Records Search: in-flight absent (not in index). Quarantine: `job_stopped`.
5. **Expected observable:** Stayed clean still resolvable under that job id. In-flight are `quarantined`/`job_stopped`, absent from clean and from the index. Job counts add up (S9).
6. **Pass / fail:** Pass if stayed resolvable, in-flight quarantined not indexed, equation holds. Fail if leftover or stayed missing.
7. **On fail:** Defect (Engineer).

#### QA-F33

1. **ID:** QA-F33
2. **Spec trace:** F33; S7 closed pair table; A19; A30; F44; section 5.7; CR-QA-6 Operator item is the Spec path to command an off-S7 pair
3. **Preconditions:** Jobs may write from any configured source. Encode the S7 table exactly. Operator item source `whitehouse_remarks`, kind `social`, channel `written_social` is the named off-S7 command. Also inspect every clean write.
4. **Steps:**
   1. Submit the named Operator item off-S7 pair. Confirm field-fail, not clean, `fetched` = 1 (QA-F44 / QA-A30).
   2. For clean records, group by `source` and read `(kind, channel)`.
   3. Confirm each clean pair is in the S7 set for that source (table below). Any pair not in the set: Quarantine field-fail, not clean, Accept disabled.
5. **Expected observable — S7 table (exact):**

| Source | Legal pairs |
| --- | --- |
| `whitehouse_remarks` | `(remark, spoken)` |
| `whitehouse_actions` | `(decision, written_official)`, `(staffing, written_official)` |
| `app` | `(remark, spoken)`, `(decision, written_official)`, `(writing, written_official)` |
| `factbase` | `(remark, spoken)` |
| `federal_register` | `(decision, written_official)` |
| `truth_social` | `(social, written_social)` |
| `x_personal` | `(social, written_social)` |
| `campaign` | `(remark, spoken)`, `(writing, other)` |
| `books` | `(writing, other)` |
| `interviews` | `(interview, spoken)` |
| `legal` | `(legal, legal)` |

Write whose `(kind, channel)` is not in this set is field-fail. Not clean. No other pairs.

6. **Pass / fail:** Pass if no clean off-set pair exists and the named Operator item off-S7 write is field-fail. Fail if a clean record has a pair outside the table.
7. **On fail:** Defect (Engineer). Do not leave forcing an off-S7 pair as an open hole.

#### QA-F34

1. **ID:** QA-F34
2. **Spec trace:** F34; S8; A20; A21; `whitehouse_actions`, `federal_register`, `books`, `legal` do not cover a counted channel
3. **Preconditions:** Dashboard source health and topic × `spoken` rows (Add a topic if needed).
4. **Steps:**
   1. Observe `books` and `legal`: cadence `none` / `no cadence`; never cadence-stale; they do not cover `spoken` or `written_social`.
   2. Make or observe: all S8 spoken covering sources not cadence-stale; `books` and `legal` never succeeded or old. Spoken failed clause is not `stale covering sources` because of books/legal.
   3. Make or observe: all S8 spoken covering sources are cadence-stale; books/legal fresh. Spoken is `not-ready` from stale covering sources anyway — books/legal freshness did not save it.
5. **Expected observable:** `books` or `legal` never participate in cadence-stale for not-ready. Spoken not-ready-from-stale uses only `whitehouse_remarks`, `app`, `factbase`, `campaign`, `interviews`.
6. **Pass / fail:** Pass if books/legal cannot decide spoken stale-not-ready. Fail if they do.
7. **On fail:** Defect (Engineer).

#### QA-F35

1. **ID:** QA-F35
2. **Spec trace:** F35; S6; S9; A22; Accept disabled on `job_stopped`
3. **Preconditions:** A running fetch stopped with in-flight items that had no other gate fail. Cancel, Connector fail, or Stop worker are named stop paths.
4. **Steps:**
   1. Stop the job (`cancelled` / `failed` / `worker_lost`).
   2. Quarantine those items: field-fail, named rule `job_stopped`. Count them in that job `quarantined`.
   3. Accept disabled. Helper for field-fail. Not missing from Quarantine (not a silent drop).
   4. S9 equation: they are not a sixth term.
   5. A later job for the same locator may write them clean if they then pass the gate — optional follow-on; not required to pass F35.
5. **Expected observable:** Field-fail `job_stopped`. Counts as `quarantined`. Accept disabled. Not a silent drop.
6. **Pass / fail:** Pass if in-flight appear as `job_stopped` field-fail in `quarantined` with Accept disabled and equation holds. Fail if they vanish or become clean.
7. **On fail:** Defect (Engineer).

#### QA-F36

1. **ID:** QA-F36
2. **Spec trace:** F36; CR-USER-1; remaining CR-E1 (Fate’s disable/enable persists across Restart the app; factory is not reapplied on restart of a non-empty instance; no wizard; a blocked reason does not force `disabled`); A23; A16; Restart the app is CR-QA-2
3. **Preconditions:** The production instance as it sits (non-empty is expected). Fate can disable at least one source. Restart method is Restart the app (`ov-restart`), not typed DELETE. Empty first boot is not this case and is out of scope. Typed DELETE is not restart and is not this check.
4. **Steps:**
   1. Control, Sources. Disable one source Fate currently has enabled (for example `campaign` if it is enabled; otherwise any enabled source). Confirm it shows `disabled`. Next scheduled run on that row is exact `not scheduled` if it has a cadence (QA-A8 / QA-F37).
   2. Restart the app (`#btn-restart`). Overlay `ov-restart` (not typed). Confirm. Do not send typed DELETE.
   3. After return: Open Control, Sources and Dashboard. Read Enabled on the source Fate disabled: it remains `disabled`. Factory is not reapplied. No wizard.
   4. Confirm a blocked reason still does not force `disabled` on sources Fate did not disable.
   5. Restore: enable the source Fate disabled for this check.
5. **Expected observable:** That source stays `disabled`. Factory is not reapplied. No wizard. A blocked reason does not force `disabled`. Empty first boot is not this case. Restart the app is not a wipe.
6. **Pass / fail:** Pass if Restart the app leaves the Fate-disabled source `disabled`, factory is not reapplied, and no wizard appears. Fail if Restart re-enables a source Fate disabled, if factory is reapplied on this non-empty instance, or if a wizard appears. Do not Block F36 for missing empty first-boot. Do not collapse this with QA-A16 (base persistence), QA-A23 (current-instance no-wizard / blocked independence), QA-A39 (no wipe control), or QA-F53. Do not treat typed DELETE as this path.
7. **On fail:** Defect (Engineer). Empty first-boot observation is out of scope (CR-USER-1). Do not invent a wipe.

#### QA-F37

1. **ID:** QA-F37
2. **Spec trace:** F37; CR-E2; CR-QA-10; A24; A8; F23; section 5.6 Exempt `books` and `legal`: `not scheduled`; Disabled source: `not scheduled`, even if it has a cadence; scheduler shall not enqueue a disabled source or an exempt source
3. **Preconditions:** Fate. Control, Sources. `books` and `legal` exist. At least one cadence source can be disabled. Chrome clock is ET. Probe clock may be Set to weekday 09:00 ET to observe that exempt/disabled still do not enqueue.
4. **Steps:**
   1. Control, Sources. `books` row: Cadence `none`. Next scheduled run exact copy `not scheduled`. Not a 09:00 datetime. Not `scheduler skip`.
   2. `legal` row: Cadence `none`. Next scheduled run exact copy `not scheduled`.
   3. Confirm Manual Run remains on both (opens `ov-run` prefilled incremental). Scheduler does not enqueue `books` or `legal`, including on an S11 tick.
   4. Disable an enabled daily or weekly source. Next scheduled run exact copy `not scheduled`, even though it has a cadence. Scheduler does not enqueue it. Manual Run still possible after `ov-disabled` (QA-F23 / QA-A8).
   5. Re-enable that source. Next scheduled run returns to the CR-E2 datetime (09:00 ET per daily/weekly rule in QA-A24), not `not scheduled`.
   6. Walk Dashboard, Control, Records, Quarantine, and named overlays: next-run display, where shown, is only a datetime in America/New_York or the exact copy `not scheduled`. Packet `scheduler skip` as next-run copy is struck.
5. **Expected observable:** Copy is `not scheduled` for `books`, for `legal`, and for a disabled source. Scheduler does not enqueue them. Manual Run remains. Closed two-value display: datetime in America/New_York, or exact copy `not scheduled`. CR-E2.
6. **Pass / fail:** Pass if those three cases show exact `not scheduled` and the scheduler does not enqueue them. Fail if `books`/`legal`/disabled show a next-run datetime, if copy is `scheduler skip`, or if the scheduler enqueues them.
7. **On fail:** Defect (Engineer).


#### QA-F38

1. **ID:** QA-F38
2. **Spec trace:** F38; CR-QA-1; A12; A25; F1; F39; section 5.9; `ov-worker-stop`
3. **Preconditions:** A job is `running`. Worker pill `available`. Chrome Stop worker (`#worker-stop`).
4. **Steps:**
   1. Stop worker. Read `ov-worker-stop` copy.
   2. Confirm.
   3. Read worker pill, banner on every screen, stored status of the previously running job, Jobs list for any `running` row.
5. **Expected observable:** `ov-worker-stop`. Confirm applies S5. Pill `not available`. Banner. Stored `failed` / `worker_lost`. No `running` row. Copy: `Stop the worker? Running jobs will fail with worker_lost.`
6. **Pass / fail:** Pass if overlay, copy, S5, pill, banner, stored failed/worker_lost, and no running row hold. Fail if Stop worker is missing, copy is wrong, or S5 is not applied.
7. **On fail:** Defect (Engineer). This check is not collapsed into QA-A12 or QA-F1.

#### QA-F39

1. **ID:** QA-F39
2. **Spec trace:** F39; CR-QA-1; A12; A25; F1; F38; Start worker
3. **Preconditions:** Worker pill `not available` after Stop worker. At least one `worker_lost` job exists. Prefer a `queued` job waiting.
4. **Steps:**
   1. Chrome shows Start worker (`#worker-start`), not Stop worker.
   2. Start worker.
   3. Read worker pill and banner. Open the `worker_lost` job. Watch the next `queued` job if any.
5. **Expected observable:** Pill `available`. Banner gone. `worker_lost` jobs are not resumed. Next `queued` job may run. A SAMPLE `running` row shown after Start worker in a mock is preview only and is not a resumed `worker_lost` job.
6. **Pass / fail:** Pass if pill available, banner gone, and `worker_lost` is not resumed. Fail if Start worker restores the same running id or leaves the banner up.
7. **On fail:** Defect (Engineer).

#### QA-F40

1. **ID:** QA-F40
2. **Spec trace:** F40; CR-QA-2; A16; A26; A33; `ov-restart`
3. **Preconditions:** Clean `record_id`s exist. Note enable/disable, topics, pins, allowlist. Control Sources danger **Restart the app**.
4. **Steps:**
   1. Open Restart the app. Read `ov-restart` copy. Confirm it is not typed.
   2. Confirm. If a job was `running`, S5 applies first.
   3. After return: same `record_id` values, same enable/disable, topics, pins, and allowlist. Worker `available`.
   4. Confirm typed DELETE (`ov-delete`) is a different path and was not used.
5. **Expected observable:** `ov-restart`. Copy `Restart the app? The knowledge base stays. Running jobs fail with worker_lost.` Confirm applies S5, then instance returns with same `record_id` values and same enable/disable, topics, pins, and allowlist. Worker `available`. Typed DELETE is not this path.
6. **Pass / fail:** Pass if restart overlay, S5, persistence, and worker available hold. Fail if typed DELETE is used as restart, records vanish, or worker does not return available.
7. **On fail:** Defect (Engineer).

#### QA-F41

1. **ID:** QA-F41
2. **Spec trace:** F41; CR-QA-3; A27; F28; A17
3. **Preconditions:** Control, Operator, Records reads = `down`. Prefer existing clean records, a topic, and a search result so each action would otherwise run.
4. **Steps:**
   1. Records. Search. Read copy.
   2. GetRecord (open a row or prior version). Read copy.
   3. GetPreference (Open preference). Read copy.
   4. Export retrieval set. Read copy.
   5. Confirm no invented records on any of the four.
5. **Expected observable:** `Search cannot run.` `GetRecord cannot run.` `GetPreference cannot run.` `Export cannot run.` No invented records. While `available`, those four actions run as specified.
6. **Pass / fail:** Pass if each of the four exact copies appears and no invented records. Fail if any action invents rows, uses other copy, or still runs while down.
7. **On fail:** Defect (Engineer).

#### QA-F42

1. **ID:** QA-F42
2. **Spec trace:** F42; CR-QA-4; A28; F29
3. **Preconditions:** Control, Operator, Fail next load choice Dashboard / Control / Records / Quarantine + Set. This check covers all four screens. A28 is Dashboard only.
4. **Steps:** For each screen in turn:
   1. Set Fail next load to that screen.
   2. Open that screen.
   3. Read `{Screen} failed to load` plus Retry. Data already shown stays until replaced.
   4. Retry loads the screen and clears the fail. A further open is not the error unless Set again.
5. **Expected observable:** Next open of the chosen screen shows `{Screen} failed to load` plus Retry. Retry loads and clears the fail. Copy uses the screen name: `Dashboard failed to load`, `Control failed to load`, `Records failed to load`, `Quarantine failed to load`.
6. **Pass / fail:** Pass if all four screens match. Fail if any screen skips the error, Retry does not clear, or a screen other than the chosen one fails.
7. **On fail:** Defect (Engineer). Missing a screen branch is not a pass of that branch.

#### QA-F43

1. **ID:** QA-F43
2. **Spec trace:** F43; CR-QA-5; A29; F25; S6
3. **Preconditions:** Connector on each source row: `ok` (default), `network`, `auth`, `parse`. Worker available. Next fetch job for that source that a worker executes is the subject.
4. **Steps:**
   1. Confirm Connector exists on each of the eleven source rows (`#connector-{source}`).
   2. Set Connector to `network` on a source. Run a fetch job. Worker executes. Stored `failed`, error exactly `network`. S6. No silent retry.
   3. Set Connector to `auth` on a source (A29 uses `books`). Same stored `failed` / `auth`.
   4. Set Connector to `parse` on a source. Same stored `failed` / `parse`.
   5. Set Connector back to `ok`. Confirm the failed job is not resumed. A fetch that returns nothing while `ok` is `succeeded_empty` (QA-F6), not this fail.
5. **Expected observable:** Job stored `failed` with that exact readable error `network` or `auth` or `parse`. S6. No silent retry loop. Setting back to `ok` does not resume.
6. **Pass / fail:** Pass if each not-ok value fails with that exact error and does not resume. Fail if Connector is missing on a source row, error is not exact, silent retry occurs, or `ok` resumes the failed id.
7. **On fail:** Defect (Engineer).

#### QA-F44

1. **ID:** QA-F44
2. **Spec trace:** F44; CR-QA-6; A19; A30; F33; S7
3. **Preconditions:** Targeted Operator item. Source `whitehouse_remarks`, kind `social`, channel `written_social`, locator and text filled. Worker available.
4. **Steps:**
   1. Submit the Operator item.
   2. Open the job. Read `fetched`. Open Quarantine. Records Search that locator.
5. **Expected observable:** Field-fail F33. Not clean. `fetched` = 1.
6. **Pass / fail:** Pass if field-fail, not clean, fetched=1. Fail if clean or fetched is not 1.
7. **On fail:** Defect (Engineer). This check is not collapsed into QA-F33.

#### QA-F45

1. **ID:** QA-F45
2. **Spec trace:** F45; CR-QA-7; F11; A31
3. **Preconditions:** Official pin set for `truth_social` or `x_personal`. Operator item pin match `lookalike`.
4. **Steps:**
   1. Submit Operator item for that source with pin match `lookalike` and the five required fields filled.
   2. Records and Quarantine for that locator.
5. **Expected observable:** F11. Quarantined, not clean.
6. **Pass / fail:** Pass if quarantined not clean. Fail if clean.
7. **On fail:** Defect (Engineer). This check is not collapsed into QA-F11.

#### QA-F46

1. **ID:** QA-F46
2. **Spec trace:** F46; CR-QA-8; F27; A32
3. **Preconditions:** Operator item source `legal`, `named_party` `the administration`, kind `legal`, channel `legal`, locator and text filled.
4. **Steps:**
   1. Submit.
   2. Records kind=`legal`. Quarantine that locator.
5. **Expected observable:** F27. Not ingested as `legal` clean.
6. **Pass / fail:** Pass if not clean legal. Fail if ingested as legal clean.
7. **On fail:** Defect (Engineer). This check is not collapsed into QA-F27.

#### QA-F47

1. **ID:** QA-F47
2. **Spec trace:** F47; CR-QA-10; S11; A24; A34; F51
3. **Preconditions:** Control, Operator, Probe clock. At least one enabled daily source and one enabled weekly source.
4. **Steps:**
   1. Probe clock Set Saturday 09:00 ET. Read next-run on enabled cadence sources. Confirm no new `incremental` with `triggered_by` `schedule`.
   2. Probe clock Set Sunday 09:00 ET. Same observations.
   3. Next-run is Monday 09:00 ET. Saturday and Sunday never enqueue.
5. **Expected observable:** Next-run Monday 09:00 ET. Scheduler does not enqueue. Saturday and Sunday never receive a scheduled run.
6. **Pass / fail:** Pass if weekend Set does not enqueue and next-run is Monday 09:00 ET. Fail if Saturday or Sunday enqueues or shows a weekend next-run datetime.
7. **On fail:** Defect (Engineer).

#### QA-F48

1. **ID:** QA-F48
2. **Spec trace:** F48; CR-QA-11; A14; A35; F16
3. **Preconditions:** Topic list empty so the counted-channel table is empty of rows. Empty copy is showing.
4. **Steps:**
   1. Confirm empty copy: `No topic × channel rows. Add topics in Control → Vocabularies, then ingest.`
   2. Add a topic. Do not ingest.
   3. Dashboard: one `spoken` row and one `written_social` row appear immediately.
   4. Remove the last topic. Confirm empty copy returns.
5. **Expected observable:** One `spoken` row and one `written_social` row appear immediately, usable 0, `not-ready`, failed clause `zero usable`. Ingest is not required. Removing the last topic returns the empty copy.
6. **Pass / fail:** Pass if rows appear immediately and empty copy returns after removing the last topic. Fail if ingest is required or empty copy is used while a topic exists.
7. **On fail:** Defect (Engineer). This check is not collapsed into QA-A35.

#### QA-F49

1. **ID:** QA-F49
2. **Spec trace:** F49; S10; A37; A4; F2
3. **Preconditions:** Control, Run, type `targeted`, mode Operator item.
4. **Steps:**
   1. Missing source: fill locator, text, kind, channel; leave source empty. Run. Copy. No job.
   2. Missing locator: fill the other four. Run. Copy. No job.
   3. Missing text: fill the other four. Run. Copy. No job.
   4. Missing kind: fill the other four. Run. Copy. No job.
   5. Missing channel: fill the other four. Run. Copy. No job.
5. **Expected observable:** Refused in place. Copy `Operator item needs source, locator, text, kind, and channel.` No job row. Not F2. Query copy is not shown.
6. **Pass / fail:** Pass if each missing required field refuses with that copy and no job. Fail if a job is created, if Query copy is used, or if only some of the five are required.
7. **On fail:** Defect (Engineer). Missing a required-field branch is not a pass of that branch.

#### QA-F50

1. **ID:** QA-F50
2. **Spec trace:** F50; S10; CR-QA-7; A18; F31
3. **Preconditions:** Official X pin and official Truth Social pin empty (Empty Save). Control, Run, targeted Operator item.
4. **Steps:**
   1. Operator item channel `written_social` with the five required fields filled. Run.
   2. Operator item source `truth_social` with the five required fields filled. Run.
   3. Operator item source `x_personal` with the five required fields filled. Run.
5. **Expected observable:** Refused in place. Copy `A written_social Operator item is refused if no pin is set.` No job row. Not F2.
6. **Pass / fail:** Pass if each of those three submits refuses with that copy and no job. Fail if a job is created or Query copy F2 is shown.
7. **On fail:** Defect (Engineer).

#### QA-F51

1. **ID:** QA-F51
2. **Spec trace:** F51; S11; CR-QA-10; A34; A24; F47
3. **Preconditions:** Probe clock. Enabled non-exempt sources due that weekday. Worker available enough for enqueue to be visible as `queued`. No occupant that would hide enqueue behind mutex reject.
4. **Steps:**
   1. Probe clock Set to a weekday 09:00 ET instant (A34 uses Monday 09:00).
   2. Observe enqueue `incremental` once for each enabled non-exempt source due that day. Then next-run advances.
   3. Remain frozen on that instant. Confirm no second enqueue.
   4. Weekday before 09:00 does not enqueue (A34 Monday 08:00). Saturday/Sunday never enqueue (F47).
5. **Expected observable:** Tick: enqueue `incremental` once for each enabled non-exempt source due that day, then advance next-run. Remaining frozen on that instant does not enqueue again (S11). Display of next-run is not that tick.
6. **Pass / fail:** Pass if one enqueue then advance, and frozen remainder does not enqueue again. Fail if no enqueue, repeated enqueue while frozen, or next-run display itself enqueues.
7. **On fail:** Defect (Engineer). This check is not collapsed into QA-A34.

#### QA-F52

1. **ID:** QA-F52
2. **Spec trace:** F52; S12; A9; A10; A38; CR-QA-8
3. **Preconditions:** Operator item source `legal`, kind `legal`, channel `legal`, locator and text filled, `named_party` absent (optional field left empty).
4. **Steps:**
   1. Submit. Open the job. Quarantine that locator. Records kind=`legal` for that locator.
   2. On a separate clean legal record (QA-A38), confirm operator can read `named_party` on `ov-record`, GetRecord, and Export.
5. **Expected observable:** Field-fail. Not clean. Not a silent drop. Operator can read `named_party` on clean legal via `ov-record`, GetRecord, and Export (S12). Absence is not omitted from quarantine; Accept disabled.
6. **Pass / fail:** Pass if absent `named_party` on a would-be legal item is field-fail not clean, and clean legal surfaces show the field. Fail if the item is clean, silently dropped, or clean legal omits the field.
7. **On fail:** Defect (Engineer).

#### QA-F53

1. **ID:** QA-F53
2. **Spec trace:** F53; CR-USER-1; A39; section 2 Out of scope; section 3 Non-goals (obtaining or inventing an empty first boot); Restart the app is not a wipe; Typed DELETE of the base is not a go-live path to factory-empty first boot
3. **Preconditions:** Fate on the production instance as it sits. Walk every screen and named overlay. Do not invent a wipe. Do not send typed DELETE as a go-live factory-empty path. Empty first-boot observation is out of scope.
4. **Steps:**
   1. Walk Dashboard, Control (all tabs including Operator), Records, Quarantine, and named overlays openable without confirming a destructive action: `ov-run`, `ov-job` if a job exists, `ov-record`, `ov-q-fieldfail`, `ov-q-hold` if present, `ov-worker-stop` (Cancel), `ov-restart` (Cancel), `ov-delete` (Cancel; do not type DELETE).
   2. Confirm an operator wipe or return-to-empty-first-boot control is absent on every screen.
   3. Confirm Restart the app is not a wipe.
   4. If typed DELETE of the base is present, treat it as the existing F21 typed confirm (Assumption A4 / packet 9.10). It is not a go-live path to factory-empty first boot and is not this fail if it is that existing F21 control. Do not treat F21 as an F53 fail.
   5. Do not invent a wipe to exercise F53. Absence is the pass.
5. **Expected observable:** Wipe / return-to-empty control absent on every screen. Restart the app is not a wipe. Typed DELETE of the base is not a go-live path to factory-empty first boot (CR-USER-1).
6. **Pass / fail:** Pass if wipe / return-to-empty is absent, Restart the app is not a wipe, and typed DELETE (if present) is the existing F21 confirm and is not treated as this fail. Fail if a wipe or return-to-empty-first-boot control exists (other than F21 typed DELETE). Do not fail F53 because F21 exists. Do not collapse this into QA-A39.
7. **On fail:** Defect (Engineer) if a wipe or return-to-empty control exists (other than typed DELETE). Do not invent a wipe. Absence is the pass. Empty first-boot observation is out of scope.

---

### 4.3 CR-QA and CR-USER-1 dedicated checks

Each CR-QA has a dedicated check. CR-USER-1 has a dedicated check. Primary A/F checks still exist and are not collapsed into these.

#### QA-CR-QA-1

1. **ID:** QA-CR-QA-1
2. **Spec trace:** CR-QA-1 Worker-down; primary QA-A12, QA-A25, QA-F1, QA-F38, QA-F39; S5; `#worker-stop` `#worker-start` `ov-worker-stop`
3. **Preconditions:** Worker pill `available`. Prefer a `running` job with some clean writes so S5 is visible. Chrome shows Stop worker.
4. **Steps:**
   1. Confirm chrome next to the worker pill has **Stop worker** while `available`, and **Start worker** while `not available`.
   2. Stop worker. Overlay `ov-worker-stop` copy exactly `Stop the worker? Running jobs will fail with worker_lost.`
   3. Confirm. Observe S5 immediately: banner on every screen; stored `running` jobs become stored `failed` with readable error `worker_lost`; display matches stored status; no row is `running`.
   4. Start worker. Pill `available`. Returning worker does not resume `worker_lost` jobs. It executes the next `queued` job, if any.
   5. Confirm Packet `#mock-worker-toggle` is this Stop / Start control. A switch that only paints `not available` and does not apply S5 is a fail.
5. **Expected observable:** Stop worker / Start worker exist and apply S5. Exact confirm copy. Immediate S5. Start worker does not resume. Switch-only-paint is a fail.
6. **Pass / fail:** Pass if the controls, copy, and S5 hold. Fail if the control is missing, copy is wrong, or only the pill paints.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-2

1. **ID:** QA-CR-QA-2
2. **Spec trace:** CR-QA-2 Restart method; primary QA-A16, QA-A26, QA-F40; `#btn-restart` `ov-restart`
3. **Preconditions:** A clean `record_id` exists. Note enable/disable, topics, occasions, pins, allowlist.
4. **Steps:**
   1. Control Sources danger zone: **Restart the app**.
   2. Overlay `ov-restart` (not typed) copy exactly `Restart the app? The knowledge base stays. Running jobs fail with worker_lost.`
   3. Confirm. S5 applies to any `running` job, then the instance returns with worker `available`, the same knowledge base, the same `record_id` values, and Fate’s enable/disable, topics, occasions, pins, and allowlist as they were.
   4. Confirm typed `DELETE` of the base is not a restart. Restart the app is not a wipe. There is no operator control that returns a used instance to empty first boot. Empty first-boot observation is out of scope (CR-USER-1). Dedicated no-wipe checks are QA-A39 and QA-F53 and are not collapsed into this check.
5. **Expected observable:** Restart the app is the named path. Exact copy. S5 then return with same KB, ids, config, worker available. Typed DELETE is not this path. Restart the app is not a wipe.
6. **Pass / fail:** Pass if those hold. Fail if Restart is typed DELETE or persistence fails. Do not fail CR-QA-2 because typed DELETE exists as F21.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-3

1. **ID:** QA-CR-QA-3
2. **Spec trace:** CR-QA-3 Section-6 down; primary QA-A17, QA-A27, QA-F28, QA-F41; `#tab-operator` `#records-reads`
3. **Preconditions:** Control Operator tab. Records reads default `available`.
4. **Steps:**
   1. Control, Operator. Records reads values `available` and `down`. Default `available`.
   2. Set `down`. On Records, Search, GetRecord, GetPreference, ExportRetrievalSet each show an inline error and do not invent records. Copy: `Search cannot run.` `GetRecord cannot run.` `GetPreference cannot run.` `Export cannot run.`
   3. Set `available`. Those four actions run as specified.
5. **Expected observable:** Records reads is the only operator way to take section 6 down. Exact four copies while down. No invented records. Available runs as specified.
6. **Pass / fail:** Pass if the control, copies, and available/down behavior hold. Fail if down invents records or a different control is required.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-4

1. **ID:** QA-CR-QA-4
2. **Spec trace:** CR-QA-4 Load-error induction; primary QA-A28, QA-F29, QA-F42; `#fail-next-load` `#fail-next-load-set`
3. **Preconditions:** Control Operator tab. Fail next load choice Dashboard, Control, Records, or Quarantine, and Set.
4. **Steps:**
   1. For each of the four screens: Set, open that screen, read `{Screen} failed to load` plus Retry, Retry loads and clears.
   2. Confirm this is the only operator way to induce F29.
5. **Expected observable:** Next open of the chosen screen shows `{Screen} failed to load` plus Retry. Retry loads and clears the fail. Data already shown stays until replaced.
6. **Pass / fail:** Pass if all four screens match. Fail if Fail next load is missing or Retry does not clear.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-5

1. **ID:** QA-CR-QA-5
2. **Spec trace:** CR-QA-5 Connector; primary QA-A29, QA-F25, QA-F43; `#connector-{source}`
3. **Preconditions:** Control Sources. Each of the eleven rows has Connector. Worker available for fetch execution.
4. **Steps:**
   1. Confirm Connector values `ok`, `network`, `auth`, `parse` on each source row. Default `ok`.
   2. Next fetch job for a source that a worker executes, if Connector is not `ok`, is stored `failed` with readable error exactly `network`, `auth`, or `parse`. S6 applies. No silent retry loop.
   3. Setting Connector back to `ok` does not resume the failed job.
   4. A fetch that returns nothing while Connector is `ok` is `succeeded_empty`.
5. **Expected observable:** Connector on each source. Exact error tokens. S6. No silent retry. No resume. Empty-in-scope while `ok` is `succeeded_empty`.
6. **Pass / fail:** Pass if Connector exists on every source and not-ok fails with the exact token. Fail if a source row lacks Connector or error is not exact.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-6

1. **ID:** QA-CR-QA-6
2. **Spec trace:** CR-QA-6 Off-S7 extract command; primary QA-A19, QA-A30, QA-F33, QA-F44; `#targeted-mode`; S10
3. **Preconditions:** Control Run, type `targeted`. Modes **Query** and **Operator item**.
4. **Steps:**
   1. Confirm two modes. Query is the existing targeted job (topic, query, occasion; at least one required). Operator item required fields are source, locator, text, kind, and channel.
   2. S10: Query’s topic/query/occasion require does not apply to Operator item. Missing source, locator, text, kind, or channel is refused in place with Operator item copy. Not F2.
   3. Submit of a complete Operator item creates a `targeted` job that processes exactly that one item (`fetched` = 1). Write-scoped. Same-source mutex applies.
   4. Operator item source `whitehouse_remarks`, kind `social`, channel `written_social`: field-fail F33, not clean, fetched=1.
5. **Expected observable:** Query vs Operator item exist. Off-S7 Operator item is field-fail not clean. fetched=1. Mutex applies. Query require does not fire on Operator item.
6. **Pass / fail:** Pass if modes, off-S7 field-fail, and fetched=1 hold. Fail if Operator item is missing or off-S7 is clean.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-7

1. **ID:** QA-CR-QA-7
2. **Spec trace:** CR-QA-7 Lookalike and pin-set; primary QA-A18, QA-A31, QA-F11, QA-F31, QA-F45, QA-F50; `#pin-x-save` `#pin-ts-save` `#pin-match-page`
3. **Preconditions:** Control Vocabularies. Official X pin and official Truth Social pin each have a text field and Save.
4. **Steps:**
   1. Save of a non-empty value sets that pin. Save of an empty value is F31 (`blocked: empty pin`).
   2. Operator item, when source is `truth_social` or `x_personal`, requires pin match `match` or `lookalike`. `match` means attribution equals the saved pin. `lookalike` means attribution does not equal the saved pin, and F11 applies: quarantined, not clean.
   3. A `written_social` Operator item, or an Operator item whose source is `truth_social` or `x_personal`, is refused in place if no pin is set, with copy `A written_social Operator item is refused if no pin is set.` That refuse is not F2 (S10).
5. **Expected observable:** Pin Save exists. Empty Save is F31. Lookalike is F11. No-pin Operator item refuse copy, not F2.
6. **Pass / fail:** Pass if Save, Empty Save, lookalike, and no-pin refuse hold. Fail if Empty Save is match-all or no-pin uses F2 copy.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-8

1. **ID:** QA-CR-QA-8
2. **Spec trace:** CR-QA-8 named_party and off-list mint; primary QA-A32, QA-A38, QA-F12, QA-F27, QA-F46, QA-F52; `#named-party-page` `#allowlist-add`; S12
3. **Preconditions:** Control Vocabularies allowlist Add/Remove. Operator item optional fields `named_party` and `outlet`.
4. **Steps:**
   1. Clean `legal` records store `named_party`. Clean legal requires `named_party` equal to `Donald Trump`. Absence on a would-be `legal` item is field-fail, not a silent drop (F52).
   2. S12: `ov-record` shows `named_party` when kind is `legal` (read-only). GetRecord includes `named_party`. Export includes `named_party` (empty on non-legal rows).
   3. Operator item `named_party` equal to `the administration` is F27: not ingested as `legal` clean.
   4. Operator item `outlet` not on the interview allowlist is F12: not clean. Fate adds an allowlist outlet from Vocabularies with text plus **Add**. Fate removes an outlet with **Remove**. Empty allowlist remains `blocked: empty allowlist`.
5. **Expected observable:** named_party required on legal; absence field-fail. Administration is F27. Off-list outlet is F12. Add/Remove work. S12 surfaces exist.
6. **Pass / fail:** Pass if those hold. Fail if named_party is omitted from operator surfaces or administration is stored clean legal.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-9

1. **ID:** QA-CR-QA-9
2. **Spec trace:** CR-QA-9 Stored UTC remainder; primary QA-A33, QA-A16
3. **Preconditions:** Displayed times exist (jobs, records, chrome clock). Restart the app is available.
4. **Steps:**
   1. Walk chrome, tables, drawers, overlays, banners: no UTC timestamp. Every displayed time is America/New_York with label `ET`.
   2. Restart the app. Same `record_id` values resolve and the same ET instants display.
   3. Confirm there is no UTC column for QA to read on a screen.
5. **Expected observable:** Stored times are UTC. No operator screen shows a UTC timestamp. After Restart, same record_ids and same ET instants. No UTC column.
6. **Pass / fail:** Pass if no UTC on screens and ET instants persist. Fail if a UTC column or UTC string appears, or ET instants change across Restart.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-10

1. **ID:** QA-CR-QA-10
2. **Spec trace:** CR-QA-10 CR-E2 clock branches; primary QA-A24, QA-A34, QA-F37, QA-F47, QA-F51; `#probe-clock` `#probe-clock-set` `#probe-clock-clear`; S11
3. **Preconditions:** Control Operator tab, Probe clock. Empty means the wall clock in America/New_York.
4. **Steps:**
   1. Empty Probe clock: chrome clock is wall clock ET. Set a datetime in America/New_York. While set, chrome clock, next-run display, and the scheduler use that instant. Clear probe clock returns to the wall clock.
   2. Display of next-run is not a scheduler tick.
   3. S11: Set to a weekday 09:00 America/New_York instant is the tick: enqueue `incremental` once for each enabled non-exempt source due that day, then advance next-run. Remaining on that frozen instant after the advance does not enqueue again. Setting to a weekday before 09:00 does not enqueue. Saturday and Sunday never enqueue (F47).
   4. Fate sets the Spec named instants: weekday before 09:00; weekday exactly 09:00; weekday after 09:00 including Friday after 09:00 → Monday 09:00; Monday before 09:00 weekly this Monday 09:00 no enqueue; Monday exactly 09:00 weekly tick then following Monday; Monday after 09:00 no enqueue following Monday; Saturday or Sunday next-run Monday 09:00 no enqueue.
5. **Expected observable:** Probe clock Set/Clear works. Display of next-run is not a tick. Named instants match enqueue and next-run. Exempt and disabled stay `not scheduled` and do not enqueue.
6. **Pass / fail:** Pass if Probe clock and the named instants hold. Fail if display of next-run enqueues, weekend enqueues, or frozen remainder enqueues again. A missing named instant is not a pass of that instant.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-QA-11

1. **ID:** QA-CR-QA-11
2. **Spec trace:** CR-QA-11 Topic row before ingest; primary QA-A14, QA-A35, QA-F16, QA-F48
3. **Preconditions:** Control Vocabularies topic list. Dashboard topic × counted channel table.
4. **Steps:**
   1. When the topic list is empty, Dashboard table copy is `No topic × channel rows. Add topics in Control → Vocabularies, then ingest.`
   2. Add a topic. Dashboard immediately shows one row per counted channel (`spoken`, `written_social`) for that topic, usable 0, health `not-ready`, failed clause `zero usable`. Ingest is not required to create those rows.
   3. Removing the last topic returns the empty copy.
5. **Expected observable:** Empty copy only when the topic list is empty. After Add, two rows immediately, usable 0, not-ready, `zero usable`. Ingest not required. Removing last topic returns empty copy.
6. **Pass / fail:** Pass if those hold. Fail if ingest is required or empty copy shows while a topic exists.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-CR-USER-1

1. **ID:** QA-CR-USER-1
2. **Spec trace:** CR-USER-1 Empty first-boot observation; section 5.9 CR-USER-1; remaining CR-E1; primary QA-A23, QA-A39, QA-F36, QA-F53. Do not collapse those dedicated checks into this row.
3. **Preconditions:** The production instance as it sits. Quality shall not obtain or invent an empty first boot. There is no operator wipe. Empty first-boot observation is out of scope and is not a go-live requirement.
4. **Steps:**
   1. Trace CR-USER-1 onto QA-A23: no first-run wizard on the current instance; `enabled` independent of `blocked`.
   2. Trace CR-USER-1 onto QA-A39: Restart the app is present; no wipe control; no return-to-empty-first-boot control; Restart the app is not a wipe. Typed DELETE is not a fail of A39.
   3. Trace CR-USER-1 onto QA-F36: Fate’s disable/enable persists across Restart the app; factory is not reapplied on restart of a non-empty instance.
   4. Trace CR-USER-1 onto QA-F53: operator wipe or return-to-empty-first-boot control absent; Restart the app is not a wipe; typed DELETE is not a go-live factory-empty path.
   5. Confirm Quality did not obtain or invent an empty first boot. Confirm empty first-boot observation is not required to pass this Spec.
5. **Expected observable:** No wizard. No wipe. No empty-first-boot requirement. Persistence is F36. Remaining CR-E1 holds on the current instance.
6. **Pass / fail:** Pass if those hold. Fail if a wipe exists or a wizard is required. Do not fail because empty first-boot was not observed. Do not collapse QA-A23, QA-A39, QA-F36, or QA-F53 into this check.
7. **On fail:** Defect (Engineer) if a wipe exists or a wizard is required. Do not raise a Change Request to invent a wipe or to obtain empty first boot. Dedicated A/F checks still run.

---

### 4.4 Named-hole dedicated checks (S10, S11, S12)

Do not treat S10–S12 as comments only. Primary A/F checks still exist and are not collapsed into these.

#### QA-S10

1. **ID:** QA-S10
2. **Spec trace:** S10 Targeted Query vs Operator item; primary QA-A4, QA-A36, QA-A37, QA-F2, QA-F49; also F50
3. **Preconditions:** Control Run, type `targeted`. Modes Query and Operator item.
4. **Steps:**
   1. Mode Query, topic/query/occasion all empty: copy `Targeted needs a topic, query, or occasion.` No job. This is A4/F2.
   2. Mode Operator item, five required filled, topic/query/occasion empty: job is created. Query copy is not shown. This is A36.
   3. Mode Operator item missing locator (or any of source, locator, text, kind, channel): copy `Operator item needs source, locator, text, kind, and channel.` No job. Not F2. This is A37/F49.
   4. Mode Operator item `written_social` or source `truth_social` / `x_personal` with no pin: copy `A written_social Operator item is refused if no pin is set.` Not F2. This is F50.
5. **Expected observable:** Query-only targeted require. Operator item required fields source, locator, text, kind, channel. Those refuses are not F2. F2 and A4 remain Query.
6. **Pass / fail:** Pass if Query empty still F2/A4, Operator item empty-three still creates a job, and Operator item missing-required uses Operator item copy not F2. Fail if the two modes share one require copy.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-S11

1. **ID:** QA-S11
2. **Spec trace:** S11 Probe-clock 09:00 tick; primary QA-A34, QA-F51, QA-F47. QA-A24 is next-run display after 09:00 and is not this tick.
3. **Preconditions:** Probe clock. Enabled non-exempt sources. Worker available enough to observe enqueue.
4. **Steps:**
   1. Set weekday 09:00 ET: enqueue `incremental` once for each enabled non-exempt source due that day, then advance next-run.
   2. Remain frozen: does not enqueue again.
   3. Weekday before 09:00: does not enqueue.
   4. Weekday after 09:00 (not at 09:00): does not enqueue. Next-run display for that instant is QA-A24, not this tick.
   5. Saturday/Sunday: never enqueue (F47). Next-run Monday 09:00 ET.
   6. Display of next-run is not that tick.
5. **Expected observable:** Probe-clock weekday 09:00 tick as specified. Remaining frozen does not enqueue again. Weekend never enqueues.
6. **Pass / fail:** Pass if tick, freeze, before-09:00, weekday after 09:00 no enqueue, and weekend hold. Fail if weekday 09:00 does not enqueue sources due that day, if remaining frozen enqueues again, or if weekend enqueues. Display of next-run is not that tick. QA-A24 does not own this tick.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

#### QA-S12

1. **ID:** QA-S12
2. **Spec trace:** S12 named_party operator surface; primary QA-A9, QA-A10, QA-A38, QA-F52
3. **Preconditions:** A clean legal record if asserting the read surfaces. Operator item for absence (F52) and for minting a clean legal with `named_party` `Donald Trump` if none exists.
4. **Steps:**
   1. `ov-record` shows `named_party` when kind is `legal` (read-only). Hidden otherwise.
   2. GetRecord includes `named_party`.
   3. Export retrieval set includes `named_party` (`Donald Trump` on legal; empty on other kinds; field not omitted).
   4. Absence of `named_party` on a would-be `legal` item is field-fail, not a silent drop.
   5. Leftover section 6 list without `named_party` is struck. S12 wins.
5. **Expected observable:** named_party on ov-record when kind legal (read-only), GetRecord, Export (empty on non-legal). Absence is field-fail F52. Not a silent drop.
6. **Pass / fail:** Pass if the three surfaces and the absence field-fail hold. Fail if the field is omitted from Export, missing on legal ov-record, or absence is a silent drop.
7. **On fail:** Defect (Engineer). Dedicated A/F checks still run.

---

## 5. Shared setup notes

Overlaps may share setup; each Spec ID still has its own check id.

**Four screens.** Dashboard, Control, Records, Quarantine. Control inner tabs: Run job, Jobs, Sources, Vocabularies, Operator. Operator is not a fifth chrome screen.

**Worker.** Stop worker while available; Start worker while not available. Use these controls whenever a check needs worker-down or worker-up. Do not paint-only.

**Restart.** Restart the app from Control Sources danger. Typed DELETE is not restart, is not first-boot, is not a wipe, and is not a fail of QA-A39 / QA-F53.

**Section 6 down.** Records reads on Control Operator tab.

**Load error.** Fail next load on Control Operator tab.

**Connector.** Per source row on Control Sources. Default `ok`.

**Operator item.** Targeted mode Operator item. Required: source, locator, text, kind, channel. Optional: named_party, outlet. Pin match when source is truth_social or x_personal. This is the Spec path for off-S7, lookalike, administration named_party, missing named_party, and off-list outlet. Do not wait for a public item Fate cannot mint.

**Pins.** Vocabularies text plus Save. Empty Save is F31.

**Allowlist.** Vocabularies text plus Add; Remove per row.

**Probe clock.** Control Operator tab. Empty = wall clock ET. Set datetime ET. Clear returns to wall clock. Display of next-run is not a tick.

**Topics.** Add creates Dashboard rows immediately. Empty copy only when the topic list is empty.

**Shared producers (do not collapse IDs).**

| Setup | Checks that may share it |
| --- | --- |
| Stop worker during a running fetch with stayed clean | QA-A12, QA-A25, QA-F1, QA-F5, QA-F32, QA-F35, QA-F38, QA-F39, QA-CR-QA-1 |
| Restart the app after a known record_id | QA-A16, QA-A26, QA-A33, QA-F36, QA-F40, QA-CR-QA-2, QA-CR-QA-9 |
| Walk screens for no wizard / no wipe | QA-A23, QA-A39, QA-F53, QA-CR-USER-1 |
| Records reads down | QA-A17, QA-A27, QA-F28, QA-F41, QA-CR-QA-3 |
| Fail next load | QA-A28, QA-F29, QA-F42, QA-CR-QA-4 |
| Connector not ok then fetch | QA-A29, QA-F25, QA-F43, QA-CR-QA-5 |
| Operator item whitehouse_remarks social written_social | QA-A19, QA-A30, QA-F33, QA-F44, QA-CR-QA-6 |
| Pin Save / Empty Save / lookalike Operator item | QA-A18, QA-A31, QA-F11, QA-F31, QA-F45, QA-F50, QA-CR-QA-7 |
| Operator item legal named_party / missing named_party / outlet | QA-A32, QA-A38, QA-F12, QA-F27, QA-F46, QA-F52, QA-CR-QA-8, QA-S12 |
| Probe clock named instants | QA-A24, QA-A34, QA-F37, QA-F47, QA-F51, QA-CR-QA-10, QA-S11 |
| Add topic with no ingest | QA-A14, QA-A35, QA-F16, QA-F48, QA-CR-QA-11 |
| Targeted Query empty vs Operator item empty-three vs missing required | QA-A4, QA-A36, QA-A37, QA-F2, QA-F49, QA-S10 |

**Do not use.** Language, framework, host, vendor, live instance addresses, pytest, or product code. Execution is illegal until this plan is Approved.

---

## 6. Ship-gate subset

Spec stranger done-when: **A1, A2, A3, A9, A11, A15, A16**. Mapped as QA-A1, QA-A2, QA-A3, QA-A9, QA-A11, QA-A15, QA-A16.

Passing the ship-gate subset in an Approved execution does not ship. QA does not ship. G11 still requires User confirm + no open blockers.

A9 now includes `named_party` when kind is `legal` (S12). A16 is induced by Restart the app (CR-QA-2), not by typed DELETE.

The rest of A1–A39 including A5b, F1–F53, CR-QA-1 through CR-QA-11, CR-USER-1, and S10–S12 remain required for this Spec to be complete and are still executed when this plan is Approved. Total dedicated checks = 108.

---

## 7. Open holes

Spec v8 closed the old CR-QA-1 through CR-QA-11 induction holes by naming operator controls: Stop worker / Start worker, Restart the app, Records reads, Fail next load, Connector, Operator item, pin Save, allowlist Add/Remove, Probe clock, Add topic rows before ingest. S10, S11, and S12 are named. CR-USER-1 put empty first-boot observation out of scope. Operator item is the Spec path for a public item Fate cannot mint. Do not leave that as an open hole. Do not drop IDs. Missing branch is not a pass.

Remaining holes only where Spec v8 still does not specify how to induce a state. Do not invent. Do not leave a would-be CR to invent a wipe.

The v4 hole that empty first-boot cannot be observed is removed. Spec v8 put that observation out of scope. QA-A23 is executable on the current instance. QA-F36 is executable via Restart the app. QA-A39 and QA-F53 are absence checks. Typed DELETE is still F21 (confirm required; Cancel leaves the base) and is not first-boot and is not a fail of A39/F53.

No unspecified induction remainder remains. No open hole that blocks this Draft.

No other CR-QA-1 through CR-QA-11 induction remainder is left as a hole. Worker-down is Stop worker. Restart is Restart the app. Section 6 down is Records reads. Load error is Fail next load. Network/auth/parse is Connector. Off-S7, lookalike, named_party, off-list outlet are Operator item. Clock branches are Probe clock. Topic rows before ingest are Add topic. Stored UTC on a screen is forbidden; QA-A33 / QA-CR-QA-9 judge ET instants and the absence of a UTC column.

Packet leftover “Global jobs are not this mutex” remains struck. Leftover section 6 list without `named_party` is struck; S12 wins. Spec v8 Advisory A1 and Advisory A2 stay as Spec advisories, not Plan blockers.

No A/F ID, CR-QA ID, CR-USER-1 ID, or S10–S12 ID was dropped.

---

## 8. Submit-for-review statement

This Draft (QA Plan Draft v5) is submitted to Adversarial Reviewer. Source is Approved Spec v8, file `/workspace/ptrp-spec-approved-v8.md` (also `/workspace/ptrp-spec-draft.md`). Frozen Plan v4 at `/workspace/ptrp-qa-plan-approved-v4.md` is bound to Spec v7 and is not this Draft.

Execution is illegal until this plan is Approved. Draft execution is illegal. Do not run these checks. Do not implement product code. Do not hit the live instance. This is not a ship. QA does not ship.

---

*End QA Plan Draft v5. Total dedicated checks = 108. Q1 stays closed. Q2 stays closed: QA-A24 Sets a weekday after 09:00 ET, not at 09:00, and does not treat S11 enqueue as an A24 fail. The tick stays on QA-A34, QA-F51, and QA-S11. Plan v4 Advisory A1 (next-run mapping) stays. Spec v8 Advisory A1 and Advisory A2 stay as Spec advisories, not Plan blockers. Empty first-boot observation is out of scope (CR-USER-1). Do not invent a wipe. Source: Approved Spec v8. Execution illegal until Approved.*
