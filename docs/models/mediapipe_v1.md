# Model card: MediaPipe BlazePose v1

Adapter: `services/cv_worker/pose/mediapipe_adapter.py` (`POSE_ADAPTER=mediapipe`, the default).
Requires the `[cv]` extra; without it the factory returns the fixture adapter.

## Status

- Not validated on football film. No MAE against coach labels exists (`golden_set: pending`).
- Not football-specific. Not a medical device. No paying users until golden-set MAE exists.
- Not exercised in CI: `mediapipe` is not installed there, so every test run uses fixture poses.

## Known failure modes

- **2D only.** Angles are measured in the image plane. Anything off the side-on plane (45° clip, athlete
  turning) distorts shin, lean and foot-plant angles. `shin_angle_at_contact` is only computed from the
  side clip.
- **Scale.** Without field lines or athlete height the pipeline cannot convert pixels to distance;
  distance cues become `uncalibrated` with `value: null`. With height only (`height_prior`), shin angle
  and hip height (WR) / pad level and foot plant (DB) are downgraded to `low_confidence`.
- **Frame rate.** The adapter needs the clip's real fps (`run_pose_assessment(fps=...)`); a wrong fps
  scales every ms cue. Default is 60.
- **Missed detections.** Frames with no detected person are left as zero-confidence keypoints; cues on
  those frames fail the 0.4 joint-confidence gate.
- **Lighting / clothing / occlusion.** Known weak spots for phone pose models (low light, backlight, baggy
  clothing, other players crossing). Not measured here.
- **Left/right assumptions.** Cue formulas use the right ankle/knee as the lead leg. Athletes leading with
  the left leg are not handled.
- Adapter exceptions produce `assessment_status: error`; synthetic poses are never substituted.
