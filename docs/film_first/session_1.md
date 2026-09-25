# Verified. Now go shoot Session 1.

D36–D45 is the right scope. No product surface. No Slice 3. The repo is done until film exists. Read this once, then put the laptop away until Session 1 is labeled.

## Before you leave for the field

Print these four. Nothing else.

1. `docs/film_first/capture_guide.md` — one per filmer
2. `docs/legal/consent_form_minor.md` — one per under-18 athlete
3. `docs/film_first/labeling_protocol.md` — one for the coach
4. A blank assignments sheet — `docs/film_first/assignments_sheet.md` — fill athlete IDs on site

Checklist for the bag: two phones (backup), a tripod or a wall to brace against, painters tape for athlete ID labels, a printed yard-line reference in case the field is unmarked.

## Session 1 field rules

One filmer per athlete. Do not have one person filming six athletes at once. They will rush. One athlete, two angles, done, next.

Side angle first, always. Then 45°. If you only get one clean angle per athlete, side is the one that gives you shin angle and hip height. Protect it.

Hold still for one full second before "go." Count it out loud if you have to. That frame is the calibration anchor. No anchor, no shin angle.

Three steps past the movement. Do not cut the clip at the movement. The event detector needs the deceleration to find the break.

One retake max per athlete per angle. If the first take fails, one more. If that fails, move to the next athlete and come back. Athletes get tired and mechanics degrade by take three.

Log the take in the intake form before moving on. Athlete ID, position, movement, which angle passed, which needs retake. Do not "remember it later."

## Session 1 night — 90-minute review

Do this the same day. Not tomorrow.

1. Ingest every clip. Run `/ingest/check` on all. Log rejects with reason.
2. Open `pose_debug.mp4` on the first clean WR clip. Watch it yourself, twice. Does the skeleton track the athlete through the burst? Any joint flipping or lag?
3. Open `calibration_debug.png` on the same clip. Is field_line mode hitting? Or did it fall to height_prior? If the field had visible lines and it still fell back, calibration detection has a bug. Fix before Session 2.
4. Check event markers. Do motion_start, first_step, release line up with what you see on the timeline? Off by more than 3 frames → event detector issue.
5. Sanity-check the 6 WR cues. shin_angle_at_contact between 30 and 50 is plausible. hip_height_at_contact between 0.75 and 0.95 is plausible. Anything outside those ranges on a clean clip means the feature formula is wrong, not the model.
6. Log it all in `docs/validation/session_1_report.md`. What passed, what failed, what needs a fix before Session 2.

## Decision tree after Session 1

- ≥ 4 clean WR clips + ≥ 4 clean DB clips → Proceed to Session 2 as planned. Label Session 1 clips within 48 hours.
- 2–3 clean clips, rest rejected for the same reason → Stop. The capture protocol has a specific bug. Rewrite the capture guide section that matches the rejection reason. Then Session 2.
- 2–3 clean clips, rejections for different reasons → The filmers are the problem, not the protocol. One of them needs to be the only filmer for Session 2.
- 0–1 clean clips → Do not run Session 2. Do not touch code. Go to a marked field with one athlete and one filmer and get one clip that passes. That clip is the whole week.

## What not to do this week

- Do not open Slice 3.
- Do not "improve" the pose pipeline.
- Do not add cues.
- Do not touch the RTMPose flag.
- Do not build the passport.
- Do not draft NIL band copy.
- Do not write a blog post about the architecture.

Every one of those feels productive and delays the only thing that unblocks the project: labeled clips.

## What success looks like Friday

- Session 1 shot
- 6 consent forms signed and scanned
- Clips ingested, at least 4 clean
- 1 clip labeled end-to-end by a real coach in under 4 minutes
- session_1_report.md written with what failed and why

That's it. Not a merged PR. Not a new feature. A field session, a labeled clip, and an honest report.

The repo will wait. The film won't.
