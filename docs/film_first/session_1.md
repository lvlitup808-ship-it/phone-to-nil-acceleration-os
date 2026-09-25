# Verified. Now go shoot Session 1.

D36–D45 is the right scope. No product surface. No Slice 3. The repo is done until film exists. Read this once, then put the laptop away until Session 1 is labeled.

PR #5 is the last commit this week.

## Before you leave for the field

Print these four. Nothing else.

1. `docs/film_first/capture_guide.md` — one per filmer
2. `docs/legal/consent_form_minor.md` — one per under-18 athlete
3. `docs/film_first/labeling_protocol.md` — one for the coach
4. A blank assignments sheet — `docs/film_first/assignments_sheet.md` — fill athlete IDs on site

Checklist for the bag: two phones (backup), a tripod or a wall to brace against, painters tape for athlete ID labels, a printed yard-line reference in case the field is unmarked.

## Five things that will save you on the field

1. Consent before cleats. Signed form in hand before the athlete touches the field. Retrofitting consent is the one thing that kills a clip after you've already shot it.
2. Sun behind you, not behind the athlete. Backlit clips fail pose confidence. If the field only has one orientation, shoot early morning or late afternoon, not noon.
3. Warm up before take one. Cold first take always looks like a bad clip. It isn't. It's a cold athlete. Take zero doesn't count.
4. Backup the same night. Phone + cloud + laptop before you sleep. Phones get lost. Cards corrupt. Six consents are worth more than a night's sleep.
5. Log rejects in the report, not in your head. The pattern across rejects is the protocol fix for Session 2. You won't remember it Thursday.

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
2. Open the pose debug output for the first clean WR clip (`artifacts/<clip_id>/pose_debug.json` and `pose_confidence_heatmap.npy`; a rendered `pose_debug.mp4` does not exist yet — the pipeline only writes it once real frames flow). Check the per-joint confidence through the burst. Any joint flipping or lag?
3. Open `artifacts/<clip_id>/calibration_debug.json` on the same clip (no `.png` is written today). Is field_line mode hitting? Or did it fall to height_prior? If the field had visible lines and it still fell back, calibration detection has a bug. Fix before Session 2.
4. Check event markers. Do motion_start, first_step, release line up with what you see on the timeline? Off by more than 3 frames → event detector issue.
5. Sanity-check the 6 WR cues against what you see on film. The ranges below are **unverified** rough guesses with no source; they are not targets and not validation.
   - shin_angle_at_contact 30–50°: `unverified`. The code measures the tibia's angle from the image vertical; whether 30–50 applies to that convention is a coach call (see `docs/audit/open_questions.md`).
   - hip_height_at_contact 0.75–0.95: `unverified`, and inconsistent with the formula. The code computes (ankle→hip) / (ankle→nose); a standing adult sits near 0.5. Do not flag a clip on this band.
   A clearly wrong number on a clean clip still points at the feature formula before the model.
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

Friday metric, one line: wr_labeled + db_labeled. Not PRs, not CI, not features.

That's it. Not a merged PR. Not a new feature. A field session, a labeled clip, and an honest report.

The repo will wait. The film won't.
