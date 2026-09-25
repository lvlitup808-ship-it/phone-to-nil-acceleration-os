import pytest

from services.cv_worker.events.detector import Event
from services.cv_worker.features.common import angle_from_vertical
from services.cv_worker.features.db_break import extract_db
from services.cv_worker.features.wr_release import extract_wr
from services.cv_worker.pose.fixture_adapter import FixturePoseAdapter
from services.cv_worker.calibration.field_line import Calibration


@pytest.mark.parametrize(
    ("dx", "dy", "expected"),
    [(0, -100, 0.0), (0, 100, 0.0), (100, -100, 45.0), (-100, -100, -45.0), (100, 100, 45.0), (100, 0, 90.0)],
)
def test_angle_from_vertical_is_symmetric_in_image_y(dx, dy, expected):
    assert angle_from_vertical(dx, dy) == pytest.approx(expected, abs=1e-3)


CAL = Calibration(mode="field_line", confidence=0.8, meters_per_pixel=0.01, debug_points=[])


def test_gct_is_not_invented_without_a_second_step():
    seq = FixturePoseAdapter().infer(None)
    events = [Event("motion_start", 400, 0.8, 25), Event("first_step", 580, 0.75, 35), Event("release", 860, 0.65, 52)]
    cue = {c["name"]: c for c in extract_wr(seq, events, CAL, "c", side_clip=True)}["ground_contact_time_first_step"]
    assert cue["value"] is None
    assert cue["cue_status"] == "insufficient_data"


def test_recovery_step_is_not_invented_when_order_is_wrong():
    seq = FixturePoseAdapter().infer(None)
    events = [Event("first_step", 300, 0.75, 18), Event("break", 860, 0.65, 52)]
    cue = {c["name"]: c for c in extract_db(seq, events, CAL, "c")}["recovery_first_step"]
    assert cue["value"] is None
    assert cue["cue_status"] == "insufficient_data"


def test_units_match_what_is_computed():
    seq = FixturePoseAdapter().infer(None)
    events = [Event("first_step", 900, 0.75, 54), Event("peak_velocity", 700, 0.7, 42), Event("break", 860, 0.65, 52)]
    units = {c["name"]: c["unit"] for c in extract_db(seq, events, CAL, "c")}
    assert units["hip_rotation_rate"] == "px/s"
    assert units["eye_discipline_proxy"] == "px^2"


def test_slice1_units():
    from packages.biomech.features import UNITS, extract_cues
    from packages.shared.models import CueId, PositionTemplate

    assert set(UNITS) == set(CueId)
    units = {c.id: c.unit for c in extract_cues(PositionTemplate.wr_release)}
    assert units[CueId.hip_height] == "ratio"
    assert units[CueId.first_step_separation] == "yd"
