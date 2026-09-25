from __future__ import annotations

import os

import numpy as np

from services.cv_worker.pose.base import POSE_MODEL_VERSION_RTMPOSE, PoseSequence


class RTMPosePoseAdapter:
    model_id = "rtmpose_onnx"
    model_version = POSE_MODEL_VERSION_RTMPOSE

    def infer(self, frames: list[np.ndarray]) -> PoseSequence:
        if os.getenv("POSE_ADAPTER", "mediapipe") != "rtmpose":
            raise RuntimeError("RTMPose is gated. Set POSE_ADAPTER=rtmpose only after Slice 3 gates.")
        raise RuntimeError("RTMPose ONNX weights are not bundled in Slice 2")
