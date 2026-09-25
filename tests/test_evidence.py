from packages.evidence.pipeline import EvidencePipeline


def test_evidence_returns_citations():
    pipe = EvidencePipeline()
    out = pipe.run("shin angle wall drill", "shin_angle")
    assert "drills" in out
    assert "citations" in out
    assert isinstance(out["grounded"], bool)
