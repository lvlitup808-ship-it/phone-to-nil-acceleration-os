# Session 1 report

Date:
Field:
Filmers:
Athletes present:

## Ingest

Clips filmed:
Clips accepted:
Clips rejected:

| filename | fps | duration | angles | reason |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## First clean WR clip

clip_id:
pose_debug.json / pose_confidence_heatmap.npy — joints confident through burst? Y/N
joint flip or lag? Y/N notes:
calibration_debug — mode: field_line / height_prior / uncalibrated
field had visible lines? Y/N
fallback unexpected? Y/N

## Events (frames off vs what you see)

motion_start:
first_step:
release or break:

Off by more than 3 frames? Y/N

## WR cue sanity (what you see vs what the pipeline says)

No reference bands are given here: the earlier 30–50° and 0.75–0.95 bands had no source and are marked
`unverified` (see `docs/audit/open_questions.md`). Record the value and whether it matches what you see.

shin_angle_at_contact (deg from vertical): value ____ matches film? Y/N
hip_height_at_contact (ankle→hip / ankle→nose): value ____ matches film? Y/N
clearly wrong on a clean clip → feature formula first, then the model.

## Decision

- [ ] ≥4 WR + ≥4 DB clean → Session 2 + label in 48h
- [ ] 2–3 clean, same reject reason → rewrite capture guide, then Session 2
- [ ] 2–3 clean, mixed rejects → one filmer only next session
- [ ] 0–1 clean → no Session 2, no code, one athlete / one filmer / one passing clip

## What failed and why

## Fix before Session 2 (if any)

Do not start Slice 3 from this report.
