"""Honesty: the Expo capture stub must not promise an NIL band.

The golden-set gate is closed and band numerics are null. The mobile
subtitle used to read "Phone start → cues → NIL band", which reads as
a valuation the app does not compute. This pin fails if that promise
returns, or if the stub prints a dollar amount.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "mobile" / "App.tsx"


def test_mobile_stub_does_not_promise_an_nil_band() -> None:
    text = APP.read_text()
    subtitle = next(
        (line for line in text.splitlines() if "styles.sub" in line and "Text" in line),
        "",
    )
    assert subtitle, "expected a subtitle Text node"
    lowered = subtitle.lower()
    assert "cues → nil band" not in lowered
    assert "cues -> nil band" not in lowered
    assert "blocked" in lowered or "null" in lowered
    assert "$" not in subtitle
    assert "p50" not in lowered
    assert "mae" not in lowered
