# Autonomous VTuber

A fully autonomous AI streamer that runs a Twitch channel without human intervention. It reads chat, decides what to do next, speaks with a Live2D avatar, and — critically — **learns from every stream to optimize its own behavior**.

---

## What makes this different

Most VTuber bots respond to chat. This one *runs the stream*.

There are two AI layers working in parallel:

**The Orchestrator** (Claude Opus) observes stream state every 5 seconds — viewer count, chat velocity, donation rate, current activity — and uses tool-calling to decide what happens next. It can switch the content format, direct a topic, or dispatch a response. It is not reacting. It is directing.

**The Learning Loop** closes after every stream. A `StreamRetrospective` computes what worked (revenue per hour, engagement score, chat velocity by activity), identifies the top-performing segments, and calls `update_bandit()`. This writes reward signals back into a **Thompson Sampling bandit** (`ThompsonBandit` in `core/bandit.py`), which adjusts the probability weights for five content modes:

| Mode | Description |
|------|-------------|
| `talk` | Freeform commentary and reactions |
| `react` | Responding to chat messages directly |
| `game` | In-game focus mode |
| `q_and_a` | Structured Q&A with viewers |
| `idle` | Low-engagement fallback |

The bandit starts with uniform priors. After stream 1, the weights shift toward whatever drove engagement and revenue. After stream 10, it has a real model of what the audience responds to. **The streamer improves without any human tuning.**

---

## Architecture

```
Twitch IRC
    │
    ▼
PriorityMessageQueue          (donations > subs > mods > chat)
    │
    ▼
TwitchBridge  ──────────────► Open-LLM-VTuber  (Live2D avatar + TTS)
                                      ▲
OrchestratorAgent (Claude Opus)       │
    │  tool-use loop every 5s         │
    │  get_stream_state               │
    │  set_activity                   │
    └──► send_chat_response ──────────┘
              │
              ▼
         EventBus
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
ChatAgent  Analytics  Performer
              │
              ▼
         MetricsCollector
              │
              ▼  (post-stream)
       StreamRetrospective
              │
              ▼
       ThompsonBandit.update()   ← self-improvement happens here
```

**Viewer memory** lives in Neo4j. Every donor, subscriber, and regular chatter is a node in the graph. Returning donors get personalized responses based on their history. The graph accumulates across streams — the system remembers your audience.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Avatar + TTS | [Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber) (Live2D, WebSocket, OpenAI TTS) |
| LLM response | GPT-4o via OpenAI |
| Orchestration | Claude Opus 4.6 (tool-use loop) |
| Viewer memory | Neo4j Aura (knowledge graph) |
| Bandit | Thompson Sampling, Beta-Bernoulli |
| Chat ingestion | twitchio 2.x + asyncio priority queue |
| Analytics API | FastAPI |
| Frontend dashboard | Next.js 15, Zustand, Recharts |
| Stream capture | FFmpeg RTMP pipe |

---

## Setup

### 1. Clone and install

```bash
git clone <repo>
cd autonomous-vtuber
pip install uv
uv sync
```

### 2. Configure credentials

Create `.env.local` in the project root:

```env
TWITCH_CLIENT_ID=
TWITCH_CLIENT_SECRET=
TWITCH_OAUTH_TOKEN=oauth:...        # get from twitchapps.com/tmi
TWITCH_CHANNEL=your_channel_name    # just the username, no URL

OPENAI_API_KEY=
ANTHROPIC_API_KEY=

NEO4J_URI=neo4j+s://...             # Neo4j Aura free tier
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=

TWITCH_STREAM_KEY=                  # for direct RTMP streaming (optional)
```

Open-LLM-VTuber has its own config at `open_llm_vtuber/conf.yaml`. Set the `llm_api_key` fields there to your OpenAI key and verify `base_url` points to `https://api.openai.com/v1`.

### 3. Run

**Terminal 1 — Avatar server:**
```bash
cd open_llm_vtuber
uv run run_server.py
# open http://localhost:12393 in a browser, or add as OBS browser source
```

**Terminal 2 — Twitch bot + bridge:**
```bash
python -m twitch_client.main
```

The bridge auto-connects to the avatar server and begins forwarding chat. You'll see `[bridge] Connected to Open-LLM-VTuber` when it's linked.

### 4. Stream to Twitch via OBS

In OBS, add a **Browser Source** pointed at `http://localhost:12393`. The avatar renders in the browser source and composites into your stream. For a transparent background, add this custom CSS in the browser source settings:

```css
body { background: transparent !important; }
```

---

## Self-improvement loop

Each stream produces a `StreamSummary`: peak viewers, revenue, engagement score, dominant activities.

`StreamRetrospective.update_bandit()` converts `revenue_per_hour` into a reward signal (capped at 1.0 at $50/hr) and pushes it into the bandit for every activity in `top_activities`. Activities that drove revenue gain alpha weight. Activities that didn't gain beta weight. The bandit's `select()` method samples from Beta distributions — arms with high alpha get picked more, but exploration is preserved through the distributional uncertainty.

This means:
- A `q_and_a` segment that triggered a donation wave → `q_and_a` arm's alpha increases
- An `idle` stretch with zero revenue → `idle` arm's beta increases
- Next stream, the orchestrator's activity recommendations are biased toward what worked

The `generate_recommendations()` method also produces human-readable stream notes — e.g. "Chat velocity was low — try more direct questions and polls" — that can inform manual tuning.

---

## Project structure

```
core/
  bandit.py          — Thompson Sampling bandit (self-improvement core)
  db.py              — Neo4j viewer/stream graph
  event_bus.py       — async pub/sub event bus
  interfaces.py      — shared Event, ChatMessage, StreamState types
  config.py          — pydantic-settings env config

agents/
  orchestrator.py    — Claude Opus tool-use loop (stream director)
  chat_agent.py      — message triage, donor/sub personalization
  performer.py       — TTS + expression control, WebSocket avatar
  analytics.py       — MetricsCollector, FastAPI /api/* endpoints
  retrospective.py   — post-stream summary + bandit weight updates
  donation_goals.py  — milestone tracker (25/50/75/100% callbacks)
  subscriber_tracker.py — sub tenure, tier breakdown, churn detection

twitch_client/
  main.py            — twitchio IRC bot
  priority_queue.py  — donations > subs > mods > regular chat
  bridge.py          — WebSocket bridge to Open-LLM-VTuber

streamer/
  ffmpeg_pipe.py     — direct RTMP stream via FFmpeg

dashboard/           — Next.js 15 stream ops UI

open_llm_vtuber/     — Live2D avatar server (subproject)
```

---

## Limitations

- **TTS rate limit**: OpenAI's free tier caps TTS at 3 requests/minute. Add a payment method at [platform.openai.com/account/billing](https://platform.openai.com/account/billing) to increase this.
- **No dance animations**: The `mao_pro` Live2D model supports facial expressions (`[joy]`, `[neutral]`, etc.) but has no body motion for commands like "dance". Swap the model in `open_llm_vtuber/model_dict.json` if you want a model with more motions.
- **Bandit cold start**: The Thompson bandit needs several streams before its priors are meaningful. For the first few streams, all five activity modes get roughly equal selection probability.
