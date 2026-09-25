from __future__ import annotations

import os

from services.cv_worker.pose.fixture_adapter import FixturePoseAdapter
from services.cv_worker.pose.mediapipe_adapter import MediaPipePoseAdapter
from services.cv_worker.pose.rtmpose_adapter import RTMPosePoseAdapter


def get_adapter():
    name = os.getenv("POSE_ADAPTER", "mediapipe").lower()
    if name == "rtmpose":
        return RTMPosePoseAdapter()
    if name == "fixture":
        return FixturePoseAdapter()
    try:
        import mediapipe  # noqa: F401

        return MediaPipePoseAdapter()
    except Exception:
        return FixturePoseAdapter()
