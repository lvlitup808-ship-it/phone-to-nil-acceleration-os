from __future__ import annotations

import numpy as np

from services.cv_worker.pose.base import (
    POSE_MODEL_VERSION_MEDIAPIPE,
    PoseSequence,
    smooth_sequence,
    timestamps_ms,
)

_MP_TO_COCO = {
    0: 0, 2: 1, 5: 2, 7: 3, 8: 4,
    11: 5, 12: 6, 13: 7, 14: 8, 15: 9, 16: 10,
    23: 11, 24: 12, 25: 13, 26: 14, 27: 15, 28: 16,
}


class MediaPipePoseAdapter:
    model_id = "mediapipe_blazepose"
    model_version = POSE_MODEL_VERSION_MEDIAPIPE

    def infer(self, frames: list[np.ndarray], fps: float = 60.0) -> PoseSequence:
        try:
            import mediapipe as mp
        except Exception as exc:
            raise RuntimeError("mediapipe is not installed") from exc
        if not frames:
            raise ValueError("no frames")
        h, w = frames[0].shape[:2]
        raw = np.zeros((len(frames), 17, 3), dtype=float)
        pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False)
        try:
            for i, frame in enumerate(frames):
                result = pose.process(frame)
                if not result.pose_landmarks:
                    continue
                lms = result.pose_landmarks.landmark
                for mp_i, coco_i in _MP_TO_COCO.items():
                    lm = lms[mp_i]
                    raw[i, coco_i] = (lm.x * w, lm.y * h, lm.visibility)
        finally:
            pose.close()
        return PoseSequence(
            keypoints=smooth_sequence(raw, fps),
            keypoints_raw=raw,
            fps=fps,
            frame_timestamps_ms=timestamps_ms(len(frames), fps),
            model_id=self.model_id,
            model_version=self.model_version,
            width=w,
            height=h,
        )
