# Analytics WebSocket + Self-Improvement Loop Implementation Plan

> **For Claude:** Use `@skills/collaboration/executing-plans/SKILL.md` to implement this plan task-by-task.

**Goal:** Wire the analytics dashboard to live data via WebSocket, and close the self-improvement loop so the orchestrator uses real metrics + Thompson Sampling bandit.

**Architecture:** Add WebSocket broadcasting to the analytics FastAPI server, subscribe it to the event bus, make the orchestrator query real stream state and use bandit recommendations, persist bandit state across restarts, and trigger post-stream retrospectives.

**Tech Stack:** Python 3.12, FastAPI (WebSocket), asyncio, Thompson Sampling, httpx

---

## Task 1: Analytics WebSocket + Event Bus Wiring

**Files:**
- Modify: `agents/analytics.py` (full rewrite)
- Test: `tests/test_analytics.py`

### What it does

The analytics module currently has REST endpoints but:
- No WebSocket `/ws/metrics` endpoint (dashboard expects this)
- No event bus subscriptions (MetricsCollector never receives data)
- No broadcasting to connected clients

### Implementation

Rewrite `agents/analytics.py` to:

1. Add `AnalyticsAgent` class that:
   - Takes an `EventBus` and subscribes to `CHAT_MESSAGE`, `DONATION`, `SUBSCRIPTION`, `VIEWER_COUNT`
   - Updates `MetricsCollector` on each event
   - Tracks `_stream_start`, `_current_activity`, `_subs_count`, `_is_live`
   - Manages a set of connected WebSocket clients

2. Add WebSocket endpoint `GET /ws/metrics`:
   - Accept connection, add to client set
   - On disconnect, remove from set
   - Send initial snapshot on connect

3. Add periodic broadcaster (every 2s):
   - Broadcast `stream_state` with `{isLive, viewerCount, uptime, currentActivity, chatVelocity, engagementScore}`
   - Broadcast `metrics_update` with `{revenueToday, subsCount, bitsToday, donationsPerHour}`

4. On donation event, broadcast:
   - `donation` with `{id, username, amount, message, timestamp, type}`
   - `revenue_point` with `{timestamp, amount, cumulative}`

### Message formats (must match dashboard stores)

```python
# stream_state
{"type": "stream_state", "data": {
    "isLive": True, "viewerCount": 42, "uptime": "1:23:45",
    "currentActivity": "talk", "chatVelocity": 12.5, "engagementScore": 65.3
}}

# metrics_update
{"type": "metrics_update", "data": {
    "revenueToday": 150.0, "subsCount": 12, "bitsToday": 0, "donationsPerHour": 25.0
}}

# revenue_point
{"type": "revenue_point", "data": {
    "timestamp": "2026-02-27T10:30:00Z", "amount": 10.0, "cumulative": 150.0
}}

# donation
{"type": "donation", "data": {
    "id": "d_abc123", "username": "viewer1", "amount": 10.0,
    "message": "", "timestamp": "2026-02-27T10:30:00Z", "type": "donation"
}}
```

---

## Task 2: Orchestrator Real State + Bandit Integration

**Files:**
- Modify: `agents/orchestrator.py`
- Test: `tests/test_orchestrator.py`

### What it does

The orchestrator currently:
- Hardcodes context as `"idle. Chat is quiet"` (line 73)
- Never reads real stream metrics
- Never uses the bandit

### Implementation

1. Add `MetricsCollector` and `ThompsonBandit` params to `OrchestratorAgent.__init__`
2. In `run_loop`, build context from real metrics:
   ```
   "Stream state: 42 viewers, chat velocity 12.5 msg/min, engagement 65.3/100,
    revenue $25/hr. Bandit suggests: q_and_a. Current activity: talk."
   ```
3. Use `bandit.select()` to include a suggested action in the context
4. After Claude responds with tool calls, record chosen action for bandit tracking
5. Keep backward compat: if no collector/bandit passed, fall back to basic context

---

## Task 3: Bandit State Persistence

**Files:**
- Modify: `core/bandit.py`
- Test: `tests/test_bandit.py`

### What it does

Bandit state is in-memory only — resets every restart.

### Implementation

1. Add `save(path: str)` — write `self.state()` as JSON
2. Add `classmethod load(path: str) -> ThompsonBandit` — read JSON, restore alpha/beta
3. Default path: `data/bandit_state.json`
4. Orchestrator calls `save()` after each `update()`

---

## Task 4: Post-Stream Retrospective Trigger

**Files:**
- Modify: `agents/retrospective.py`
- Modify: `agents/analytics.py` (add `get_stream_summary()` method)

### What it does

Retrospective exists but is never called.

### Implementation

1. Add `get_stream_summary()` to `AnalyticsAgent` — returns data needed for `build_summary()`
2. Add `shutdown()` method to `AnalyticsAgent` that:
   - Calls retrospective `build_summary()` + `update_bandit()` + `format_report()`
   - Saves bandit state
   - Prints report to stdout

---

## Task 5: Main Entrypoint Wiring

**Files:**
- Modify: `twitch_client/main.py`

### What it does

Wire everything together in the main async entrypoint.

### Implementation

1. Create `EventBus`, `PriorityMessageQueue`, `ThompsonBandit`, `MetricsCollector`
2. Create `AnalyticsAgent(bus, collector)` — subscribes to events
3. Create `OrchestratorAgent(collector, bandit)` — uses real state
4. Start all tasks: bot, bridge, analytics broadcaster, orchestrator loop, uvicorn
5. Handle SIGINT/SIGTERM: trigger retrospective + save bandit state
