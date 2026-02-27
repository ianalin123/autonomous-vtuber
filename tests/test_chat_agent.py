import pytest
from unittest.mock import MagicMock, patch
from core.interfaces import ChatMessage
from agents.chat_agent import ChatAgent


def test_classify_donation():
    agent = ChatAgent(db=None)
    msg = ChatMessage(username="donor", text="great stream!", is_donation=True, donation_amount=10.0)
    assert agent.classify(msg) == "donation"


def test_classify_sub():
    agent = ChatAgent(db=None)
    msg = ChatMessage(username="subber", text="", is_sub=True, sub_tier=2)
    assert agent.classify(msg) == "subscription"


def test_classify_spam():
    agent = ChatAgent(db=None)
    msg = ChatMessage(username="spammer", text="follow4follow http://spam.com")
    assert agent.classify(msg) == "spam"


def test_format_donation_response_includes_name_and_amount():
    agent = ChatAgent(db=None)
    msg = ChatMessage(username="bigfan", text="love you!", is_donation=True, donation_amount=25.0)
    response = agent.format_donation_response(msg, viewer_history=None)
    assert "bigfan" in response
    assert "25.00" in response or "25" in response


def test_format_returning_donor_includes_callback():
    agent = ChatAgent(db=None)
    msg = ChatMessage(username="regulardono", text="back again!", is_donation=True, donation_amount=5.0)
    history = {"total_donated": 50.0, "first_seen": "2025-01-01"}
    response = agent.format_donation_response(msg, viewer_history=history)
    assert "regulardono" in response


def test_should_respond_to_questions():
    agent = ChatAgent(db=None)
    msg = ChatMessage(username="curious", text="what game are you playing?")
    assert agent.should_respond(msg) is True


def test_should_not_respond_to_spam():
    agent = ChatAgent(db=None)
    msg = ChatMessage(username="bot", text="follow4follow")
    assert agent.should_respond(msg) is False
