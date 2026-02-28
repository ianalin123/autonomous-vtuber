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


def test_bandit_save_and_load(tmp_path):
    path = str(tmp_path / "bandit.json")
    bandit = ThompsonBandit(actions=list(Action))
    for _ in range(10):
        bandit.update(Action.QA, reward=1.0)
    bandit.save(path)

    loaded = ThompsonBandit.load(path)
    assert loaded._arms[Action.QA]["alpha"] == bandit._arms[Action.QA]["alpha"]
    assert loaded._arms[Action.QA]["beta"] == bandit._arms[Action.QA]["beta"]


def test_bandit_load_or_create_missing_file(tmp_path):
    path = str(tmp_path / "missing.json")
    bandit = ThompsonBandit.load_or_create(path)
    assert len(bandit._arms) == len(Action)
    for arm in bandit._arms.values():
        assert arm["alpha"] == 1.0
        assert arm["beta"] == 1.0
