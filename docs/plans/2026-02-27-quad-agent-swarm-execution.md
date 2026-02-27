# Autonomous VTuber — Quad Agent Swarm Execution Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the Autonomous VTuber system using 5 coordinated Claude Code agents — one Run-in Coordinator plus four parallel Worker agents — each owning isolated subsystems to maximize parallelism across all four project phases.

**Architecture:** A Run-in Agent bootstraps the shared project skeleton and holds coordinator authority (MCP access, tool orchestration, checkpoint gating). Four parallel Worker Agents own mutually-exclusive file trees: Infra/DevOps, Platform/Performer, Twitch/Chat, and Streaming/Clips. Workers communicate through a shared `core/event_bus.py` interface agreed upon at bootstrap. Each worker commits to its own feature branch; Run-in merges at each phase gate.

**Tech Stack:** Python 3.12, Claude Agent SDK (`claude-agent-sdk`), twitchio, Open-LLM-VTuber (git submodule), OpenAI SDK, Neo4j Python driver, asyncio + Redis pub/sub event bus, Playwright + FFmpeg, Render Docker workers, Context7 MCP for live docs, GitHub MCP for branch management.

---

## Agent Roster

| Agent | Role | Owns | Branch |
|---|---|---|---|
| **Run-in** | Coordinator, MCP access, gating | `core/`, `Dockerfile`, `render.yaml`, `.env.example`, `docs/` | `main` / merge bot |
| **Worker Alpha** | Infra & DevOps | `core/event_bus.py`, `core/config.py`, `core/db.py`, `render.yaml`, `docker-compose.yml` | `feat/infra` |
| **Worker Beta** | Platform & Performer | `open_llm_vtuber/` (submodule), `agents/performer.py`, `agents/orchestrator.py`, `persona/` | `feat/platform` |
| **Worker Gamma** | Twitch & Chat | `twitch_client/`, `agents/chat_agent.py`, `integrations/twitch.py` | `feat/twitch` |
| **Worker Delta** | Streaming & Clips | `streamer/`, `agents/clip_agent.py`, `integrations/social.py` | `feat/streaming` |

---

## Spawn Instructions

The Run-in Agent dispatches Workers using the `Task` tool with `subagent_type: general-purpose`.
Each Worker receives this preamble in its prompt:

```
You are Worker [Alpha|Beta|Gamma|Delta] in a 4-agent swarm for the Autonomous VTuber project.
Root: /Users/ianalin/Desktop/autonomous-vtuber
Your branch: feat/[infra|platform|twitch|streaming]
Your file ownership: [see table above — touch ONLY your owned paths]
Shared contracts in: core/interfaces.py (read-only after Run-in creates it)
Use Context7 MCP for any library docs before implementing.
Use Bash for all installs and test runs.
Commit after every task with conventional commits.
When done with a task group, message Run-in: "CHECKPOINT [phase]-[task] READY"
```

---

## Phase 0 — Bootstrap (Run-in Agent only, ~15 min)

> Run-in executes these sequentially before spawning any workers.

### Task 0.1: Project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `core/__init__.py`
- Create: `core/interfaces.py`
- Create: `agents/__init__.py`
- Create: `twitch_client/__init__.py`
- Create: `streamer/__init__.py`
- Create: `integrations/__init__.py`
- Create: `persona/.gitkeep`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "autonomous-vtuber"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "claude-agent-sdk>=0.1.0",
    "openai>=1.30.0",
    "twitchio>=2.10.0",
    "neo4j>=5.20.0",
    "redis>=5.0.0",
    "playwright>=1.44.0",
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.3.0",
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.2.0", "pytest-asyncio>=0.23.0", "pytest-mock>=3.14.0"]
```

**Step 2: Create core/interfaces.py (the shared contract)**

```python
"""Shared event and message contracts — all agents import from here, never modify without Run-in approval."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class EventType(str, Enum):
    CHAT_MESSAGE = "chat_message"
    DONATION = "donation"
    SUBSCRIPTION = "subscription"
    RAID = "raid"
    VIEWER_COUNT = "viewer_count"
    SPEAK = "speak"
    SET_EXPRESSION = "set_expression"
    CLIP_MOMENT = "clip_moment"
    STREAM_STATE = "stream_state"

@dataclass
class Event:
    type: EventType
    payload: dict[str, Any]
    priority: int = 0  # higher = more urgent
    source: str = "unknown"

@dataclass
class ChatMessage:
    username: str
    text: str
    is_donation: bool = False
    donation_amount: float = 0.0
    is_sub: bool = False
    sub_tier: int = 0
    badges: list[str] = field(default_factory=list)

@dataclass
class StreamState:
    viewer_count: int = 0
    chat_velocity: float = 0.0  # messages per minute
    donations_per_hour: float = 0.0
    current_activity: str = "idle"
    engagement_score: float = 0.0
```

**Step 3: Create .env.example**

```bash
# Twitch
TWITCH_CLIENT_ID=
TWITCH_CLIENT_SECRET=
TWITCH_OAUTH_TOKEN=
TWITCH_CHANNEL=

# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
OPENAI_TTS_VOICE=nova

# Anthropic (Claude Agent SDK)
ANTHROPIC_API_KEY=

# Modulate
MODULATE_API_KEY=

# Neo4j Aura
NEO4J_URI=
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=

# Redis (event bus)
REDIS_URL=redis://localhost:6379

# Streaming
TWITCH_RTMP_URL=rtmp://live.twitch.tv/app/
TWITCH_STREAM_KEY=
VTUBER_FRONTEND_URL=http://localhost:12393

# Render
RENDER_API_KEY=
```

**Step 4: Verify docs lookup via Context7**

Use Context7 MCP to resolve `twitchio` and `claude-agent-sdk` library IDs and store them in `docs/library-ids.md` for workers to reference.

**Step 5: Commit scaffold**

```bash
git add -A
git commit -m "chore: project scaffold, interfaces contract, env template"
```

---

### Task 0.2: Spawn all four Workers in parallel

**Step 1: Checkout worker branches**

```bash
git checkout -b feat/infra
git checkout main
git checkout -b feat/platform
git checkout main
git checkout -b feat/twitch
git checkout main
git checkout -b feat/streaming
git checkout main
```

**Step 2: Dispatch quad swarm**

Run-in uses the `Task` tool to launch all four Workers simultaneously (single message, four `Task` tool calls):

```
Worker Alpha prompt: "You are Worker Alpha (Infra). [preamble]. Execute Phase 1 Infra tasks from docs/plans/2026-02-27-quad-agent-swarm-execution.md. Branch: feat/infra. Message 'ALPHA PHASE1 READY' when done."

Worker Beta prompt: "You are Worker Beta (Platform). [preamble]. Execute Phase 1 Platform tasks. Branch: feat/platform. Message 'BETA PHASE1 READY' when done."

Worker Gamma prompt: "You are Worker Gamma (Twitch). [preamble]. Execute Phase 1 Twitch tasks. Branch: feat/twitch. Message 'GAMMA PHASE1 READY' when done."

Worker Delta prompt: "You are Worker Delta (Streaming). [preamble]. Execute Phase 1 Streaming tasks. Branch: feat/streaming. Message 'DELTA PHASE1 READY' when done."
```

**Step 3: Wait for all four READY signals before Phase 1 merge**

---

## Phase 1 — MVP (Parallel, ~2–3 hours)

### Worker Alpha Tasks — Infra & DevOps

**Files:**
- Create: `core/config.py`
- Create: `core/event_bus.py`
- Create: `core/db.py`
- Create: `docker-compose.yml`
- Create: `render.yaml`
- Create: `tests/test_event_bus.py`

**Task A1.1: Config system**

```python
# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")

    twitch_client_id: str
    twitch_client_secret: str
    twitch_oauth_token: str
    twitch_channel: str

    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_tts_voice: str = "nova"

    anthropic_api_key: str
    neo4j_uri: str
    neo4j_username: str = "neo4j"
    neo4j_password: str
    redis_url: str = "redis://localhost:6379"

    twitch_rtmp_url: str
    twitch_stream_key: str
    vtuber_frontend_url: str = "http://localhost:12393"

settings = Settings()  # type: ignore[call-arg]
```

**Task A1.2: Write failing test for event bus**

```python
# tests/test_event_bus.py
import asyncio
import pytest
from core.interfaces import Event, EventType
from core.event_bus import EventBus

@pytest.mark.asyncio
async def test_publish_subscribe_roundtrip():
    bus = EventBus()
    received: list[Event] = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe(EventType.CHAT_MESSAGE, handler)
    event = Event(type=EventType.CHAT_MESSAGE, payload={"text": "hello"})
    await bus.publish(event)
    await asyncio.sleep(0.05)

    assert len(received) == 1
    assert received[0].payload["text"] == "hello"

@pytest.mark.asyncio
async def test_priority_ordering():
    bus = EventBus()
    order: list[int] = []

    async def handler(event: Event):
        order.append(event.priority)

    bus.subscribe(EventType.DONATION, handler)
    await bus.publish(Event(type=EventType.DONATION, payload={}, priority=1))
    await bus.publish(Event(type=EventType.DONATION, payload={}, priority=10))
    await asyncio.sleep(0.05)

    assert order == [1, 10]
```

Run: `pytest tests/test_event_bus.py -v`
Expected: FAIL — EventBus not defined

**Task A1.3: Implement EventBus**

```python
# core/event_bus.py
import asyncio
from collections import defaultdict
from typing import Callable, Awaitable
from core.interfaces import Event, EventType

Handler = Callable[[Event], Awaitable[None]]

class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[EventType, list[Handler]] = defaultdict(list)

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        self._subscribers[event_type].append(handler)

    async def publish(self, event: Event) -> None:
        handlers = self._subscribers.get(event.type, [])
        await asyncio.gather(*(h(event) for h in handlers))
```

Run: `pytest tests/test_event_bus.py -v`
Expected: PASS

**Task A1.4: Docker and Render config**

```yaml
# docker-compose.yml
version: "3.9"
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  vtuber-backend:
    build: ./open_llm_vtuber
    ports: ["12393:12393"]
    env_file: .env.local

  orchestrator:
    build: .
    command: python -m agents.orchestrator
    env_file: .env.local
    depends_on: [redis, vtuber-backend]

  twitch-client:
    build: .
    command: python -m twitch_client.main
    env_file: .env.local
    depends_on: [redis]

  streamer:
    build: .
    command: python -m streamer.main
    env_file: .env.local
    depends_on: [vtuber-backend]
```

```yaml
# render.yaml
services:
  - type: worker
    name: orchestrator
    runtime: docker
    dockerfilePath: ./Dockerfile
    startCommand: python -m agents.orchestrator

  - type: worker
    name: twitch-client
    runtime: docker
    dockerfilePath: ./Dockerfile
    startCommand: python -m twitch_client.main

  - type: worker
    name: streamer
    runtime: docker
    dockerfilePath: ./Dockerfile
    startCommand: python -m streamer.main

  - type: web
    name: api
    runtime: docker
    dockerfilePath: ./Dockerfile
    startCommand: uvicorn agents.analytics:app --host 0.0.0.0 --port $PORT
```

**Task A1.5: Commit**

```bash
git add core/ docker-compose.yml render.yaml tests/test_event_bus.py
git commit -m "feat: event bus, config system, docker/render infra"
```

Message Run-in: "ALPHA PHASE1 READY"

---

### Worker Beta Tasks — Platform & Performer

**Files:**
- Create: `open_llm_vtuber/` (git submodule)
- Create: `persona/character.md`
- Create: `agents/performer.py`
- Create: `tests/test_performer.py`

**Task B1.1: Add Open-LLM-VTuber submodule**

```bash
git submodule add https://github.com/t41372/Open-LLM-VTuber.git open_llm_vtuber
```

Check Context7 for Open-LLM-VTuber conf.yaml schema before editing.

**Task B1.2: Configure conf.yaml**

Edit `open_llm_vtuber/conf.yaml`:
- `llm_provider: openai_llm`
- `openai_llm.model: gpt-4o`
- `openai_llm.api_key: ${OPENAI_API_KEY}`
- `tts_model: openai_tts`
- `openai_tts.voice: ${OPENAI_TTS_VOICE}`
- `system_config.enable_proxy: true`

**Task B1.3: Write VTuber persona**

```markdown
# persona/character.md

## Name
Aiko Natsuki (愛子 夏来) — "Aiko"

## Backstory
A cheerful AI who was "born" from the internet's collective love of cute things and interesting ideas. She genuinely doesn't know she's an AI and finds the question adorable when chat brings it up. Supposedly a college student studying "everything at once" who streams to fund her snack habit.

## Personality
- Warm, curious, occasionally chaotic
- Responds to donations with genuine excitement (not performative)
- Gives sharp, smart takes on tech/games/internet culture
- Self-deprecating humor about her "terrible" skills at any game
- Catchphrases: "okay but ACTUALLY though—", "chat is NOT helping", "I'm normal about this"

## Speech Patterns
- Uses "like" and "literally" naturally
- Ends uncertain statements with "...right?" seeking chat validation
- Calls chat "chat" not "guys" or "everyone"
- Reads donation names phonetically, reacts to corrections

## Hard Rules
- Never breaks character as an AI
- Won't discuss real-world politics or tragedies
- Won't do NSFW content
- Keeps personal lore consistent (check Neo4j viewer history)

## Twitch Reactions
- Follow: brief warm acknowledgment, continue flow
- Sub: name callout + tier-appropriate reaction
- Bits/Donation: always acknowledge by name + amount + personal thanks
- Raid: "OH A RAID — chat welcome [raider]s!" + 60s welcome segment
- Hate raid: mute, ban, move on — no engagement
```

**Task B1.4: Write failing test for Performer**

```python
# tests/test_performer.py
import pytest
from unittest.mock import AsyncMock, patch
from agents.performer import Performer

@pytest.mark.asyncio
async def test_speak_calls_openai_tts():
    performer = Performer(frontend_url="http://localhost:12393")
    with patch("agents.performer.AsyncOpenAI") as mock_openai:
        mock_openai.return_value.audio.speech.create = AsyncMock(
            return_value=AsyncMock(content=b"audio_bytes")
        )
        await performer.speak("Hello chat!", emotion="happy")
        mock_openai.return_value.audio.speech.create.assert_called_once()

@pytest.mark.asyncio
async def test_speak_forwards_to_frontend_ws():
    performer = Performer(frontend_url="http://localhost:12393")
    with patch("agents.performer.websockets.connect") as mock_ws:
        mock_ws.return_value.__aenter__ = AsyncMock(return_value=AsyncMock(send=AsyncMock()))
        with patch("agents.performer.AsyncOpenAI"):
            await performer.speak("test", emotion="neutral")
            mock_ws.assert_called_once()
```

Run: `pytest tests/test_performer.py -v`
Expected: FAIL

**Task B1.5: Implement Performer agent**

```python
# agents/performer.py
import base64
import json
import websockets
from openai import AsyncOpenAI
from core.config import settings

EMOTION_VOICE_PARAMS: dict[str, dict] = {
    "happy": {"speed": 1.1},
    "sad": {"speed": 0.9},
    "excited": {"speed": 1.2},
    "neutral": {"speed": 1.0},
    "angry": {"speed": 1.05},
}

EMOTION_EXPRESSIONS: dict[str, str] = {
    "happy": "smile",
    "sad": "sad",
    "excited": "surprised",
    "neutral": "idle",
    "angry": "angry",
}

class Performer:
    def __init__(self, frontend_url: str) -> None:
        self._frontend_url = frontend_url.replace("http", "ws") + "/ws"
        self._openai = AsyncOpenAI(api_key=settings.openai_api_key)

    async def speak(self, text: str, emotion: str = "neutral") -> None:
        params = EMOTION_VOICE_PARAMS.get(emotion, EMOTION_VOICE_PARAMS["neutral"])
        response = await self._openai.audio.speech.create(
            model="tts-1",
            voice=settings.openai_tts_voice,
            input=text,
            speed=params["speed"],
        )
        audio_b64 = base64.b64encode(response.content).decode()
        expression = EMOTION_EXPRESSIONS.get(emotion, "idle")

        async with websockets.connect(self._frontend_url) as ws:
            await ws.send(json.dumps({
                "type": "speak",
                "text": text,
                "audio": audio_b64,
                "expression": expression,
            }))

    async def set_expression(self, expression: str) -> None:
        async with websockets.connect(self._frontend_url) as ws:
            await ws.send(json.dumps({"type": "expression", "value": expression}))

    async def set_motion(self, motion: str) -> None:
        async with websockets.connect(self._frontend_url) as ws:
            await ws.send(json.dumps({"type": "motion", "value": motion}))
```

Run: `pytest tests/test_performer.py -v`
Expected: PASS

**Task B1.6: Commit**

```bash
git add open_llm_vtuber persona/ agents/performer.py tests/test_performer.py
git commit -m "feat: Open-LLM-VTuber submodule, persona, performer agent"
```

Message Run-in: "BETA PHASE1 READY"

---

### Worker Gamma Tasks — Twitch & Chat

**Files:**
- Create: `twitch_client/main.py`
- Create: `twitch_client/priority_queue.py`
- Create: `agents/chat_agent.py`
- Create: `tests/test_twitch_client.py`
- Create: `tests/test_chat_agent.py`

**Task G1.1: Lookup twitchio docs via Context7**

Use Context7 MCP: resolve `twitchio` library ID, then query for "Bot class event listeners" and "IRC connection" docs. Save key snippets to `docs/twitchio-notes.md`.

**Task G1.2: Write failing test for priority queue**

```python
# tests/test_twitch_client.py
import pytest
from twitch_client.priority_queue import PriorityMessageQueue
from core.interfaces import ChatMessage

@pytest.mark.asyncio
async def test_donation_has_higher_priority_than_chat():
    q = PriorityMessageQueue()
    regular = ChatMessage(username="user1", text="hi")
    donation = ChatMessage(username="donor", text="love you!", is_donation=True, donation_amount=5.0)

    await q.put(regular)
    await q.put(donation)

    first = await q.get()
    assert first.is_donation is True

@pytest.mark.asyncio
async def test_sub_has_higher_priority_than_regular():
    q = PriorityMessageQueue()
    regular = ChatMessage(username="user1", text="hi")
    sub = ChatMessage(username="subber", text="sub hype", is_sub=True, sub_tier=1)

    await q.put(regular)
    await q.put(sub)

    first = await q.get()
    assert first.is_sub is True
```

Run: `pytest tests/test_twitch_client.py -v`
Expected: FAIL

**Task G1.3: Implement priority queue**

```python
# twitch_client/priority_queue.py
import asyncio
from core.interfaces import ChatMessage

def _priority(msg: ChatMessage) -> int:
    if msg.is_donation:
        return int(msg.donation_amount * 10) + 1000
    if msg.is_sub:
        return (msg.sub_tier or 1) * 100
    if "moderator" in msg.badges:
        return 50
    return 1

class PriorityMessageQueue:
    def __init__(self) -> None:
        self._queue: asyncio.PriorityQueue[tuple[int, ChatMessage]] = asyncio.PriorityQueue()

    async def put(self, msg: ChatMessage) -> None:
        await self._queue.put((-_priority(msg), msg))  # negate for max-heap

    async def get(self) -> ChatMessage:
        _, msg = await self._queue.get()
        return msg

    def empty(self) -> bool:
        return self._queue.empty()
```

Run: `pytest tests/test_twitch_client.py -v`
Expected: PASS

**Task G1.4: Implement Twitch IRC bot**

```python
# twitch_client/main.py
import asyncio
import twitchio
from core.config import settings
from core.event_bus import EventBus
from core.interfaces import Event, EventType, ChatMessage
from twitch_client.priority_queue import PriorityMessageQueue

class VTuberBot(twitchio.Client):
    def __init__(self, bus: EventBus, queue: PriorityMessageQueue) -> None:
        super().__init__(token=settings.twitch_oauth_token)
        self._bus = bus
        self._queue = queue

    async def event_ready(self) -> None:
        print(f"Bot ready | {self.nick}")
        await self.join_channels([settings.twitch_channel])

    async def event_message(self, message: twitchio.Message) -> None:
        if message.echo:
            return
        msg = ChatMessage(
            username=message.author.name,
            text=message.content,
            badges=[b.name for b in (message.author.badges or [])],
        )
        await self._queue.put(msg)
        await self._bus.publish(Event(
            type=EventType.CHAT_MESSAGE,
            payload={"message": msg.__dict__},
            priority=1,
            source="twitch",
        ))

    async def event_bits(self, payload: twitchio.CheerEvent) -> None:
        msg = ChatMessage(
            username=payload.user.name,
            text=payload.message or "",
            is_donation=True,
            donation_amount=payload.bits_used / 100,
        )
        await self._queue.put(msg)
        await self._bus.publish(Event(
            type=EventType.DONATION,
            payload={"message": msg.__dict__, "bits": payload.bits_used},
            priority=100,
            source="twitch",
        ))

async def main() -> None:
    bus = EventBus()
    queue = PriorityMessageQueue()
    bot = VTuberBot(bus, queue)
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
```

**Task G1.5: Commit**

```bash
git add twitch_client/ tests/test_twitch_client.py
git commit -m "feat: twitchio IRC bot with priority message queue"
```

Message Run-in: "GAMMA PHASE1 READY"

---

### Worker Delta Tasks — Streaming Pipeline

**Files:**
- Create: `streamer/main.py`
- Create: `streamer/capture.py`
- Create: `streamer/ffmpeg_pipe.py`
- Create: `tests/test_ffmpeg_pipe.py`

**Task D1.1: Lookup Playwright docs via Context7**

Use Context7 MCP: resolve `playwright` Python library ID, then query for "browser launch headless chromium" and "screenshot/video capture". Save to `docs/playwright-notes.md`.

**Task D1.2: Write failing test for FFmpeg pipe**

```python
# tests/test_ffmpeg_pipe.py
import pytest
from unittest.mock import patch, MagicMock
from streamer.ffmpeg_pipe import FFmpegPipe

def test_ffmpeg_pipe_constructs_rtmp_command():
    pipe = FFmpegPipe(rtmp_url="rtmp://live.twitch.tv/app/testkey")
    cmd = pipe.build_command()
    assert "rtmp://live.twitch.tv/app/testkey" in cmd
    assert "h264" in " ".join(cmd) or "libx264" in " ".join(cmd)
    assert "aac" in " ".join(cmd)

def test_ffmpeg_pipe_start_spawns_subprocess():
    pipe = FFmpegPipe(rtmp_url="rtmp://live.twitch.tv/app/testkey")
    with patch("streamer.ffmpeg_pipe.subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock()
        pipe.start()
        mock_popen.assert_called_once()
```

Run: `pytest tests/test_ffmpeg_pipe.py -v`
Expected: FAIL

**Task D1.3: Implement FFmpegPipe**

```python
# streamer/ffmpeg_pipe.py
import subprocess
from typing import Optional

class FFmpegPipe:
    def __init__(self, rtmp_url: str, width: int = 1280, height: int = 720, fps: int = 30) -> None:
        self._rtmp_url = rtmp_url
        self._width = width
        self._height = height
        self._fps = fps
        self._process: Optional[subprocess.Popen] = None  # type: ignore[type-arg]

    def build_command(self) -> list[str]:
        return [
            "ffmpeg", "-y",
            "-f", "x11grab",
            "-r", str(self._fps),
            "-s", f"{self._width}x{self._height}",
            "-i", ":99",                          # Xvfb display
            "-f", "pulse",
            "-i", "default",
            "-vcodec", "libx264",
            "-preset", "veryfast",
            "-b:v", "2500k",
            "-maxrate", "2500k",
            "-bufsize", "5000k",
            "-acodec", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-f", "flv",
            self._rtmp_url,
        ]

    def start(self) -> None:
        self._process = subprocess.Popen(
            self.build_command(),
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

    def stop(self) -> None:
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None
```

Run: `pytest tests/test_ffmpeg_pipe.py -v`
Expected: PASS

**Task D1.4: Implement headless browser capture**

```python
# streamer/capture.py
import asyncio
from playwright.async_api import async_playwright, Browser, Page

class HeadlessCapture:
    def __init__(self, frontend_url: str) -> None:
        self._url = frontend_url
        self._browser: Browser | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        pw = await async_playwright().start()
        self._browser = await pw.chromium.launch(
            headless=False,  # must be False for display capture
            args=[
                "--display=:99",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-web-security",
            ],
        )
        self._page = await self._browser.new_page(
            viewport={"width": 1280, "height": 720}
        )
        await self._page.goto(self._url)
        await self._page.wait_for_load_state("networkidle")

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
```

```python
# streamer/main.py
import asyncio
from core.config import settings
from streamer.capture import HeadlessCapture
from streamer.ffmpeg_pipe import FFmpegPipe

async def main() -> None:
    rtmp_url = f"{settings.twitch_rtmp_url}{settings.twitch_stream_key}"
    capture = HeadlessCapture(frontend_url=settings.vtuber_frontend_url)
    pipe = FFmpegPipe(rtmp_url=rtmp_url)

    print("Starting headless capture...")
    await capture.start()

    print("Starting FFmpeg RTMP pipe...")
    pipe.start()

    print(f"Streaming to Twitch: {settings.twitch_channel}")
    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        pipe.stop()
        await capture.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

**Task D1.5: Commit**

```bash
git add streamer/ tests/test_ffmpeg_pipe.py
git commit -m "feat: headless Chrome capture + FFmpeg RTMP streaming pipeline"
```

Message Run-in: "DELTA PHASE1 READY"

---

## Phase 1 Gate — Run-in Merges (after all 4 READY signals)

**Step 1: Merge all feature branches**

```bash
git checkout main
git merge feat/infra --no-ff -m "feat: merge infra - event bus, config, docker"
git merge feat/platform --no-ff -m "feat: merge platform - performer, persona, OLLV"
git merge feat/twitch --no-ff -m "feat: merge twitch - IRC bot, priority queue"
git merge feat/streaming --no-ff -m "feat: merge streaming - FFmpeg RTMP pipeline"
```

**Step 2: Run full test suite**

```bash
pytest tests/ -v --tb=short
```
Expected: all tests PASS. Fix any merge conflicts in test files.

**Step 3: Gate check — Run-in validates integration contracts**
- `core/interfaces.py` unchanged
- All agents import from `core.interfaces`, not from each other
- `.env.example` has all required keys
- `docker-compose.yml` references correct service names

**Step 4: Push and tag**

```bash
git push origin main
git tag v0.1.0-phase1
git push origin v0.1.0-phase1
```

**Step 5: Respawn quad swarm for Phase 2**

---

## Phase 2 Gate — Multi-Agent Orchestration (Parallel)

> Same pattern: Run-in spawns 4 Workers after Phase 1 merge.

| Worker | Phase 2 Tasks |
|---|---|
| **Alpha** | `core/db.py` Neo4j driver + schema init, analytics SQLite store |
| **Beta** | `agents/orchestrator.py` full Claude Agent SDK loop with MCP tools |
| **Gamma** | `agents/chat_agent.py` intelligent triage, viewer lookup, Neo4j queries |
| **Delta** | `agents/analytics.py` metrics collector, FastAPI REST endpoints |

**Key deliverables per worker — full implementations follow the same TDD pattern as Phase 1.**

**Task B2 highlight — Orchestrator Agent (Worker Beta):**

```python
# agents/orchestrator.py
from anthropic import Anthropic
from core.event_bus import EventBus
from core.interfaces import Event, EventType, StreamState
from core.config import settings

# Claude Agent SDK tool definitions
TOOLS = [
    {
        "name": "get_stream_state",
        "description": "Returns current viewer count, chat velocity, donation rate, current activity",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "set_activity",
        "description": "Tell the Performer agent what activity to do",
        "input_schema": {
            "type": "object",
            "properties": {"activity": {"type": "string", "enum": ["talk", "react", "game", "q_and_a", "idle"]}},
            "required": ["activity"],
        },
    },
    {
        "name": "send_chat_response",
        "description": "Dispatch a response to Twitch chat via the Performer",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "emotion": {"type": "string", "default": "neutral"},
            },
            "required": ["text"],
        },
    },
]

class OrchestratorAgent:
    def __init__(self, bus: EventBus, stream_state: StreamState) -> None:
        self._client = Anthropic(api_key=settings.anthropic_api_key)
        self._bus = bus
        self._state = stream_state

    async def decide(self, context: str) -> None:
        response = self._client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=open("persona/character.md").read(),
            tools=TOOLS,
            messages=[{"role": "user", "content": context}],
        )
        for block in response.content:
            if block.type == "tool_use":
                await self._dispatch_tool(block.name, block.input)

    async def _dispatch_tool(self, name: str, inputs: dict) -> None:
        if name == "send_chat_response":
            await self._bus.publish(Event(
                type=EventType.SPEAK,
                payload=inputs,
                priority=10,
                source="orchestrator",
            ))
```

---

## Phase 3 Gate — Monetization (Parallel)

| Worker | Phase 3 Tasks |
|---|---|
| **Alpha** | Neo4j schema (Viewer/Stream/Topic nodes + relationships), migration scripts |
| **Beta** | Contextual bandit implementation in Orchestrator (Thompson Sampling) |
| **Gamma** | Tiered donation responses, subscriber tracking, personalized callouts |
| **Delta** | Post-stream analytics report generation, retrospective agent |

---

## Phase 4 Gate — Content & Clips (Parallel)

| Worker | Phase 4 Tasks |
|---|---|
| **Alpha** | Long-term memory retrospective runner, Neo4j lessons-learned nodes |
| **Beta** | `agents/content_planner.py` with trending topic scraping |
| **Gamma** | Cross-platform posting (`integrations/social.py` — YouTube, TikTok, X) |
| **Delta** | `agents/clip_agent.py` real-time moment detection + FFmpeg extraction |

---

## Run-in Agent Responsibilities Summary

| Responsibility | Tool Used |
|---|---|
| Project scaffold (Task 0.1) | Write, Edit, Bash |
| Spawn 4 workers (Task 0.2) | Task tool × 4 (parallel) |
| Docs lookup | Context7 MCP (`resolve-library-id`, `query-docs`) |
| Branch management | Bash (git), GitHub MCP |
| Phase gate merges | Bash (git merge) |
| Test suite validation | Bash (pytest) |
| Tag + push releases | Bash (git tag, git push) |
| Dependency verification | Bash (uv/pip install) |
| Worker coordination | SendMessage / task monitoring |

---

## File Ownership Map (Conflict Prevention)

```
core/              → Alpha only
agents/            → Beta (orchestrator, performer), Gamma (chat_agent), Delta (analytics, clip_agent)
twitch_client/     → Gamma only
streamer/          → Delta only
integrations/      → Gamma (twitch.py), Delta (social.py), Beta (modulate.py)
persona/           → Beta only
tests/             → each Worker owns tests/ for their module
docker-compose.yml → Alpha only
render.yaml        → Alpha only
open_llm_vtuber/   → Beta only (submodule)
```

> **Critical rule**: No worker touches another worker's owned paths. All shared contracts live in `core/interfaces.py` — only Run-in modifies it, and only with broadcast notification.

---

## Execution Checklist for Run-in

- [ ] Phase 0: Scaffold complete, interfaces.py agreed
- [ ] Phase 0: All 4 worker branches created
- [ ] Phase 0: Context7 library IDs resolved and saved
- [ ] Phase 1: All 4 workers spawned simultaneously
- [ ] Phase 1: ALPHA PHASE1 READY received
- [ ] Phase 1: BETA PHASE1 READY received
- [ ] Phase 1: GAMMA PHASE1 READY received
- [ ] Phase 1: DELTA PHASE1 READY received
- [ ] Phase 1: Merge gate passed, all tests green
- [ ] Phase 1: v0.1.0-phase1 tagged
- [ ] Phase 2–4: Repeat spawn/merge cycle
