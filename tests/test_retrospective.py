import pytest
from agents.retrospective import StreamRetrospective, StreamSummary


def test_retrospective_builds_summary():
    retro = StreamRetrospective(db=None, bandit=None)
    summary = retro.build_summary(
        stream_id="stream-001",
        duration_minutes=120,
        peak_viewers=450,
        total_revenue=87.50,
        top_activities=["talk", "react", "q_and_a"],
        chat_messages=3200,
    )
    assert summary.stream_id == "stream-001"
    assert summary.total_revenue == 87.50
    assert summary.revenue_per_hour == pytest.approx(43.75, rel=0.01)


def test_retrospective_generates_recommendations():
    retro = StreamRetrospective(db=None, bandit=None)
    summary = StreamSummary(
        stream_id="s1",
        duration_minutes=60,
        peak_viewers=100,
        total_revenue=5.0,
        revenue_per_hour=5.0,
        top_activities=["idle"],
        chat_messages=50,
        engagement_score=12.0,
    )
    recs = retro.generate_recommendations(summary)
    assert isinstance(recs, list)
    assert len(recs) > 0


def test_low_revenue_triggers_recommendation():
    retro = StreamRetrospective(db=None, bandit=None)
    summary = StreamSummary(
        stream_id="s1",
        duration_minutes=60,
        peak_viewers=200,
        total_revenue=0.0,
        revenue_per_hour=0.0,
        top_activities=["talk"],
        chat_messages=500,
        engagement_score=60.0,
    )
    recs = retro.generate_recommendations(summary)
    assert any("donation" in r.lower() or "goal" in r.lower() for r in recs)


def test_report_text_includes_key_stats():
    retro = StreamRetrospective(db=None, bandit=None)
    summary = StreamSummary(
        stream_id="s1",
        duration_minutes=90,
        peak_viewers=300,
        total_revenue=45.0,
        revenue_per_hour=30.0,
        top_activities=["talk", "game"],
        chat_messages=1200,
        engagement_score=55.0,
    )
    report = retro.format_report(summary)
    assert "45" in report
    assert "300" in report
