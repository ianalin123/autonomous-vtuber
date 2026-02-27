import pytest
from agents.subscriber_tracker import SubscriberTracker


def test_add_subscriber():
    tracker = SubscriberTracker(db=None)
    tracker.add("viewer1", tier=1)
    assert "viewer1" in tracker._subs


def test_renew_subscriber_increments_months():
    tracker = SubscriberTracker(db=None)
    tracker.add("viewer1", tier=1)
    tracker.renew("viewer1")
    assert tracker._subs["viewer1"]["months"] == 2


def test_churn_removes_subscriber():
    tracker = SubscriberTracker(db=None)
    tracker.add("viewer1", tier=1)
    tracker.churn("viewer1")
    assert "viewer1" not in tracker._subs


def test_is_subscriber_returns_true():
    tracker = SubscriberTracker(db=None)
    tracker.add("viewer1", tier=2)
    assert tracker.is_subscriber("viewer1") is True


def test_is_subscriber_returns_false_for_unknown():
    tracker = SubscriberTracker(db=None)
    assert tracker.is_subscriber("nobody") is False


def test_sub_count_accurate():
    tracker = SubscriberTracker(db=None)
    tracker.add("a", tier=1)
    tracker.add("b", tier=2)
    tracker.add("c", tier=3)
    assert tracker.sub_count == 3


def test_tenure_response_for_long_subscriber():
    tracker = SubscriberTracker(db=None)
    tracker.add("veteran", tier=1)
    tracker._subs["veteran"]["months"] = 12
    response = tracker.format_sub_appreciation("veteran")
    assert "veteran" in response
    assert "12" in response


def test_tier_breakdown():
    tracker = SubscriberTracker(db=None)
    tracker.add("a", tier=1)
    tracker.add("b", tier=1)
    tracker.add("c", tier=2)
    breakdown = tracker.tier_breakdown()
    assert breakdown[1] == 2
    assert breakdown[2] == 1
