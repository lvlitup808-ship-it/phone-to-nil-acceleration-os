"""Runnable pose / event stub."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FramePose:
    frame: int
    keypoints: dict[str, tuple[float, float, float]]


def quality_gate(width: int, height: int, fps: float, blur: float) -> dict:
    ok = width >= 720 and fps >= 30 and blur < 0.35
    return {"usable": ok, "score": 0.9 if ok else 0.3, "retake": None if ok else "Raise resolution / stabilize"}


def estimate_pose(frames: int = 30) -> list[FramePose]:
    poses = []
    for i in range(frames):
        poses.append(
            FramePose(
                frame=i,
                keypoints={
                    "hip": (0.5, 0.55, 0.9),
                    "knee": (0.52, 0.72, 0.88),
                    "ankle": (0.54, 0.90, 0.86),
                },
            )
        )
    return poses


def detect_events(poses: list[FramePose]) -> dict[str, int]:
    return {"start_motion": 2, "first_step": 6, "foot_strike": 8, "hip_rise": 12}


def run_stub() -> dict:
    gate = quality_gate(1280, 720, 60, 0.1)
    poses = estimate_pose()
    events = detect_events(poses)
    return {"quality": gate, "frames": len(poses), "events": events}


if __name__ == "__main__":
    print(run_stub())
