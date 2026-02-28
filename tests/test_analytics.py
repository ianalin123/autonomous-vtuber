import pytest
from agents.analytics import MetricsCollector, AnalyticsAgent, compute_engagement_score, create_app
from core.event_bus import EventBus
from core.interfaces import Event, EventType


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


@pytest.mark.asyncio
async def test_analytics_agent_subscribes_to_events():
    bus = EventBus()
    agent = AnalyticsAgent(bus)
    assert EventType.CHAT_MESSAGE in bus._subscribers
    assert EventType.DONATION in bus._subscribers
    assert EventType.SUBSCRIPTION in bus._subscribers
    assert EventType.VIEWER_COUNT in bus._subscribers
    assert EventType.STREAM_STATE in bus._subscribers


@pytest.mark.asyncio
async def test_analytics_agent_chat_updates_collector():
    bus = EventBus()
    collector = MetricsCollector()
    agent = AnalyticsAgent(bus, collector)
    await bus.publish(Event(
        type=EventType.CHAT_MESSAGE,
        payload={"username": "test", "text": "hello"},
    ))
    assert collector._message_count == 1
    assert collector.chat_velocity > 0


@pytest.mark.asyncio
async def test_analytics_agent_donation_updates_collector():
    bus = EventBus()
    collector = MetricsCollector()
    agent = AnalyticsAgent(bus, collector)
    await bus.publish(Event(
        type=EventType.DONATION,
        payload={"username": "donor", "amount": 25.0},
    ))
    assert collector._donation_total == 25.0


@pytest.mark.asyncio
async def test_analytics_agent_viewer_count_updates():
    bus = EventBus()
    collector = MetricsCollector()
    agent = AnalyticsAgent(bus, collector)
    await bus.publish(Event(
        type=EventType.VIEWER_COUNT,
        payload={"count": 150},
    ))
    assert collector.viewer_count == 150


@pytest.mark.asyncio
async def test_analytics_agent_stream_state_tracks_activity():
    bus = EventBus()
    agent = AnalyticsAgent(bus)
    await bus.publish(Event(
        type=EventType.STREAM_STATE,
        payload={"activity": "q_and_a"},
    ))
    assert agent._current_activity == "q_and_a"


@pytest.mark.asyncio
async def test_analytics_agent_subscription_increments_count():
    bus = EventBus()
    agent = AnalyticsAgent(bus)
    await bus.publish(Event(
        type=EventType.SUBSCRIPTION,
        payload={"username": "sub_user", "tier": 1},
    ))
    assert agent._subs_count == 1


def test_analytics_agent_stream_summary_data():
    bus = EventBus()
    collector = MetricsCollector()
    agent = AnalyticsAgent(bus, collector)
    collector.record_chat_message()
    collector.record_chat_message()
    collector.record_donation(10.0)
    data = agent.get_stream_summary_data()
    assert "duration_minutes" in data
    assert data["chat_messages"] == 2
    assert data["total_revenue"] == 10.0


def test_create_app_has_websocket_route():
    app = create_app()
    routes = [r.path for r in app.routes]
    assert "/ws/metrics" in routes
    assert "/api/stream/state" in routes
    assert "/health" in routes
