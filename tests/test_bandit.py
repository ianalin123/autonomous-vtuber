import pytest
from core.bandit import ThompsonBandit, Action


def test_bandit_initializes_with_actions():
    actions = [Action.TALK, Action.REACT, Action.GAME, Action.QA]
    bandit = ThompsonBandit(actions=actions)
    assert len(bandit._arms) == 4


def test_bandit_select_returns_valid_action():
    actions = [Action.TALK, Action.REACT, Action.GAME, Action.QA]
    bandit = ThompsonBandit(actions=actions)
    selected = bandit.select()
    assert selected in actions


def test_bandit_update_increases_successes():
    bandit = ThompsonBandit(actions=[Action.TALK])
    bandit.update(Action.TALK, reward=1.0)
    assert bandit._arms[Action.TALK]["alpha"] > 1


def test_bandit_update_increases_failures_on_zero_reward():
    bandit = ThompsonBandit(actions=[Action.TALK])
    bandit.update(Action.TALK, reward=0.0)
    assert bandit._arms[Action.TALK]["beta"] > 1


def test_bandit_exploit_selects_best_arm():
    bandit = ThompsonBandit(actions=[Action.TALK, Action.REACT])
    for _ in range(20):
        bandit.update(Action.TALK, reward=1.0)
    for _ in range(20):
        bandit.update(Action.REACT, reward=0.0)
    selections = [bandit.exploit() for _ in range(10)]
    assert selections.count(Action.TALK) >= 8
