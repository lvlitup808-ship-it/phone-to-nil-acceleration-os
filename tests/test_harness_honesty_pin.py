"""Honesty pin: golden-set harness never claims athlete validation or MAE.

While golden_set is pending and no real film is on disk, the harness runs in
fixture mode. Its report must keep the honesty line and must not invent an
accuracy number.
"""

from services.golden_set.harness import HONESTY_LINE, build_report


def test_harness_report_includes_honesty_line():
    text = build_report()
    assert HONESTY_LINE in text
    assert "Do not treat this as athlete validation" in text


def test_harness_report_declares_fixture_mode_when_no_real_film():
    text = build_report()
    assert "real_mp4_present: false" in text
    assert "fixture (synthetic poses, not athlete film)" in text
    assert "No athlete-film MAE is published" in text


def test_harness_report_never_claims_mae_number():
    text = build_report().lower()
    # Fail if a numeric MAE claim appears (e.g. "MAE 12.3" or "mae=0.4")
    import re

    assert not re.search(r"\bmae\s*[:=]?\s*\d", text), text
    assert "accuracy" not in text or "no accuracy" in text or "unmeasured" in text
