# Model card: RTMPose ONNX v1

Adapter: `services/cv_worker/pose/rtmpose_adapter.py`. **Off.** Default `POSE_ADAPTER` is `mediapipe`.

## Status

- Weights are not bundled. `infer()` raises unconditionally, so selecting it yields
  `assessment_status: error` on any real clip.
- Gate to turn it on: Slice 3 gates plus an RTMPose-vs-MediaPipe comparison on the golden set
  (`docs/film_first/schedule.md`, week 3). Neither exists.
- No accuracy numbers exist for this adapter.

## Known failure modes

Same 2D, scale, frame-rate and lead-leg limits as MediaPipe (`docs/models/mediapipe_v1.md`). Same
uncalibrated rules: no calibration, no number.
