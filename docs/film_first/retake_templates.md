# Retake Packet

Send automatically when ingest rejects. Each heading is the exact `reasons[]` code returned by
`POST /ingest/check` (`packages/capture/contract.py`, filename check in
`services/cv_worker/ingest/naming.py`). If a code here does not match the validator, the validator wins
and this file is wrong.

## Reason: fps_below_30

The clip was filmed below 30fps. We need 30fps minimum, 60fps preferred.

Fix: Open your camera settings → Video → select 1080p at 60fps. Re-film.

## Reason: duration_not_4_to_12s

The clip was shorter than 4 seconds or longer than 12. The validator accepts 4–12 seconds; aim for
5–10 so the athlete completes 3 steps past the movement.

Fix: Start recording 1 second before the athlete moves, stop 3 steps after.

## Reason: phone_unstable_first_500ms

The phone moved during the first half-second. We need a still frame to calibrate.

Fix: Set the phone down or brace your elbows. Hold still for 1 full second before the athlete moves.

## Reason: missing_side_or_45

Only one angle uploaded. We need both side and 45°.

Fix: Film both. Side first, then move 45° and film again.

## Reason: bad_filename

The file name does not follow `<athlete_id>_<position>_<movement>_<angle>_<date>.mp4`
(for example `ath_0042_WR_release_side_20260925.mp4`).

Fix: Rename and re-upload. No re-film needed.

## Not an ingest reject: no field lines

This is not a `reasons[]` code. Ingest accepts the clip. When no yard lines are detected, calibration
falls back to `height_prior` (or `uncalibrated` if no height is on file), and the assessment reports it
through `calibration_mode` and `cue_status`. With `height_prior`, 2 of 6 cues are downgraded to
`low_confidence` (WR: shin_angle_at_contact, hip_height_at_contact; DB: pad_level_at_break,
foot_plant_angle — `services/cv_worker/confidence.py`).

Fix for next time: reframe so at least one yard line or hash mark is visible behind the athlete.
