import pytest
from agents.donation_goals import DonationGoalTracker, Goal


def test_goal_initializes_at_zero():
    tracker = DonationGoalTracker()
    tracker.set_goal(Goal(target=100.0, description="hit $100 and I'll do a karaoke"))
    assert tracker.current_total == 0.0
    assert tracker.progress_pct == 0.0


def test_record_donation_updates_total():
    tracker = DonationGoalTracker()
    tracker.set_goal(Goal(target=50.0, description="karaoke at $50"))
    tracker.record_donation(25.0)
    assert tracker.current_total == 25.0


def test_progress_pct_correct():
    tracker = DonationGoalTracker()
    tracker.set_goal(Goal(target=100.0, description="test"))
    tracker.record_donation(40.0)
    assert tracker.progress_pct == 40.0


def test_milestone_triggers_at_50_pct():
    tracker = DonationGoalTracker()
    tracker.set_goal(Goal(target=100.0, description="test"))
    milestones = []
    tracker.on_milestone = lambda pct, msg: milestones.append(pct)
    tracker.record_donation(50.0)
    assert 50 in milestones


def test_goal_complete_triggers_callback():
    tracker = DonationGoalTracker()
    tracker.set_goal(Goal(target=20.0, description="small goal"))
    completed = []
    tracker.on_complete = lambda msg: completed.append(msg)
    tracker.record_donation(25.0)
    assert len(completed) == 1


def test_announce_text_includes_progress():
    tracker = DonationGoalTracker()
    tracker.set_goal(Goal(target=100.0, description="karaoke at $100"))
    tracker.record_donation(30.0)
    text = tracker.announce_text()
    assert "30" in text or "30.00" in text
    assert "100" in text
