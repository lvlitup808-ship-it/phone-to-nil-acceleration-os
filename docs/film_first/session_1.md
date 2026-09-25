# Verified. Now go shoot Session 1.

D36–D45 is the right scope. No product surface. No Slice 3. The repo is done until film exists. Read this once, then put the laptop away until Session 1 is labeled.

## Before you leave for the field

Print these four. Nothing else.

1. `docs/film_first/capture_guide.md` — one per filmer
2. `docs/legal/consent_form_minor.md` — one per under-18 athlete
3. `docs/film_first/labeling_protocol.md` — one for the coach
4. A blank assignments sheet — fill athlete IDs on site (`data/golden_set/assignments.json`)

Bag: two phones (backup), a tripod or a wall to brace against, painters tape for athlete ID labels, a printed yard-line reference if the field is unmarked.

## Session 1 field rules

- One filmer per athlete. Do not have one person filming six athletes at once.
- Side angle first, always. Then 45°. If you only get one clean angle, protect side.
- Hold still for one full second before "go." Count it out loud. That frame is the calibration anchor.
- Three steps past the movement. Do not cut the clip at the movement.
- One retake max per athlete per angle. If that fails, move on and come back.
- Log the take in the intake form before moving on. Do not remember it later.

## Session 1 night — 90-minute review (same day)

1. Ingest every clip. Run `/ingest/check` on all. Log rejects with reason.
2. Open `pose_debug.mp4` on the first clean WR clip. Twice. Does the skeleton track through the burst?
3. Open `calibration_debug` on the same clip. field_line or height_prior? Visible lines + fallback = bug. Fix before Session 2.
4. Event markers vs timeline. Off by more than 3 frames → event detector issue.
5. Sanity-check 6 WR cues. shin_angle_at_contact 30–50 plausible. hip_height_at_contact 0.75–0.95 plausible. Outside that on a clean clip = formula, not model.
6. Write `docs/validation/session_1_report.md`.

## Decision tree after Session 1

- ≥ 4 clean WR + ≥ 4 clean DB → Session 2 as planned. Label Session 1 within 48 hours.
- 2–3 clean, same reject reason → Stop. Rewrite that capture-guide section. Then Session 2.
- 2–3 clean, mixed reject reasons → Filmers, not protocol. One filmer for Session 2.
- 0–1 clean → Do not run Session 2. Do not touch code. One athlete, one filmer, one passing clip. That clip is the week.

## What not to do this week

Do not open Slice 3. Do not improve the pose pipeline. Do not add cues. Do not touch the RTMPose flag. Do not build the passport. Do not draft NIL band copy. Do not write a blog post about the architecture.

## What success looks like Friday

- Session 1 shot
- 6 consent forms signed and scanned
- Clips ingested, at least 4 clean
- 1 clip labeled end-to-end by a real coach in under 4 minutes
- `session_1_report.md` written with what failed and why

Not a merged PR. Not a new feature. A field session, a labeled clip, and an honest report.

The repo will wait. The film won't.
