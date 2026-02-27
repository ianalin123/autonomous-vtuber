import pytest
from agents.analytics import MetricsCollector, compute_engagement_score


def test_engagement_score_zero_when_no_activity():
    score = compute_engagement_score(chat_velocity=0, viewer_retention=0, donation_rate=0)
    assert score == 0.0


def test_engagement_score_increases_with_chat():
    low = compute_engagement_score(chat_velocity=5, viewer_retention=0.5, donation_rate=0)
    high = compute_engagement_score(chat_velocity=50, viewer_retention=0.5, donation_rate=0)
    assert high > low


def test_metrics_collector_initial_state():
    collector = MetricsCollector()
    assert collector.viewer_count == 0
    assert collector.chat_velocity == 0.0
    assert collector.donations_per_hour == 0.0


def test_metrics_collector_record_message_increases_count():
    collector = MetricsCollector()
    collector.record_chat_message()
    collector.record_chat_message()
    assert collector._message_count == 2


def test_metrics_collector_record_donation():
    collector = MetricsCollector()
    collector.record_donation(10.0)
    assert collector._donation_total == 10.0
