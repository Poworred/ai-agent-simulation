# AI 南大 Agent Simulation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable web MVP where 5-8 fictional campus agents live through a simplified Nanchang University week, with FastAPI simulation logic, Next.js visualization, SQLite persistence, memory, Game Master validation, and real Claude-powered dialogue/reflection/intervention handling.

**Architecture:** Use a two-app monorepo: `backend/` contains FastAPI, SQLModel/SQLite, the simulation engine, Game Master, memory retrieval, and LLM provider abstraction; `frontend/` contains a Next.js TypeScript UI that polls backend tick/state APIs. The first implementation proceeds from deterministic rule simulation to LLM-enhanced key moments so every milestone is demonstrable and testable.

**Tech Stack:** Python 3.11+, FastAPI, SQLModel, SQLite, Pydantic v2, Anthropic Python SDK, pytest, httpx; Node 22+, Next.js, TypeScript, Tailwind CSS, Playwright.

---

## Source Documents

Read these before implementing:

- Spec: `docs/superpowers/specs/2026-06-21-ai-nanda-agent-simulation-design.md`
- Overview: `00_项目总览.md`
- PRD: `01_PRD_AI南大_多智能体校园社会模拟系统.md`
- Project memory: `02_项目记忆.md`
- References: `03_参考项目与论文.md`
- MVP breakdown: `05_MVP任务拆解.md`

## Research Reinforcement

The 2026-06-21 deep research pass confirmed the plan direction:

- Stanford Generative Agents is the stronger MVP engineering reference: small-scale, replayable, memory-stream-driven, with environment/visualization separated from agent simulation.
- AIvilization/Aivilization is the stronger long-term design reference: unified LLM-agent architecture, branch-thinking, dual-process memory, human steering, and action feasibility validation.
- Implementation should therefore prioritize a Stanford-style small campus simulation first, then leave seams for AIvilization-style resource/institution constraints later.

Implementation implications:

- Treat `events` as replay/debug/memory infrastructure, not just UI feed.
- Keep `GameMaster` as mandatory world arbiter for all state mutations.
- Keep seed data structured so persona/history/memory can later be imported from JSON or CSV.
- Do not expand MVP into MMO, large-scale society, or complex economy during this plan.

## File Structure

Create this project structure. Keep files focused and small; do not place all simulation logic in one large file.

```text
backend/
  pyproject.toml
  .env.example
  app/
    __init__.py
    main.py
    api/
      __init__.py
      agents.py
      debug.py
      events.py
      runs.py
    core/
      __init__.py
      config.py
      ids.py
      time.py
    db/
      __init__.py
      session.py
    domain/
      __init__.py
      actions.py
      constants.py
      schemas.py
    models/
      __init__.py
      tables.py
    seed/
      __init__.py
      seed_data.py
      seed_service.py
    services/
      __init__.py
      action_selector.py
      events.py
      game_master.py
      llm_service.py
      memory.py
      relationships.py
      safety.py
      simulation.py
    llm/
      __init__.py
      anthropic_provider.py
      base.py
      fake_provider.py
      prompts.py
      schemas.py
  tests/
    conftest.py
    test_action_selector.py
    test_agents_api.py
    test_game_master.py
    test_health.py
    test_interventions.py
    test_llm_contracts.py
    test_memory.py
    test_runs_api.py
    test_simulation_tick.py

frontend/
  package.json
  next.config.ts
  tsconfig.json
  postcss.config.mjs
  tailwind.config.ts
  src/
    app/
      globals.css
      layout.tsx
      page.tsx
      about/page.tsx
    components/
      AgentDetailPanel.tsx
      AgentSidebar.tsx
      CampusMap.tsx
      EventFeed.tsx
      SimulationHeader.tsx
    lib/
      api.ts
      time.ts
    types/
      simulation.ts
  tests/
    simulation.spec.ts

README.md
docs/testing/manual-test-checklist.md
```

## Cross-Cutting Implementation Rules

- Use `tick_minutes = 30` by default.
- Start simulations at `Day 1 07:30`, represented as `current_day=1`, `current_minute=450`.
- Mark a run completed after `Day 7 23:30`.
- Use fictional agents only. Do not model real students.
- Put all mutable world changes through `GameMaster`; LLMs may propose actions but may not write state directly.
- Use Claude API via a provider abstraction. Default model: `claude-opus-4-6`; use `thinking={"type": "adaptive"}` for complex generation. Prefer structured JSON output and Pydantic validation.
- Default tests must not call real LLMs. Real calls are behind `RUN_LLM_TESTS=1` or `pytest -m llm`.
- If this directory remains non-git, skip commit commands during execution and note that commits were skipped because the project is not a git repo. If a git repo is initialized later, use the commit checkpoints in each task.

---

### Task 0: Create Backend and Frontend Skeletons

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`
- Create: `frontend/package.json`
- Create: `frontend/next.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/app/layout.tsx`
- Create: `frontend/src/app/page.tsx`
- Create: `frontend/src/app/globals.css`

- [ ] **Step 1: Write the failing backend health test**

Create `backend/tests/test_health.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run the backend health test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_health.py -v
```

Expected: FAIL because `app.main` or `/health` does not exist yet.

- [ ] **Step 3: Create backend package configuration**

Create `backend/pyproject.toml`:

```toml
[project]
name = "ai-nanda-backend"
version = "0.1.0"
description = "FastAPI backend for AI Nanda multi-agent campus simulation"
requires-python = ">=3.11"
dependencies = [
  "anthropic>=0.74.0",
  "fastapi>=0.115.0",
  "httpx>=0.27.0",
  "pydantic>=2.10.0",
  "pydantic-settings>=2.7.0",
  "sqlmodel>=0.0.22",
  "uvicorn[standard]>=0.34.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.0",
  "pytest-asyncio>=0.24.0",
  "ruff>=0.8.0",
]

[tool.pytest.ini_options]
pythonpath = ["."]
markers = [
  "llm: tests that make real LLM API calls",
]

[tool.ruff]
line-length = 100
```

- [ ] **Step 4: Create backend environment example**

Create `backend/.env.example`:

```bash
DATABASE_URL=sqlite:///./ai_nanda.db
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-opus-4-6
LLM_PROVIDER=fake
DEFAULT_TICK_MINUTES=30
```

- [ ] **Step 5: Create backend settings**

Create `backend/app/core/config.py`:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ai_nanda.db"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-opus-4-6"
    llm_provider: str = "fake"
    default_tick_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 6: Create FastAPI app with health endpoint**

Create `backend/app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="AI 南大 Simulation API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 7: Run backend health test to verify it passes**

Run:

```bash
cd backend && pytest tests/test_health.py -v
```

Expected: PASS `test_health_returns_ok`.

- [ ] **Step 8: Create frontend package configuration**

Create `frontend/package.json`:

```json
{
  "name": "ai-nanda-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "lint": "next lint",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "@types/node": "latest",
    "@types/react": "latest",
    "@types/react-dom": "latest",
    "next": "latest",
    "react": "latest",
    "react-dom": "latest",
    "typescript": "latest"
  },
  "devDependencies": {
    "@playwright/test": "latest",
    "autoprefixer": "latest",
    "postcss": "latest",
    "tailwindcss": "latest"
  }
}
```

- [ ] **Step 9: Create minimal Next.js files**

Create `frontend/next.config.ts`:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {};

export default nextConfig;
```

Create `frontend/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

Create `frontend/src/app/layout.tsx`:

```tsx
import "./globals.css";

export const metadata = {
  title: "AI 南大",
  description: "多智能体校园社会模拟系统",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
```

Create `frontend/src/app/page.tsx`:

```tsx
export default function HomePage() {
  return <main>AI 南大 Simulation</main>;
}
```

Create `frontend/src/app/globals.css`:

```css
:root {
  color-scheme: light;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

body {
  margin: 0;
  background: #f6f1e8;
  color: #241f1a;
}
```

- [ ] **Step 10: Install and build frontend**

Run:

```bash
cd frontend && npm install && npm run build
```

Expected: Next.js build succeeds.

- [ ] **Step 11: Commit checkpoint if git is available**

Run:

```bash
git status --short
```

If this is a git repo, commit:

```bash
git add backend frontend
git commit -m "chore: scaffold AI Nanda frontend and backend"
```

If not a git repo, record: `Skipped commit: project is not a git repository.`

---

### Task 1: Add Domain Constants, Time Helpers, and Database Models

**Files:**
- Create: `backend/app/domain/constants.py`
- Create: `backend/app/core/time.py`
- Create: `backend/app/core/ids.py`
- Create: `backend/app/models/tables.py`
- Create: `backend/app/db/session.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_simulation_tick.py`

- [ ] **Step 1: Write failing tests for time helpers**

Create `backend/tests/test_simulation_tick.py`:

```python
from app.core.time import format_sim_time, is_after_simulation_end, next_tick


def test_format_sim_time():
    assert format_sim_time(day=1, minute=450) == "Day 1 07:30"
    assert format_sim_time(day=7, minute=1410) == "Day 7 23:30"


def test_next_tick_rolls_to_next_day():
    assert next_tick(day=1, minute=1410, tick_minutes=30) == (2, 0)


def test_simulation_end_after_day_7_2330():
    assert is_after_simulation_end(day=7, minute=1410) is True
    assert is_after_simulation_end(day=7, minute=1380) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd backend && pytest tests/test_simulation_tick.py -v
```

Expected: FAIL because `app.core.time` does not exist.

- [ ] **Step 3: Implement constants**

Create `backend/app/domain/constants.py`:

```python
from enum import StrEnum


DEFAULT_START_DAY = 1
DEFAULT_START_MINUTE = 7 * 60 + 30
DEFAULT_END_DAY = 7
DEFAULT_END_MINUTE = 23 * 60 + 30
DEFAULT_TICK_MINUTES = 30


class RunStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class EventType(StrEnum):
    CLASS = "class"
    MEAL = "meal"
    SOCIAL = "social"
    CLUB = "club"
    LOST_ITEM = "lost_item"
    REFLECTION = "reflection"
    INTERVENTION = "intervention"
    SYSTEM = "system"
    MOVE = "move"


class ActionType(StrEnum):
    MOVE = "move"
    ATTEND_CLASS = "attend_class"
    EAT = "eat"
    TALK = "talk"
    JOIN_ACTIVITY = "join_activity"
    ASK_HELP = "ask_help"
    HANDLE_LOST_ITEM = "handle_lost_item"
    STUDY = "study"
    REST = "rest"
    REFLECT = "reflect"
    IDLE = "idle"
```

- [ ] **Step 4: Implement time helpers**

Create `backend/app/core/time.py`:

```python
from app.domain.constants import DEFAULT_END_DAY, DEFAULT_END_MINUTE


def format_sim_time(day: int, minute: int) -> str:
    hour = minute // 60
    mins = minute % 60
    return f"Day {day} {hour:02d}:{mins:02d}"


def next_tick(day: int, minute: int, tick_minutes: int) -> tuple[int, int]:
    new_minute = minute + tick_minutes
    new_day = day
    while new_minute >= 24 * 60:
        new_day += 1
        new_minute -= 24 * 60
    return new_day, new_minute


def is_after_simulation_end(day: int, minute: int) -> bool:
    return day > DEFAULT_END_DAY or (day == DEFAULT_END_DAY and minute >= DEFAULT_END_MINUTE)
```

- [ ] **Step 5: Implement ID helper**

Create `backend/app/core/ids.py`:

```python
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"
```

- [ ] **Step 6: Run time helper tests to verify they pass**

Run:

```bash
cd backend && pytest tests/test_simulation_tick.py -v
```

Expected: PASS all three tests.

- [ ] **Step 7: Implement SQLModel tables**

Create `backend/app/models/tables.py` with focused tables from the spec:

```python
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel

from app.domain.constants import DEFAULT_TICK_MINUTES, RunStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SimulationRun(SQLModel, table=True):
    __tablename__ = "simulation_runs"

    id: str = Field(primary_key=True)
    name: str
    current_day: int
    current_minute: int
    tick_minutes: int = DEFAULT_TICK_MINUTES
    status: str = RunStatus.PAUSED.value
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Location(SQLModel, table=True):
    __tablename__ = "locations"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    name: str
    type: str
    description: str
    x: int
    y: int
    open_minutes: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    available_actions: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    event_tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class Path(SQLModel, table=True):
    __tablename__ = "paths"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    from_location_id: str = Field(index=True)
    to_location_id: str = Field(index=True)
    distance_minutes: int


class Agent(SQLModel, table=True):
    __tablename__ = "agents"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    name: str
    role: str
    major: str
    personality: str
    interests: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    long_term_goals: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    social_style: str
    current_location_id: str = Field(index=True)
    current_goal: str
    current_action: str = "idle"
    mood: str = "neutral"
    energy: int = 80
    stress: int = 20
    adaptation_score: int = 0
    last_reflection_at: str | None = None


class Schedule(SQLModel, table=True):
    __tablename__ = "schedules"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_id: str = Field(index=True)
    day: int
    start_minute: int
    end_minute: int
    type: str
    title: str
    location_id: str
    priority: int = 0


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    day: int
    minute: int
    event_type: str
    location_id: str | None = None
    agent_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    summary: str
    details: str = ""
    visibility: str = "public"
    llm_generated: bool = False
    state_delta: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utc_now)


class Memory(SQLModel, table=True):
    __tablename__ = "memories"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_id: str = Field(index=True)
    memory_type: str
    content: str
    importance: int = 1
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    source: str = "system"
    related_agent_id: str | None = None
    related_event_id: str | None = None
    created_day: int
    created_minute: int
    last_accessed_at: datetime | None = None
    expires_at: datetime | None = None


class Relationship(SQLModel, table=True):
    __tablename__ = "relationships"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_a_id: str = Field(index=True)
    agent_b_id: str = Field(index=True)
    affinity: int = 0
    familiarity: int = 0
    trust: int = 0
    relationship_tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    last_interaction_event_id: str | None = None


class UserIntervention(SQLModel, table=True):
    __tablename__ = "user_interventions"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_id: str = Field(index=True)
    content: str
    status: str = "pending"
    created_day: int
    created_minute: int
    handled_event_id: str | None = None


class LLMCall(SQLModel, table=True):
    __tablename__ = "llm_calls"

    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    agent_id: str | None = Field(default=None, index=True)
    function_name: str
    prompt_version: str
    input_summary: str
    output_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    status: str
    latency_ms: int | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
```

- [ ] **Step 8: Implement database session helpers**

Create `backend/app/db/session.py`:

```python
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

engine = create_engine(get_settings().database_url, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

- [ ] **Step 9: Wire database startup**

Modify `backend/app/main.py`:

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.db.session import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    yield


app = FastAPI(title="AI 南大 Simulation API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

- [ ] **Step 10: Run backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all current tests pass.

- [ ] **Step 11: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests backend/pyproject.toml backend/.env.example
git commit -m "feat: add backend domain models and database setup"
```

---

### Task 2: Seed a Default Campus World

**Files:**
- Create: `backend/app/seed/seed_data.py`
- Create: `backend/app/seed/seed_service.py`
- Create: `backend/tests/test_runs_api.py`

- [ ] **Step 1: Write failing test for creating a run with seed data**

Create `backend/tests/test_runs_api.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_create_run_initializes_seed_world():
    client = TestClient(app)

    response = client.post("/api/runs", json={"name": "测试模拟"})

    assert response.status_code == 201
    body = response.json()
    assert body["run"]["current_day"] == 1
    assert body["run"]["current_minute"] == 450
    assert len(body["locations"]) >= 6
    assert len(body["agents"]) >= 5
    assert len(body["recent_events"]) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_runs_api.py::test_create_run_initializes_seed_world -v
```

Expected: FAIL because `/api/runs` is not implemented.

- [ ] **Step 3: Create seed data definitions**

Create `backend/app/seed/seed_data.py`:

```python
LOCATIONS = [
    {
        "id": "dorm",
        "name": "宿舍区",
        "type": "residence",
        "description": "新生最熟悉的起点，晚上适合休息和反思。",
        "x": 120,
        "y": 180,
        "available_actions": ["move", "rest", "talk"],
        "event_tags": ["rest", "social"],
    },
    {
        "id": "teaching_building",
        "name": "教学楼",
        "type": "academic",
        "description": "课程、迟到、问路和同班交流最常发生的地方。",
        "x": 380,
        "y": 130,
        "available_actions": ["move", "attend_class", "talk", "ask_help"],
        "event_tags": ["class", "lost", "social"],
    },
    {
        "id": "canteen",
        "name": "食堂",
        "type": "dining",
        "description": "饭点人流密集，容易发生拼桌、排队和偶遇。",
        "x": 300,
        "y": 310,
        "available_actions": ["move", "eat", "talk"],
        "event_tags": ["meal", "social"],
    },
    {
        "id": "library",
        "name": "图书馆",
        "type": "study",
        "description": "适合学习、安静反思，也可能发生失物招领事件。",
        "x": 560,
        "y": 250,
        "available_actions": ["move", "study", "talk", "handle_lost_item"],
        "event_tags": ["study", "lost_item"],
    },
    {
        "id": "stadium",
        "name": "体育场",
        "type": "sports",
        "description": "运动、社团活动和偶遇发生地。",
        "x": 170,
        "y": 430,
        "available_actions": ["move", "rest", "talk"],
        "event_tags": ["sports", "social"],
    },
    {
        "id": "club_fair",
        "name": "社团招新点",
        "type": "club",
        "description": "新生认识学长学姐、寻找归属感的关键地点。",
        "x": 520,
        "y": 420,
        "available_actions": ["move", "join_activity", "talk"],
        "event_tags": ["club", "social"],
    },
    {
        "id": "lost_and_found",
        "name": "失物招领处",
        "type": "service",
        "description": "校园卡、水杯和教材失而复得的地点。",
        "x": 650,
        "y": 350,
        "available_actions": ["move", "handle_lost_item", "talk"],
        "event_tags": ["lost_item", "service"],
    },
    {
        "id": "gate",
        "name": "校门 / 商业街",
        "type": "gate",
        "description": "校园边界和生活服务区域。",
        "x": 80,
        "y": 340,
        "available_actions": ["move", "talk", "rest"],
        "event_tags": ["life", "social"],
    },
]

PATHS = [
    ("dorm", "teaching_building", 20),
    ("dorm", "canteen", 15),
    ("dorm", "stadium", 20),
    ("teaching_building", "canteen", 10),
    ("teaching_building", "library", 10),
    ("canteen", "library", 15),
    ("canteen", "club_fair", 20),
    ("library", "club_fair", 15),
    ("library", "lost_and_found", 10),
    ("stadium", "club_fair", 20),
    ("gate", "dorm", 15),
    ("gate", "canteen", 20),
]

AGENTS = [
    {
        "id": "agent_wang_yinuo",
        "name": "王一诺",
        "role": "新生",
        "major": "软件工程",
        "personality": "有点社恐但责任感强，遇到问题会先自己扛一会儿。",
        "interests": ["编程", "羽毛球", "技术社团"],
        "long_term_goals": ["适应大学生活", "加入技术社团", "认识同专业朋友"],
        "social_style": "慢热，熟悉后话多",
    },
    {
        "id": "agent_chen_nian",
        "name": "陈念",
        "role": "新生",
        "major": "新闻传播",
        "personality": "外向、好奇、喜欢记录校园里的新鲜事。",
        "interests": ["摄影", "校园媒体", "探店"],
        "long_term_goals": ["加入校园媒体", "认识不同专业同学"],
        "social_style": "主动破冰",
    },
    {
        "id": "agent_zhou_lan",
        "name": "周岚",
        "role": "新生",
        "major": "临床医学",
        "personality": "认真谨慎，容易给自己压力，但很可靠。",
        "interests": ["阅读", "志愿服务", "跑步"],
        "long_term_goals": ["保持成绩", "找到稳定学习节奏"],
        "social_style": "礼貌克制",
    },
    {
        "id": "agent_lin_jianchuan",
        "name": "林见川",
        "role": "新生",
        "major": "软件工程",
        "personality": "方向感强，乐于帮忙，但不太主动表达情绪。",
        "interests": ["算法", "篮球", "校园地图"],
        "long_term_goals": ["找到学习伙伴", "参加比赛"],
        "social_style": "实用型社交",
    },
    {
        "id": "agent_li_mengyao",
        "name": "李梦瑶",
        "role": "新生",
        "major": "经济学",
        "personality": "目标明确，喜欢做计划，对社团和机会很敏感。",
        "interests": ["辩论", "商业分析", "社团活动"],
        "long_term_goals": ["锻炼表达能力", "加入有影响力的社团"],
        "social_style": "目标导向",
    },
    {
        "id": "agent_xu_qinghe",
        "name": "徐清和",
        "role": "学长",
        "major": "计算机科学与技术",
        "personality": "温和可靠，熟悉校园和社团流程。",
        "interests": ["开源", "社团管理"],
        "long_term_goals": ["帮助新生融入社团"],
        "social_style": "引导型",
    },
]
```

- [ ] **Step 4: Implement seed service**

Create `backend/app/seed/seed_service.py`:

```python
from sqlmodel import Session

from app.core.ids import new_id
from app.domain.constants import DEFAULT_START_DAY, DEFAULT_START_MINUTE, DEFAULT_TICK_MINUTES, EventType, RunStatus
from app.models.tables import Agent, Event, Location, Path, Schedule, SimulationRun
from app.seed.seed_data import AGENTS, LOCATIONS, PATHS


def create_seed_run(session: Session, name: str) -> SimulationRun:
    run = SimulationRun(
        id=new_id("run"),
        name=name,
        current_day=DEFAULT_START_DAY,
        current_minute=DEFAULT_START_MINUTE,
        tick_minutes=DEFAULT_TICK_MINUTES,
        status=RunStatus.PAUSED.value,
    )
    session.add(run)
    session.flush()

    for loc in LOCATIONS:
        session.add(Location(run_id=run.id, open_minutes={}, **loc))

    for from_id, to_id, distance in PATHS:
        session.add(Path(id=new_id("path"), run_id=run.id, from_location_id=from_id, to_location_id=to_id, distance_minutes=distance))
        session.add(Path(id=new_id("path"), run_id=run.id, from_location_id=to_id, to_location_id=from_id, distance_minutes=distance))

    for agent in AGENTS:
        session.add(
            Agent(
                run_id=run.id,
                current_location_id="dorm",
                current_goal="适应大学第一周生活",
                **agent,
            )
        )

    _seed_schedules(session, run.id)

    session.add(
        Event(
            id=new_id("event"),
            run_id=run.id,
            day=run.current_day,
            minute=run.current_minute,
            event_type=EventType.SYSTEM.value,
            summary="AI 南大的一周模拟开始了，第一批新生正在宿舍区整理自己的计划。",
            details="系统初始化了地点、路径、角色、课表和初始事件。",
        )
    )
    session.commit()
    session.refresh(run)
    return run


def _seed_schedules(session: Session, run_id: str) -> None:
    class_agents = ["agent_wang_yinuo", "agent_chen_nian", "agent_zhou_lan", "agent_lin_jianchuan", "agent_li_mengyao"]
    for day in range(1, 8):
        for agent_id in class_agents:
            session.add(Schedule(id=new_id("schedule"), run_id=run_id, agent_id=agent_id, day=day, start_minute=8 * 60 + 30, end_minute=10 * 60, type="class", title="上午课程", location_id="teaching_building", priority=10))
            session.add(Schedule(id=new_id("schedule"), run_id=run_id, agent_id=agent_id, day=day, start_minute=12 * 60, end_minute=13 * 60, type="meal", title="午饭", location_id="canteen", priority=8))
            session.add(Schedule(id=new_id("schedule"), run_id=run_id, agent_id=agent_id, day=day, start_minute=22 * 60 + 30, end_minute=23 * 60, type="rest", title="晚间反思", location_id="dorm", priority=9))
        if day in {1, 2, 3}:
            for agent_id in class_agents:
                session.add(Schedule(id=new_id("schedule"), run_id=run_id, agent_id=agent_id, day=day, start_minute=16 * 60, end_minute=18 * 60, type="club", title="社团招新", location_id="club_fair", priority=6))
```

- [ ] **Step 5: Implement response schemas for runs**

Create `backend/app/domain/schemas.py`:

```python
from pydantic import BaseModel


class CreateRunRequest(BaseModel):
    name: str = "AI 南大默认模拟"


class RunRead(BaseModel):
    id: str
    name: str
    current_day: int
    current_minute: int
    tick_minutes: int
    status: str


class LocationRead(BaseModel):
    id: str
    name: str
    type: str
    description: str
    x: int
    y: int
    available_actions: list[str]
    event_tags: list[str]


class AgentRead(BaseModel):
    id: str
    name: str
    role: str
    major: str
    personality: str
    interests: list[str]
    long_term_goals: list[str]
    social_style: str
    current_location_id: str
    current_goal: str
    current_action: str
    mood: str
    energy: int
    stress: int
    adaptation_score: int


class EventRead(BaseModel):
    id: str
    day: int
    minute: int
    event_type: str
    location_id: str | None
    agent_ids: list[str]
    summary: str
    details: str
    llm_generated: bool


class RunStateResponse(BaseModel):
    run: RunRead
    locations: list[LocationRead]
    agents: list[AgentRead]
    recent_events: list[EventRead]
```

- [ ] **Step 6: Implement runs router**

Create `backend/app/api/runs.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.domain.schemas import CreateRunRequest, RunStateResponse
from app.models.tables import Agent, Event, Location, SimulationRun
from app.seed.seed_service import create_seed_run

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.post("", response_model=RunStateResponse, status_code=status.HTTP_201_CREATED)
def create_run(payload: CreateRunRequest, session: Session = Depends(get_session)) -> RunStateResponse:
    run = create_seed_run(session, payload.name)
    return _build_run_state(session, run.id)


@router.get("/{run_id}/state", response_model=RunStateResponse)
def get_run_state(run_id: str, session: Session = Depends(get_session)) -> RunStateResponse:
    return _build_run_state(session, run_id)


def _build_run_state(session: Session, run_id: str) -> RunStateResponse:
    run = session.get(SimulationRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    locations = session.exec(select(Location).where(Location.run_id == run_id)).all()
    agents = session.exec(select(Agent).where(Agent.run_id == run_id)).all()
    events = session.exec(select(Event).where(Event.run_id == run_id).order_by(Event.created_at.desc()).limit(50)).all()
    return RunStateResponse(run=run, locations=locations, agents=agents, recent_events=list(reversed(events)))
```

- [ ] **Step 7: Register runs router**

Modify `backend/app/main.py`:

```python
from app.api.runs import router as runs_router

app.include_router(runs_router)
```

Keep the existing lifespan and health endpoint.

- [ ] **Step 8: Run create run test**

Run:

```bash
cd backend && pytest tests/test_runs_api.py::test_create_run_initializes_seed_world -v
```

Expected: PASS.

- [ ] **Step 9: Run all backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all tests pass.

- [ ] **Step 10: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests
git commit -m "feat: seed default AI Nanda campus world"
```

---

### Task 3: Implement Run State, Events, Agents, and Basic API Coverage

**Files:**
- Create: `backend/app/api/agents.py`
- Create: `backend/app/api/events.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_agents_api.py`

- [ ] **Step 1: Write failing test for agent detail API**

Create `backend/tests/test_agents_api.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_get_agent_detail_includes_profile_state_events_and_memory():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Agent Detail Test"})
    agent_id = run_response.json()["agents"][0]["id"]

    response = client.get(f"/api/agents/{agent_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["id"] == agent_id
    assert "state" in body
    assert "recent_events" in body
    assert "important_memories" in body
    assert "relationships" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_agents_api.py -v
```

Expected: FAIL because agent API does not exist.

- [ ] **Step 3: Add Agent detail response schemas**

Modify `backend/app/domain/schemas.py` and add:

```python
class AgentProfileRead(BaseModel):
    id: str
    name: str
    role: str
    major: str
    personality: str
    interests: list[str]
    long_term_goals: list[str]
    social_style: str


class AgentStateRead(BaseModel):
    current_location_id: str
    current_goal: str
    current_action: str
    mood: str
    energy: int
    stress: int
    adaptation_score: int


class MemoryRead(BaseModel):
    id: str
    memory_type: str
    content: str
    importance: int
    tags: list[str]


class RelationshipRead(BaseModel):
    id: str
    agent_a_id: str
    agent_b_id: str
    affinity: int
    familiarity: int
    trust: int
    relationship_tags: list[str]


class AgentDetailResponse(BaseModel):
    profile: AgentProfileRead
    state: AgentStateRead
    recent_events: list[EventRead]
    important_memories: list[MemoryRead]
    relationships: list[RelationshipRead]
```

- [ ] **Step 4: Implement agents router**

Create `backend/app/api/agents.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, or_, select

from app.db.session import get_session
from app.domain.schemas import AgentDetailResponse, AgentProfileRead, AgentStateRead
from app.models.tables import Agent, Event, Memory, Relationship

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("/{agent_id}", response_model=AgentDetailResponse)
def get_agent(agent_id: str, session: Session = Depends(get_session)) -> AgentDetailResponse:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    recent_events = session.exec(
        select(Event)
        .where(Event.run_id == agent.run_id)
        .order_by(Event.created_at.desc())
        .limit(50)
    ).all()
    filtered_events = [event for event in recent_events if agent_id in event.agent_ids][:10]

    important_memories = session.exec(
        select(Memory)
        .where(Memory.agent_id == agent_id)
        .order_by(Memory.importance.desc())
        .limit(10)
    ).all()

    relationships = session.exec(
        select(Relationship).where(
            or_(Relationship.agent_a_id == agent_id, Relationship.agent_b_id == agent_id)
        )
    ).all()

    return AgentDetailResponse(
        profile=AgentProfileRead(**agent.model_dump()),
        state=AgentStateRead(**agent.model_dump()),
        recent_events=list(reversed(filtered_events)),
        important_memories=important_memories,
        relationships=relationships,
    )
```

- [ ] **Step 5: Implement events router**

Create `backend/app/api/events.py`:

```python
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.db.session import get_session
from app.domain.schemas import EventRead
from app.models.tables import Event

router = APIRouter(prefix="/api/runs", tags=["events"])


@router.get("/{run_id}/events", response_model=list[EventRead])
def list_events(
    run_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    agent_id: str | None = None,
    session: Session = Depends(get_session),
) -> list[EventRead]:
    events = session.exec(
        select(Event).where(Event.run_id == run_id).order_by(Event.created_at.desc()).limit(limit)
    ).all()
    if agent_id:
        events = [event for event in events if agent_id in event.agent_ids]
    return list(reversed(events))
```

- [ ] **Step 6: Register routers**

Modify `backend/app/main.py`:

```python
from app.api.agents import router as agents_router
from app.api.events import router as events_router

app.include_router(agents_router)
app.include_router(events_router)
```

- [ ] **Step 7: Run agent API test**

Run:

```bash
cd backend && pytest tests/test_agents_api.py -v
```

Expected: PASS.

- [ ] **Step 8: Run all backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all tests pass.

- [ ] **Step 9: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests
git commit -m "feat: expose run events and agent detail APIs"
```

---

### Task 4: Build Static Frontend Campus Observer

**Files:**
- Create: `frontend/src/types/simulation.ts`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/time.ts`
- Create: `frontend/src/components/SimulationHeader.tsx`
- Create: `frontend/src/components/AgentSidebar.tsx`
- Create: `frontend/src/components/CampusMap.tsx`
- Create: `frontend/src/components/EventFeed.tsx`
- Create: `frontend/src/components/AgentDetailPanel.tsx`
- Modify: `frontend/src/app/page.tsx`
- Modify: `frontend/src/app/globals.css`

- [ ] **Step 1: Create frontend simulation types**

Create `frontend/src/types/simulation.ts`:

```typescript
export type Run = {
  id: string;
  name: string;
  current_day: number;
  current_minute: number;
  tick_minutes: number;
  status: string;
};

export type Location = {
  id: string;
  name: string;
  type: string;
  description: string;
  x: number;
  y: number;
  available_actions: string[];
  event_tags: string[];
};

export type Agent = {
  id: string;
  name: string;
  role: string;
  major: string;
  personality: string;
  interests: string[];
  long_term_goals: string[];
  social_style: string;
  current_location_id: string;
  current_goal: string;
  current_action: string;
  mood: string;
  energy: number;
  stress: number;
  adaptation_score: number;
};

export type Event = {
  id: string;
  day: number;
  minute: number;
  event_type: string;
  location_id: string | null;
  agent_ids: string[];
  summary: string;
  details: string;
  llm_generated: boolean;
};

export type RunState = {
  run: Run;
  locations: Location[];
  agents: Agent[];
  recent_events: Event[];
};
```

- [ ] **Step 2: Create frontend time helper**

Create `frontend/src/lib/time.ts`:

```typescript
export function formatSimTime(day: number, minute: number): string {
  const hour = Math.floor(minute / 60);
  const mins = minute % 60;
  return `Day ${day} ${hour.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}`;
}
```

- [ ] **Step 3: Create API client**

Create `frontend/src/lib/api.ts`:

```typescript
import type { RunState } from "@/types/simulation";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function createRun(name = "AI 南大默认模拟"): Promise<RunState> {
  const response = await fetch(`${API_BASE}/api/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!response.ok) throw new Error(`Failed to create run: ${response.status}`);
  return response.json();
}

export async function getRunState(runId: string): Promise<RunState> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/state`);
  if (!response.ok) throw new Error(`Failed to load state: ${response.status}`);
  return response.json();
}
```

- [ ] **Step 4: Create SimulationHeader component**

Create `frontend/src/components/SimulationHeader.tsx`:

```tsx
import { formatSimTime } from "@/lib/time";
import type { Run } from "@/types/simulation";

type Props = {
  run: Run | null;
  onCreateRun: () => void;
};

export function SimulationHeader({ run, onCreateRun }: Props) {
  return (
    <header className="header">
      <div>
        <h1>AI 南大</h1>
        <p>多智能体校园社会模拟系统</p>
      </div>
      <div className="timeBox">
        {run ? formatSimTime(run.current_day, run.current_minute) : "尚未开始"}
        {run ? <span className="status">{run.status}</span> : null}
      </div>
      <button onClick={onCreateRun}>初始化模拟</button>
    </header>
  );
}
```

- [ ] **Step 5: Create AgentSidebar component**

Create `frontend/src/components/AgentSidebar.tsx`:

```tsx
import type { Agent } from "@/types/simulation";

type Props = {
  agents: Agent[];
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string) => void;
};

export function AgentSidebar({ agents, selectedAgentId, onSelectAgent }: Props) {
  return (
    <aside className="panel agentList">
      <h2>Agent</h2>
      {agents.map((agent) => (
        <button
          key={agent.id}
          className={agent.id === selectedAgentId ? "agentCard selected" : "agentCard"}
          onClick={() => onSelectAgent(agent.id)}
        >
          <strong>{agent.name}</strong>
          <span>{agent.major}</span>
          <small>{agent.current_action} · {agent.mood}</small>
        </button>
      ))}
    </aside>
  );
}
```

- [ ] **Step 6: Create CampusMap component**

Create `frontend/src/components/CampusMap.tsx`:

```tsx
import type { Agent, Location } from "@/types/simulation";

type Props = {
  locations: Location[];
  agents: Agent[];
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string) => void;
};

export function CampusMap({ locations, agents, selectedAgentId, onSelectAgent }: Props) {
  return (
    <section className="panel mapPanel">
      <h2>校园地图</h2>
      <div className="mapCanvas">
        {locations.map((location) => {
          const agentsHere = agents.filter((agent) => agent.current_location_id === location.id);
          return (
            <div
              key={location.id}
              className="locationNode"
              style={{ left: location.x, top: location.y }}
              title={location.description}
            >
              <span>{location.name}</span>
              <div className="agentDots">
                {agentsHere.map((agent) => (
                  <button
                    key={agent.id}
                    className={agent.id === selectedAgentId ? "agentDot selected" : "agentDot"}
                    onClick={() => onSelectAgent(agent.id)}
                    title={`${agent.name}：${agent.current_goal}`}
                  >
                    {agent.name.slice(0, 1)}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
```

- [ ] **Step 7: Create EventFeed component**

Create `frontend/src/components/EventFeed.tsx`:

```tsx
import { formatSimTime } from "@/lib/time";
import type { Event } from "@/types/simulation";

type Props = {
  events: Event[];
};

export function EventFeed({ events }: Props) {
  return (
    <aside className="panel eventFeed">
      <h2>事件流</h2>
      {events.map((event) => (
        <article key={event.id} className="eventItem">
          <span className={`tag tag-${event.event_type}`}>{event.event_type}</span>
          <time>{formatSimTime(event.day, event.minute)}</time>
          <p>{event.summary}</p>
          {event.details ? <small>{event.details}</small> : null}
        </article>
      ))}
    </aside>
  );
}
```

- [ ] **Step 8: Create AgentDetailPanel component**

Create `frontend/src/components/AgentDetailPanel.tsx`:

```tsx
import type { Agent } from "@/types/simulation";

type Props = {
  agent: Agent | null;
};

export function AgentDetailPanel({ agent }: Props) {
  if (!agent) {
    return <section className="panel detailPanel">选择一个 Agent 查看详情。</section>;
  }

  return (
    <section className="panel detailPanel">
      <h2>{agent.name}</h2>
      <p>{agent.role} · {agent.major}</p>
      <p>{agent.personality}</p>
      <dl>
        <dt>当前目标</dt>
        <dd>{agent.current_goal}</dd>
        <dt>当前行动</dt>
        <dd>{agent.current_action}</dd>
        <dt>状态</dt>
        <dd>心情 {agent.mood} · 精力 {agent.energy} · 压力 {agent.stress} · 适应度 {agent.adaptation_score}</dd>
      </dl>
      <h3>长期目标</h3>
      <ul>{agent.long_term_goals.map((goal) => <li key={goal}>{goal}</li>)}</ul>
    </section>
  );
}
```

- [ ] **Step 9: Implement main page state flow**

Modify `frontend/src/app/page.tsx`:

```tsx
"use client";

import { useState } from "react";

import { AgentDetailPanel } from "@/components/AgentDetailPanel";
import { AgentSidebar } from "@/components/AgentSidebar";
import { CampusMap } from "@/components/CampusMap";
import { EventFeed } from "@/components/EventFeed";
import { SimulationHeader } from "@/components/SimulationHeader";
import { createRun } from "@/lib/api";
import type { RunState } from "@/types/simulation";

export default function HomePage() {
  const [state, setState] = useState<RunState | null>(null);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleCreateRun() {
    setError(null);
    try {
      const nextState = await createRun();
      setState(nextState);
      setSelectedAgentId(nextState.agents[0]?.id ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "创建模拟失败");
    }
  }

  const selectedAgent = state?.agents.find((agent) => agent.id === selectedAgentId) ?? null;

  return (
    <main className="page">
      <SimulationHeader run={state?.run ?? null} onCreateRun={handleCreateRun} />
      {error ? <div className="error">{error}</div> : null}
      <div className="grid">
        <AgentSidebar agents={state?.agents ?? []} selectedAgentId={selectedAgentId} onSelectAgent={setSelectedAgentId} />
        <CampusMap locations={state?.locations ?? []} agents={state?.agents ?? []} selectedAgentId={selectedAgentId} onSelectAgent={setSelectedAgentId} />
        <EventFeed events={state?.recent_events ?? []} />
      </div>
      <AgentDetailPanel agent={selectedAgent} />
    </main>
  );
}
```

- [ ] **Step 10: Add basic styling**

Modify `frontend/src/app/globals.css` with the CSS needed by components:

```css
:root {
  color-scheme: light;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

body {
  margin: 0;
  background: #f6f1e8;
  color: #241f1a;
}

button {
  font: inherit;
  cursor: pointer;
}

.page {
  min-height: 100vh;
  padding: 24px;
}

.header,
.panel {
  border: 1px solid rgba(60, 42, 30, 0.16);
  border-radius: 20px;
  background: rgba(255, 252, 246, 0.92);
  box-shadow: 0 12px 30px rgba(50, 35, 24, 0.08);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 22px;
  margin-bottom: 18px;
}

.header h1 {
  margin: 0;
  font-size: 28px;
}

.header p {
  margin: 4px 0 0;
  color: #766754;
}

.timeBox {
  display: flex;
  gap: 10px;
  align-items: center;
  font-weight: 700;
}

.status,
.tag {
  border-radius: 999px;
  padding: 3px 9px;
  background: #ead8bc;
  font-size: 12px;
}

.grid {
  display: grid;
  grid-template-columns: 240px minmax(520px, 1fr) 340px;
  gap: 18px;
  align-items: stretch;
}

.panel {
  padding: 16px;
}

.agentList,
.eventFeed {
  max-height: 600px;
  overflow: auto;
}

.agentCard {
  display: grid;
  width: 100%;
  margin-bottom: 10px;
  padding: 12px;
  border: 1px solid transparent;
  border-radius: 14px;
  background: #f7ead6;
  text-align: left;
}

.agentCard.selected,
.agentDot.selected {
  border-color: #8f4f24;
  background: #f1c99f;
}

.mapCanvas {
  position: relative;
  height: 560px;
  border-radius: 18px;
  background: linear-gradient(135deg, #e7f0d3, #dbe8c4);
  overflow: hidden;
}

.locationNode {
  position: absolute;
  min-width: 112px;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(68, 91, 54, 0.24);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.86);
  padding: 8px;
  text-align: center;
}

.agentDots {
  display: flex;
  justify-content: center;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.agentDot {
  width: 26px;
  height: 26px;
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 50%;
  background: #fff2d6;
}

.eventItem {
  border-bottom: 1px solid rgba(60, 42, 30, 0.12);
  padding: 10px 0;
}

.eventItem time {
  display: block;
  margin: 6px 0;
  color: #766754;
  font-size: 12px;
}

.eventItem p {
  margin: 0;
}

.detailPanel {
  margin-top: 18px;
}

.error {
  margin-bottom: 12px;
  padding: 10px;
  border-radius: 12px;
  background: #ffe1df;
  color: #7e1f17;
}
```

- [ ] **Step 11: Run frontend build**

Run:

```bash
cd frontend && npm run build
```

Expected: build succeeds.

- [ ] **Step 12: Manually verify static observer**

Run backend and frontend in separate terminals:

```bash
cd backend && uvicorn app.main:app --reload
```

```bash
cd frontend && npm run dev
```

Open `http://localhost:3000`, click “初始化模拟”. Expected: map, agents, event feed, and detail panel render using backend seed data.

- [ ] **Step 13: Commit checkpoint if git is available**

Run:

```bash
git add frontend
git commit -m "feat: build static campus observer UI"
```

---

### Task 5: Implement Rule-Based Tick and Action Selection

**Files:**
- Create: `backend/app/domain/actions.py`
- Create: `backend/app/services/action_selector.py`
- Create: `backend/app/services/events.py`
- Create: `backend/app/services/simulation.py`
- Modify: `backend/app/api/runs.py`
- Modify: `backend/app/domain/schemas.py`
- Create: `backend/tests/test_action_selector.py`
- Modify: `backend/tests/test_simulation_tick.py`

- [ ] **Step 1: Write failing action selector test**

Create `backend/tests/test_action_selector.py`:

```python
from app.domain.actions import ProposedAction
from app.domain.constants import ActionType
from app.services.action_selector import choose_rule_action


def test_agent_moves_to_class_when_schedule_is_near():
    action = choose_rule_action(
        agent_id="agent_wang_yinuo",
        current_location_id="dorm",
        current_minute=8 * 60 + 10,
        nearby_agent_ids=[],
        pending_interventions=[],
        current_schedule={
            "type": "class",
            "location_id": "teaching_building",
            "title": "上午课程",
            "start_minute": 8 * 60 + 30,
        },
    )

    assert isinstance(action, ProposedAction)
    assert action.type == ActionType.MOVE
    assert action.target_location_id == "teaching_building"


def test_agent_eats_at_meal_time():
    action = choose_rule_action(
        agent_id="agent_wang_yinuo",
        current_location_id="teaching_building",
        current_minute=12 * 60,
        nearby_agent_ids=[],
        pending_interventions=[],
        current_schedule={
            "type": "meal",
            "location_id": "canteen",
            "title": "午饭",
            "start_minute": 12 * 60,
        },
    )

    assert action.type == ActionType.MOVE
    assert action.target_location_id == "canteen"
```

- [ ] **Step 2: Run action selector test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_action_selector.py -v
```

Expected: FAIL because action selector does not exist.

- [ ] **Step 3: Implement ProposedAction**

Create `backend/app/domain/actions.py`:

```python
from pydantic import BaseModel

from app.domain.constants import ActionType


class ProposedAction(BaseModel):
    type: ActionType
    agent_id: str
    reason: str
    target_location_id: str | None = None
    target_agent_id: str | None = None
    topic: str | None = None
```

- [ ] **Step 4: Implement rule action selector**

Create `backend/app/services/action_selector.py`:

```python
from typing import Any

from app.domain.actions import ProposedAction
from app.domain.constants import ActionType


def choose_rule_action(
    agent_id: str,
    current_location_id: str,
    current_minute: int,
    nearby_agent_ids: list[str],
    pending_interventions: list[str],
    current_schedule: dict[str, Any] | None,
) -> ProposedAction:
    if current_schedule:
        target_location_id = current_schedule["location_id"]
        schedule_type = current_schedule["type"]
        if current_location_id != target_location_id:
            return ProposedAction(
                type=ActionType.MOVE,
                agent_id=agent_id,
                target_location_id=target_location_id,
                reason=f"当前日程是{current_schedule['title']}，需要前往目标地点。",
            )
        if schedule_type == "class":
            return ProposedAction(type=ActionType.ATTEND_CLASS, agent_id=agent_id, reason="已到达教学地点，按计划上课。")
        if schedule_type == "meal":
            return ProposedAction(type=ActionType.EAT, agent_id=agent_id, reason="已到达食堂，按饭点吃饭。")
        if schedule_type == "club":
            return ProposedAction(type=ActionType.JOIN_ACTIVITY, agent_id=agent_id, reason="已到达社团招新点，参加活动。")
        if schedule_type == "rest":
            return ProposedAction(type=ActionType.REST, agent_id=agent_id, reason="晚上回到宿舍休息。")

    if pending_interventions:
        return ProposedAction(type=ActionType.IDLE, agent_id=agent_id, reason="正在考虑用户建议，暂时观察环境。")

    if nearby_agent_ids and 10 * 60 <= current_minute <= 21 * 60:
        return ProposedAction(
            type=ActionType.TALK,
            agent_id=agent_id,
            target_agent_id=nearby_agent_ids[0],
            topic="校园适应",
            reason="附近有认识同学的机会。",
        )

    return ProposedAction(type=ActionType.IDLE, agent_id=agent_id, reason="当前没有高优先级日程，暂时等待。")
```

- [ ] **Step 5: Run action selector tests**

Run:

```bash
cd backend && pytest tests/test_action_selector.py -v
```

Expected: PASS.

- [ ] **Step 6: Implement event creation helper**

Create `backend/app/services/events.py`:

```python
from sqlmodel import Session

from app.core.ids import new_id
from app.domain.constants import EventType
from app.models.tables import Event


def create_event(
    session: Session,
    *,
    run_id: str,
    day: int,
    minute: int,
    event_type: EventType | str,
    summary: str,
    details: str = "",
    location_id: str | None = None,
    agent_ids: list[str] | None = None,
    llm_generated: bool = False,
    state_delta: dict | None = None,
) -> Event:
    event = Event(
        id=new_id("event"),
        run_id=run_id,
        day=day,
        minute=minute,
        event_type=str(event_type),
        location_id=location_id,
        agent_ids=agent_ids or [],
        summary=summary,
        details=details,
        llm_generated=llm_generated,
        state_delta=state_delta or {},
    )
    session.add(event)
    return event
```

- [ ] **Step 7: Write failing tick API test**

Append to `backend/tests/test_runs_api.py`:

```python
def test_tick_advances_time_and_creates_events():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Tick Test"})
    run_id = run_response.json()["run"]["id"]

    response = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 1, "llm_mode": "offline"})

    assert response.status_code == 200
    body = response.json()
    assert body["run"]["current_minute"] == 480
    assert len(body["new_events"]) >= 1
    assert len(body["updated_agents"]) >= 1
```

- [ ] **Step 8: Add tick response schemas**

Modify `backend/app/domain/schemas.py` and add:

```python
class TickRequest(BaseModel):
    tick_count: int = 1
    llm_mode: str = "normal"


class TickResponse(BaseModel):
    run: RunRead
    new_events: list[EventRead]
    updated_agents: list[AgentRead]
```

- [ ] **Step 9: Implement minimal simulation service**

Create `backend/app/services/simulation.py`:

```python
from sqlmodel import Session, select

from app.core.time import is_after_simulation_end, next_tick
from app.domain.constants import ActionType, EventType, RunStatus
from app.models.tables import Agent, Event, Schedule, SimulationRun
from app.services.action_selector import choose_rule_action
from app.services.events import create_event


class SimulationService:
    def __init__(self, session: Session):
        self.session = session

    def tick(self, run_id: str, tick_count: int = 1, llm_mode: str = "normal") -> tuple[SimulationRun, list[Event], list[Agent]]:
        run = self.session.get(SimulationRun, run_id)
        if run is None:
            raise ValueError("Run not found")

        new_events: list[Event] = []
        updated_agents: list[Agent] = []
        for _ in range(tick_count):
            if run.status == RunStatus.COMPLETED.value:
                break
            run.current_day, run.current_minute = next_tick(run.current_day, run.current_minute, run.tick_minutes)
            if is_after_simulation_end(run.current_day, run.current_minute):
                run.status = RunStatus.COMPLETED.value

            events, agents = self._tick_agents(run)
            new_events.extend(events)
            updated_agents.extend(agents)

        self.session.add(run)
        self.session.commit()
        self.session.refresh(run)
        return run, new_events, updated_agents

    def _tick_agents(self, run: SimulationRun) -> tuple[list[Event], list[Agent]]:
        agents = self.session.exec(select(Agent).where(Agent.run_id == run.id)).all()
        new_events: list[Event] = []
        updated_agents: list[Agent] = []
        for agent in agents:
            schedule = self._current_schedule(run.id, agent.id, run.current_day, run.current_minute)
            action = choose_rule_action(
                agent_id=agent.id,
                current_location_id=agent.current_location_id,
                current_minute=run.current_minute,
                nearby_agent_ids=[],
                pending_interventions=[],
                current_schedule=schedule,
            )
            event = self._apply_rule_action(run, agent, action)
            new_events.append(event)
            updated_agents.append(agent)
        return new_events, updated_agents

    def _current_schedule(self, run_id: str, agent_id: str, day: int, minute: int) -> dict | None:
        schedule = self.session.exec(
            select(Schedule)
            .where(Schedule.run_id == run_id, Schedule.agent_id == agent_id, Schedule.day == day)
            .where(Schedule.start_minute <= minute, Schedule.end_minute >= minute)
            .order_by(Schedule.priority.desc())
        ).first()
        return schedule.model_dump() if schedule else None

    def _apply_rule_action(self, run: SimulationRun, agent: Agent, action) -> Event:
        if action.type == ActionType.MOVE and action.target_location_id:
            old_location_id = agent.current_location_id
            agent.current_location_id = action.target_location_id
            agent.current_action = ActionType.MOVE.value
            summary = f"{agent.name}从{old_location_id}前往{action.target_location_id}。"
            event_type = EventType.MOVE
        elif action.type == ActionType.ATTEND_CLASS:
            agent.current_action = ActionType.ATTEND_CLASS.value
            summary = f"{agent.name}按计划在教学楼上课。"
            event_type = EventType.CLASS
        elif action.type == ActionType.EAT:
            agent.current_action = ActionType.EAT.value
            agent.energy = min(100, agent.energy + 10)
            summary = f"{agent.name}在食堂吃饭，精力稍微恢复。"
            event_type = EventType.MEAL
        elif action.type == ActionType.JOIN_ACTIVITY:
            agent.current_action = ActionType.JOIN_ACTIVITY.value
            summary = f"{agent.name}来到社团招新点，观察不同社团的摊位。"
            event_type = EventType.CLUB
        else:
            agent.current_action = action.type.value
            summary = f"{agent.name}暂时停留，原因是：{action.reason}"
            event_type = EventType.SYSTEM

        self.session.add(agent)
        return create_event(
            self.session,
            run_id=run.id,
            day=run.current_day,
            minute=run.current_minute,
            event_type=event_type,
            summary=summary,
            details=action.reason,
            location_id=agent.current_location_id,
            agent_ids=[agent.id],
            state_delta={"action": action.model_dump(mode="json")},
        )
```

- [ ] **Step 10: Add tick route**

Modify `backend/app/api/runs.py` and add:

```python
from app.domain.schemas import TickRequest, TickResponse
from app.services.simulation import SimulationService


@router.post("/{run_id}/tick", response_model=TickResponse)
def tick_run(run_id: str, payload: TickRequest, session: Session = Depends(get_session)) -> TickResponse:
    service = SimulationService(session)
    try:
        run, new_events, updated_agents = service.tick(run_id, payload.tick_count, payload.llm_mode)
    except ValueError:
        raise HTTPException(status_code=404, detail="Run not found")
    return TickResponse(run=run, new_events=new_events, updated_agents=updated_agents)
```

- [ ] **Step 11: Run tick API test**

Run:

```bash
cd backend && pytest tests/test_runs_api.py::test_tick_advances_time_and_creates_events -v
```

Expected: PASS.

- [ ] **Step 12: Run all backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all backend tests pass.

- [ ] **Step 13: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests
git commit -m "feat: add rule-based simulation tick"
```

---

### Task 6: Add Game Master Validation

**Files:**
- Create: `backend/app/services/game_master.py`
- Modify: `backend/app/services/simulation.py`
- Create: `backend/tests/test_game_master.py`

- [ ] **Step 1: Write failing Game Master tests**

Create `backend/tests/test_game_master.py`:

```python
from app.domain.actions import ProposedAction
from app.domain.constants import ActionType
from app.services.game_master import GameMaster


def test_game_master_rejects_invalid_location():
    gm = GameMaster(paths={"dorm": {"canteen"}}, locations={"dorm", "canteen"})
    action = ProposedAction(
        type=ActionType.MOVE,
        agent_id="agent_1",
        target_location_id="moon",
        reason="test",
    )

    result = gm.validate(current_location_id="dorm", action=action)

    assert result.allowed is False
    assert "不存在" in result.reason


def test_game_master_rejects_unconnected_move():
    gm = GameMaster(paths={"dorm": {"canteen"}}, locations={"dorm", "canteen", "library"})
    action = ProposedAction(
        type=ActionType.MOVE,
        agent_id="agent_1",
        target_location_id="library",
        reason="test",
    )

    result = gm.validate(current_location_id="dorm", action=action)

    assert result.allowed is False
    assert "不连通" in result.reason


def test_game_master_allows_connected_move():
    gm = GameMaster(paths={"dorm": {"canteen"}}, locations={"dorm", "canteen"})
    action = ProposedAction(
        type=ActionType.MOVE,
        agent_id="agent_1",
        target_location_id="canteen",
        reason="test",
    )

    result = gm.validate(current_location_id="dorm", action=action)

    assert result.allowed is True
```

- [ ] **Step 2: Run Game Master tests to verify they fail**

Run:

```bash
cd backend && pytest tests/test_game_master.py -v
```

Expected: FAIL because Game Master does not exist.

- [ ] **Step 3: Implement Game Master**

Create `backend/app/services/game_master.py`:

```python
from pydantic import BaseModel

from app.domain.actions import ProposedAction
from app.domain.constants import ActionType


class ValidationResult(BaseModel):
    allowed: bool
    reason: str


class GameMaster:
    def __init__(self, paths: dict[str, set[str]], locations: set[str]):
        self.paths = paths
        self.locations = locations

    def validate(self, current_location_id: str, action: ProposedAction) -> ValidationResult:
        if action.type == ActionType.MOVE:
            return self._validate_move(current_location_id, action)
        if action.type == ActionType.TALK and not action.target_agent_id:
            return ValidationResult(allowed=False, reason="对话行动缺少目标 Agent。")
        return ValidationResult(allowed=True, reason="行动合法。")

    def _validate_move(self, current_location_id: str, action: ProposedAction) -> ValidationResult:
        if not action.target_location_id:
            return ValidationResult(allowed=False, reason="移动行动缺少目标地点。")
        if action.target_location_id not in self.locations:
            return ValidationResult(allowed=False, reason="目标地点不存在。")
        if action.target_location_id == current_location_id:
            return ValidationResult(allowed=True, reason="Agent 已在目标地点。")
        connected = self.paths.get(current_location_id, set())
        if action.target_location_id not in connected:
            return ValidationResult(allowed=False, reason="当前地点和目标地点不连通。")
        return ValidationResult(allowed=True, reason="移动行动合法。")
```

- [ ] **Step 4: Run Game Master tests**

Run:

```bash
cd backend && pytest tests/test_game_master.py -v
```

Expected: PASS.

- [ ] **Step 5: Integrate Game Master into SimulationService**

Modify `backend/app/services/simulation.py`:

- Load `Location` and `Path` rows for the current run.
- Build `GameMaster(paths, locations)`.
- Before applying action, call `validate()`.
- If rejected, create a system event and set `agent.current_action = "idle"`.

Implementation pattern:

```python
from app.models.tables import Location, Path
from app.services.game_master import GameMaster


def _build_game_master(self, run_id: str) -> GameMaster:
    locations = self.session.exec(select(Location).where(Location.run_id == run_id)).all()
    paths = self.session.exec(select(Path).where(Path.run_id == run_id)).all()
    location_ids = {location.id for location in locations}
    path_map: dict[str, set[str]] = {}
    for path in paths:
        path_map.setdefault(path.from_location_id, set()).add(path.to_location_id)
    return GameMaster(paths=path_map, locations=location_ids)
```

Then in `_tick_agents`, build one Game Master per tick and pass it into `_apply_rule_action`.

- [ ] **Step 6: Add regression test for invalid action fallback**

Add a focused unit test or service-level test proving rejected moves create a system event and do not change location.

Run:

```bash
cd backend && pytest tests/test_game_master.py tests/test_runs_api.py -v
```

Expected: PASS.

- [ ] **Step 7: Run all backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all backend tests pass.

- [ ] **Step 8: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests
git commit -m "feat: validate actions through game master"
```

---

### Task 7: Implement Memory Retrieval and Relationship Updates

**Files:**
- Create: `backend/app/services/memory.py`
- Create: `backend/app/services/relationships.py`
- Modify: `backend/app/services/simulation.py`
- Create: `backend/tests/test_memory.py`

- [ ] **Step 1: Write failing Memory Retriever tests**

Create `backend/tests/test_memory.py`:

```python
from app.services.memory import score_memory


def test_memory_retriever_prioritizes_important_memory():
    high = score_memory(
        content="王一诺迟到了并向林见川求助。",
        importance=5,
        created_day=1,
        created_minute=480,
        current_day=1,
        current_minute=540,
        query_terms=["林见川", "求助"],
    )
    low = score_memory(
        content="王一诺路过食堂。",
        importance=1,
        created_day=1,
        created_minute=480,
        current_day=1,
        current_minute=540,
        query_terms=["林见川", "求助"],
    )

    assert high > low


def test_memory_retriever_prioritizes_relevance():
    relevant = score_memory("周岚在图书馆捡到校园卡。", 2, 1, 600, 1, 660, ["图书馆", "校园卡"])
    irrelevant = score_memory("陈念在食堂排队。", 2, 1, 600, 1, 660, ["图书馆", "校园卡"])

    assert relevant > irrelevant
```

- [ ] **Step 2: Run memory tests to verify they fail**

Run:

```bash
cd backend && pytest tests/test_memory.py -v
```

Expected: FAIL because memory service does not exist.

- [ ] **Step 3: Implement memory scoring and retrieval**

Create `backend/app/services/memory.py`:

```python
from sqlmodel import Session, select

from app.models.tables import Memory


def score_memory(
    content: str,
    importance: int,
    created_day: int,
    created_minute: int,
    current_day: int,
    current_minute: int,
    query_terms: list[str],
) -> float:
    age_minutes = max(0, (current_day - created_day) * 24 * 60 + (current_minute - created_minute))
    recency_score = max(0.0, 5.0 - age_minutes / 180.0)
    importance_score = float(importance)
    relevance_score = sum(2.0 for term in query_terms if term and term in content)
    return recency_score + importance_score + relevance_score


class MemoryService:
    def __init__(self, session: Session):
        self.session = session

    def retrieve(
        self,
        *,
        run_id: str,
        agent_id: str,
        current_day: int,
        current_minute: int,
        query_terms: list[str],
        limit: int = 8,
    ) -> list[Memory]:
        memories = self.session.exec(
            select(Memory).where(Memory.run_id == run_id, Memory.agent_id == agent_id)
        ).all()
        ranked = sorted(
            memories,
            key=lambda memory: score_memory(
                memory.content,
                memory.importance,
                memory.created_day,
                memory.created_minute,
                current_day,
                current_minute,
                query_terms,
            ),
            reverse=True,
        )
        return ranked[:limit]
```

- [ ] **Step 4: Run memory tests**

Run:

```bash
cd backend && pytest tests/test_memory.py -v
```

Expected: PASS.

- [ ] **Step 5: Implement relationship service**

Create `backend/app/services/relationships.py`:

```python
from sqlmodel import Session, or_, select

from app.core.ids import new_id
from app.models.tables import Relationship


class RelationshipService:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create(self, run_id: str, agent_a_id: str, agent_b_id: str) -> Relationship:
        relationship = self.session.exec(
            select(Relationship).where(
                Relationship.run_id == run_id,
                or_(
                    (Relationship.agent_a_id == agent_a_id) & (Relationship.agent_b_id == agent_b_id),
                    (Relationship.agent_a_id == agent_b_id) & (Relationship.agent_b_id == agent_a_id),
                ),
            )
        ).first()
        if relationship:
            return relationship
        relationship = Relationship(id=new_id("rel"), run_id=run_id, agent_a_id=agent_a_id, agent_b_id=agent_b_id)
        self.session.add(relationship)
        return relationship

    def apply_delta(
        self,
        relationship: Relationship,
        *,
        affinity: int = 0,
        familiarity: int = 0,
        trust: int = 0,
        tag: str | None = None,
        event_id: str | None = None,
    ) -> Relationship:
        relationship.affinity += affinity
        relationship.familiarity += familiarity
        relationship.trust += trust
        if tag and tag not in relationship.relationship_tags:
            relationship.relationship_tags = [*relationship.relationship_tags, tag]
        relationship.last_interaction_event_id = event_id or relationship.last_interaction_event_id
        self.session.add(relationship)
        return relationship
```

- [ ] **Step 6: Write memories during simulation events**

Modify `backend/app/services/simulation.py` so each non-system event creates a `Memory` row for involved agents:

```python
from app.core.ids import new_id
from app.models.tables import Memory


def _write_event_memory(self, run: SimulationRun, event: Event, importance: int = 2) -> None:
    for agent_id in event.agent_ids:
        self.session.add(
            Memory(
                id=new_id("mem"),
                run_id=run.id,
                agent_id=agent_id,
                memory_type="short_term",
                content=event.summary,
                importance=importance,
                tags=[event.event_type],
                source="event",
                related_event_id=event.id,
                created_day=run.current_day,
                created_minute=run.current_minute,
            )
        )
```

Call `_write_event_memory` after event creation.

- [ ] **Step 7: Add integration test that tick writes memory**

Append to `backend/tests/test_runs_api.py` or create a service-level test:

```python
def test_tick_writes_agent_memory():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Memory Tick Test"})
    run_id = run_response.json()["run"]["id"]
    agent_id = run_response.json()["agents"][0]["id"]

    client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 1, "llm_mode": "offline"})
    detail_response = client.get(f"/api/agents/{agent_id}")

    assert detail_response.status_code == 200
    assert len(detail_response.json()["important_memories"]) >= 1
```

- [ ] **Step 8: Run memory-related tests**

Run:

```bash
cd backend && pytest tests/test_memory.py tests/test_runs_api.py tests/test_agents_api.py -v
```

Expected: PASS.

- [ ] **Step 9: Run all backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all backend tests pass.

- [ ] **Step 10: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests
git commit -m "feat: add memory retrieval and event memories"
```

---

### Task 8: Implement User Interventions

**Files:**
- Modify: `backend/app/domain/schemas.py`
- Modify: `backend/app/api/agents.py`
- Modify: `backend/app/services/action_selector.py`
- Modify: `backend/app/services/simulation.py`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/AgentDetailPanel.tsx`
- Create: `backend/tests/test_interventions.py`

- [ ] **Step 1: Write failing backend intervention test**

Create `backend/tests/test_interventions.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_submit_intervention_creates_pending_intervention_and_memory():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Intervention Test"})
    agent_id = run_response.json()["agents"][0]["id"]

    response = client.post(
        f"/api/agents/{agent_id}/interventions",
        json={"content": "你可以去社团招新点看看。"},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"

    detail = client.get(f"/api/agents/{agent_id}").json()
    assert any("社团招新" in memory["content"] for memory in detail["important_memories"])
```

- [ ] **Step 2: Run intervention test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_interventions.py -v
```

Expected: FAIL because intervention route does not exist.

- [ ] **Step 3: Add intervention schemas**

Modify `backend/app/domain/schemas.py`:

```python
class CreateInterventionRequest(BaseModel):
    content: str


class InterventionResponse(BaseModel):
    intervention_id: str
    status: str
```

- [ ] **Step 4: Implement basic safety filter**

Create `backend/app/services/safety.py`:

```python
BLOCKED_TERMS = ["攻击", "骚扰", "歧视", "违法", "人肉", "真实个人信息"]


def is_safe_user_intervention(content: str) -> bool:
    normalized = content.strip().lower()
    if not normalized:
        return False
    return not any(term in normalized for term in BLOCKED_TERMS)
```

- [ ] **Step 5: Add intervention route**

Modify `backend/app/api/agents.py` and add:

```python
from fastapi import status
from app.core.ids import new_id
from app.core.time import format_sim_time
from app.domain.constants import EventType
from app.domain.schemas import CreateInterventionRequest, InterventionResponse
from app.models.tables import Memory, SimulationRun, UserIntervention
from app.services.events import create_event
from app.services.safety import is_safe_user_intervention


@router.post("/{agent_id}/interventions", response_model=InterventionResponse, status_code=status.HTTP_201_CREATED)
def create_intervention(
    agent_id: str,
    payload: CreateInterventionRequest,
    session: Session = Depends(get_session),
) -> InterventionResponse:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    run = session.get(SimulationRun, agent.run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if not is_safe_user_intervention(payload.content):
        event = create_event(
            session,
            run_id=run.id,
            day=run.current_day,
            minute=run.current_minute,
            event_type=EventType.SYSTEM,
            summary=f"系统拒绝了一条不适合进入模拟的用户干预。",
            details="用户干预未写入 Agent 记忆。",
            agent_ids=[agent.id],
        )
        session.commit()
        return InterventionResponse(intervention_id=event.id, status="rejected")

    intervention = UserIntervention(
        id=new_id("int"),
        run_id=run.id,
        agent_id=agent.id,
        content=payload.content,
        created_day=run.current_day,
        created_minute=run.current_minute,
    )
    session.add(intervention)
    session.add(
        Memory(
            id=new_id("mem"),
            run_id=run.id,
            agent_id=agent.id,
            memory_type="intervention",
            content=f"用户在{format_sim_time(run.current_day, run.current_minute)}建议：{payload.content}",
            importance=5,
            tags=["intervention"],
            source="user",
            created_day=run.current_day,
            created_minute=run.current_minute,
        )
    )
    create_event(
        session,
        run_id=run.id,
        day=run.current_day,
        minute=run.current_minute,
        event_type=EventType.INTERVENTION,
        summary=f"用户给{agent.name}留下建议：{payload.content}",
        agent_ids=[agent.id],
    )
    session.commit()
    return InterventionResponse(intervention_id=intervention.id, status=intervention.status)
```

- [ ] **Step 6: Run intervention test**

Run:

```bash
cd backend && pytest tests/test_interventions.py -v
```

Expected: PASS.

- [ ] **Step 7: Make action selector consider interventions**

Modify `choose_rule_action` so if a pending intervention mentions `社团` and the Agent is not at `club_fair`, return a move action to `club_fair`:

```python
if any("社团" in intervention for intervention in pending_interventions) and current_location_id != "club_fair":
    return ProposedAction(
        type=ActionType.MOVE,
        agent_id=agent_id,
        target_location_id="club_fair",
        reason="用户建议 Agent 去社团招新点看看，且该建议符合校园适应目标。",
    )
```

- [ ] **Step 8: Pass pending interventions into simulation**

Modify `SimulationService._tick_agents` to query pending `UserIntervention` rows for each Agent and pass their content into `choose_rule_action`.

- [ ] **Step 9: Add test proving intervention affects next action**

Add to `backend/tests/test_interventions.py`:

```python
def test_intervention_can_affect_next_tick_action():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Intervention Action Test"})
    run_id = run_response.json()["run"]["id"]
    agent_id = run_response.json()["agents"][0]["id"]

    client.post(f"/api/agents/{agent_id}/interventions", json={"content": "你可以去社团招新点看看。"})
    tick = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 1, "llm_mode": "offline"}).json()

    updated = next(agent for agent in tick["updated_agents"] if agent["id"] == agent_id)
    assert updated["current_location_id"] == "club_fair"
```

- [ ] **Step 10: Add frontend intervention submit API**

Modify `frontend/src/lib/api.ts`:

```typescript
export async function submitIntervention(agentId: string, content: string): Promise<{ intervention_id: string; status: string }> {
  const response = await fetch(`${API_BASE}/api/agents/${agentId}/interventions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!response.ok) throw new Error(`Failed to submit intervention: ${response.status}`);
  return response.json();
}
```

- [ ] **Step 11: Add intervention input to detail panel**

Modify `frontend/src/components/AgentDetailPanel.tsx` to accept `onSubmitIntervention` and render a textarea/button. Keep it controlled in parent page.

Minimum component API:

```tsx
type Props = {
  agent: Agent | null;
  interventionText: string;
  onInterventionTextChange: (value: string) => void;
  onSubmitIntervention: () => void;
};
```

- [ ] **Step 12: Wire intervention in page**

Modify `frontend/src/app/page.tsx` to call `submitIntervention(selectedAgentId, interventionText)`, clear input, then refresh run state.

- [ ] **Step 13: Run backend and frontend verification**

Run:

```bash
cd backend && pytest tests/test_interventions.py -v
```

Expected: PASS.

Run:

```bash
cd frontend && npm run build
```

Expected: build succeeds.

- [ ] **Step 14: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests frontend/src
git commit -m "feat: add user interventions"
```

---

### Task 9: Implement LLM Provider Abstraction and Contract Tests

**Files:**
- Create: `backend/app/llm/schemas.py`
- Create: `backend/app/llm/base.py`
- Create: `backend/app/llm/fake_provider.py`
- Create: `backend/app/llm/anthropic_provider.py`
- Create: `backend/app/llm/prompts.py`
- Modify: `backend/app/services/llm_service.py`
- Create: `backend/tests/test_llm_contracts.py`

- [ ] **Step 1: Write failing LLM contract tests**

Create `backend/tests/test_llm_contracts.py`:

```python
from pydantic import ValidationError

from app.llm.schemas import DialogueResult, ReflectionResult


def test_dialogue_result_schema_accepts_valid_output():
    result = DialogueResult.model_validate(
        {
            "dialogue": [
                {"speaker": "王一诺", "text": "请问教学楼怎么走？"},
                {"speaker": "林见川", "text": "我也去那里，一起吧。"},
            ],
            "relationship_delta": {"affinity": 1, "familiarity": 1, "trust": 1},
            "memory_writes": ["王一诺记住林见川帮他找路。"],
            "event_summary": "王一诺向林见川问路，两人因此认识。",
        }
    )

    assert result.event_summary.startswith("王一诺")


def test_reflection_result_schema_rejects_missing_reflection():
    try:
        ReflectionResult.model_validate({"goal_updates": []})
    except ValidationError:
        return
    raise AssertionError("Expected validation error")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd backend && pytest tests/test_llm_contracts.py -v
```

Expected: FAIL because LLM schemas do not exist.

- [ ] **Step 3: Implement LLM schemas**

Create `backend/app/llm/schemas.py`:

```python
from pydantic import BaseModel, Field


class DialogueLine(BaseModel):
    speaker: str
    text: str


class RelationshipDelta(BaseModel):
    affinity: int = 0
    familiarity: int = 0
    trust: int = 0


class DialogueResult(BaseModel):
    dialogue: list[DialogueLine]
    relationship_delta: RelationshipDelta
    memory_writes: list[str]
    event_summary: str


class ReflectionResult(BaseModel):
    reflection: str
    goal_updates: list[str] = Field(default_factory=list)
    important_memories: list[str] = Field(default_factory=list)
    mood_delta: str = "neutral"
    adaptation_delta: int = 0


class InterventionDecision(BaseModel):
    decision: str
    reason: str
    new_immediate_goal: str | None = None


class ComplexEventDecision(BaseModel):
    chosen_action: str
    target_location: str | None = None
    reason: str


class PolishedEvent(BaseModel):
    summary: str
    details: str = ""
```

- [ ] **Step 4: Run LLM schema tests**

Run:

```bash
cd backend && pytest tests/test_llm_contracts.py -v
```

Expected: PASS.

- [ ] **Step 5: Define provider interface**

Create `backend/app/llm/base.py`:

```python
from abc import ABC, abstractmethod
from typing import Any

from app.llm.schemas import DialogueResult, InterventionDecision, ReflectionResult


class LLMProvider(ABC):
    @abstractmethod
    def generate_dialogue(self, context: dict[str, Any]) -> DialogueResult:
        raise NotImplementedError

    @abstractmethod
    def reflect_day(self, context: dict[str, Any]) -> ReflectionResult:
        raise NotImplementedError

    @abstractmethod
    def decide_intervention(self, context: dict[str, Any]) -> InterventionDecision:
        raise NotImplementedError
```

- [ ] **Step 6: Implement fake provider**

Create `backend/app/llm/fake_provider.py`:

```python
from typing import Any

from app.llm.base import LLMProvider
from app.llm.schemas import DialogueResult, InterventionDecision, ReflectionResult


class FakeLLMProvider(LLMProvider):
    def generate_dialogue(self, context: dict[str, Any]) -> DialogueResult:
        speaker = context.get("speaker", "王一诺")
        target = context.get("target", "林见川")
        return DialogueResult.model_validate(
            {
                "dialogue": [
                    {"speaker": speaker, "text": "我对这里还不太熟，可以问你一个问题吗？"},
                    {"speaker": target, "text": "当然可以，我们可以一起过去。"},
                ],
                "relationship_delta": {"affinity": 1, "familiarity": 1, "trust": 1},
                "memory_writes": [f"{speaker}和{target}进行了一次友好的校园交流。"],
                "event_summary": f"{speaker}和{target}在校园里交流了一会儿。",
            }
        )

    def reflect_day(self, context: dict[str, Any]) -> ReflectionResult:
        agent_name = context.get("agent_name", "这名 Agent")
        return ReflectionResult(
            reflection=f"{agent_name}回顾了今天的课程、吃饭和社交经历，决定明天继续适应校园生活。",
            goal_updates=["明天继续按计划上课", "留意可以认识同学的机会"],
            important_memories=[f"{agent_name}完成了一天的校园生活。"],
            mood_delta="slightly_positive",
            adaptation_delta=1,
        )

    def decide_intervention(self, context: dict[str, Any]) -> InterventionDecision:
        content = context.get("content", "")
        if "社团" in content:
            return InterventionDecision(decision="accepted", reason="建议与加入社团的长期目标一致。", new_immediate_goal="去社团招新点看看")
        return InterventionDecision(decision="considered", reason="Agent 会把这条建议作为参考。")
```

- [ ] **Step 7: Implement prompts**

Create `backend/app/llm/prompts.py`:

```python
SYSTEM_PROMPT = """你是 AI 南大校园社会模拟系统中的结构化生成模块。
只生成虚构校园 Agent 的对话、反思和决策解释。
不要生成真实个人信息、攻击、骚扰、歧视、违法或不适合校园展示的内容。
输出必须符合调用方提供的 JSON schema。
"""


def dialogue_prompt(context: dict) -> str:
    return f"""请为两个校园 Agent 生成一次简短、有校园语境的对话。
上下文：{context}
要求：对话自然、短、具体；输出结构化 JSON。
"""


def reflection_prompt(context: dict) -> str:
    return f"""请为一个校园 Agent 生成一天结束后的反思。
上下文：{context}
要求：反思要引用当天事件，给出明天目标更新；输出结构化 JSON。
"""


def intervention_prompt(context: dict) -> str:
    return f"""请判断用户建议是否应影响 Agent 下一步计划。
上下文：{context}
要求：只在符合 Agent 目标、状态和安全边界时接受；输出结构化 JSON。
"""
```

- [ ] **Step 8: Implement Anthropic provider**

Create `backend/app/llm/anthropic_provider.py`:

```python
from typing import Any, TypeVar

import anthropic
from pydantic import BaseModel

from app.core.config import Settings
from app.llm.base import LLMProvider
from app.llm.prompts import SYSTEM_PROMPT, dialogue_prompt, intervention_prompt, reflection_prompt
from app.llm.schemas import DialogueResult, InterventionDecision, ReflectionResult

T = TypeVar("T", bound=BaseModel)


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def generate_dialogue(self, context: dict[str, Any]) -> DialogueResult:
        return self._parse(DialogueResult, dialogue_prompt(context))

    def reflect_day(self, context: dict[str, Any]) -> ReflectionResult:
        return self._parse(ReflectionResult, reflection_prompt(context))

    def decide_intervention(self, context: dict[str, Any]) -> InterventionDecision:
        return self._parse(InterventionDecision, intervention_prompt(context))

    def _parse(self, model_type: type[T], prompt: str) -> T:
        response = self.client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=4000,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": model_type.model_json_schema(),
                }
            },
        )
        text = next(block.text for block in response.content if block.type == "text")
        return model_type.model_validate_json(text)
```

- [ ] **Step 9: Implement provider factory service**

Create or modify `backend/app/services/llm_service.py`:

```python
from app.core.config import get_settings
from app.llm.anthropic_provider import AnthropicLLMProvider
from app.llm.base import LLMProvider
from app.llm.fake_provider import FakeLLMProvider


def get_llm_provider(llm_mode: str = "normal") -> LLMProvider:
    settings = get_settings()
    if llm_mode == "offline" or settings.llm_provider == "fake":
        return FakeLLMProvider()
    if settings.llm_provider == "anthropic":
        return AnthropicLLMProvider(settings)
    return FakeLLMProvider()
```

- [ ] **Step 10: Add fallback test**

Add test ensuring `get_llm_provider("offline")` returns fake and can produce valid reflection.

Run:

```bash
cd backend && pytest tests/test_llm_contracts.py -v
```

Expected: PASS.

- [ ] **Step 11: Run all backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all default tests pass without real LLM calls.

- [ ] **Step 12: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests
git commit -m "feat: add LLM provider abstraction"
```

---

### Task 10: Integrate Dialogue, Reflection, and Intervention Decisions

**Files:**
- Modify: `backend/app/services/simulation.py`
- Modify: `backend/app/services/llm_service.py`
- Modify: `backend/app/services/relationships.py`
- Modify: `backend/app/models/tables.py` if needed
- Modify: `backend/tests/test_interventions.py`
- Modify: `backend/tests/test_runs_api.py`

- [ ] **Step 1: Write failing test for reflection event near night**

Add to `backend/tests/test_runs_api.py`:

```python
def test_tick_near_night_generates_reflection_event_offline():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Reflection Test"})
    run_id = run_response.json()["run"]["id"]

    # 30 ticks from 07:30 reaches 22:30.
    response = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 30, "llm_mode": "offline"})

    assert response.status_code == 200
    summaries = [event["summary"] for event in response.json()["new_events"]]
    assert any("反思" in summary or "回顾" in summary for summary in summaries)
```

- [ ] **Step 2: Run reflection test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_runs_api.py::test_tick_near_night_generates_reflection_event_offline -v
```

Expected: FAIL because reflection not integrated.

- [ ] **Step 3: Add reflection trigger to SimulationService**

In `SimulationService._tick_agents`, if `run.current_minute >= 22 * 60 + 30`, call provider `reflect_day()` for main agents and create reflection events.

Implementation pattern:

```python
from app.domain.constants import EventType
from app.services.llm_service import get_llm_provider


def _maybe_reflect(self, run: SimulationRun, agent: Agent, llm_mode: str) -> Event | None:
    reflection_key = f"day-{run.current_day}"
    if run.current_minute < 22 * 60 + 30 or agent.last_reflection_at == reflection_key:
        return None
    provider = get_llm_provider(llm_mode)
    result = provider.reflect_day({"agent_name": agent.name, "current_goal": agent.current_goal})
    agent.last_reflection_at = reflection_key
    agent.adaptation_score += result.adaptation_delta
    event = create_event(
        self.session,
        run_id=run.id,
        day=run.current_day,
        minute=run.current_minute,
        event_type=EventType.REFLECTION,
        summary=f"{agent.name}完成今日反思：{result.reflection}",
        details="\n".join(result.goal_updates),
        location_id=agent.current_location_id,
        agent_ids=[agent.id],
        llm_generated=llm_mode != "offline",
    )
    self._write_event_memory(run, event, importance=4)
    return event
```

Pass `llm_mode` through `_tick_agents`.

- [ ] **Step 4: Run reflection test**

Run:

```bash
cd backend && pytest tests/test_runs_api.py::test_tick_near_night_generates_reflection_event_offline -v
```

Expected: PASS.

- [ ] **Step 5: Integrate intervention decisions**

When pending interventions exist and `llm_mode != "offline"`, call `decide_intervention`; when `offline`, use fake provider. Update intervention status to accepted/considered/ignored and set `agent.current_goal` if accepted.

- [ ] **Step 6: Add test for intervention status update after tick**

Add to `backend/tests/test_interventions.py`:

```python
def test_tick_marks_intervention_considered():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Intervention Status Test"})
    run_id = run_response.json()["run"]["id"]
    agent_id = run_response.json()["agents"][0]["id"]

    intervention = client.post(f"/api/agents/{agent_id}/interventions", json={"content": "你可以去社团招新点看看。"}).json()
    client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 1, "llm_mode": "offline"})

    # Verify indirectly through events until a debug endpoint exposes intervention rows.
    events = client.get(f"/api/runs/{run_id}/events?limit=50").json()
    assert any("建议" in event["summary"] or "社团" in event["summary"] for event in events)
```

- [ ] **Step 7: Add dialogue trigger for talk actions**

If `choose_rule_action` returns `TALK`, use provider `generate_dialogue()` to create a social event, write memories, and update relationship through `RelationshipService`.

Do not let LLM choose arbitrary state changes; only use event summary, memory writes, and relationship delta.

- [ ] **Step 8: Add deterministic offline dialogue test**

Create a setup where two agents are at the same location during non-class time; run a tick with `offline`; assert at least one social/talk event appears.

- [ ] **Step 9: Run integration tests**

Run:

```bash
cd backend && pytest tests/test_runs_api.py tests/test_interventions.py tests/test_llm_contracts.py -v
```

Expected: PASS.

- [ ] **Step 10: Run all backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all default tests pass.

- [ ] **Step 11: Optional real Claude smoke test**

Only run if `ANTHROPIC_API_KEY` is set and you intentionally want to spend API credits.

Add a test marked `@pytest.mark.llm`, then run:

```bash
cd backend && RUN_LLM_TESTS=1 pytest -m llm -v
```

Expected: provider returns schema-valid dialogue/reflection. If it fails because no API key is configured, do not count as product failure; document skipped real LLM verification.

- [ ] **Step 12: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests
git commit -m "feat: integrate LLM dialogue reflection and intervention decisions"
```

---

### Task 11: Add Debug APIs and LLM Call Logging

**Files:**
- Create: `backend/app/api/debug.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/services/llm_service.py`
- Modify: `backend/app/services/simulation.py`
- Create: `backend/tests/test_debug_api.py`

- [ ] **Step 1: Write failing debug API test**

Create `backend/tests/test_debug_api.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_debug_memories_returns_agent_memories():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Debug Test"})
    agent_id = run_response.json()["agents"][0]["id"]

    response = client.get(f"/api/debug/agents/{agent_id}/memories")

    assert response.status_code == 200
    assert isinstance(response.json()["memories"], list)
```

- [ ] **Step 2: Run debug test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_debug_api.py -v
```

Expected: FAIL because debug API does not exist.

- [ ] **Step 3: Implement debug router**

Create `backend/app/api/debug.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.tables import Agent, LLMCall, Memory

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/agents/{agent_id}/memories")
def debug_agent_memories(agent_id: str, session: Session = Depends(get_session)) -> dict:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    memories = session.exec(select(Memory).where(Memory.agent_id == agent_id)).all()
    return {"agent_id": agent_id, "memories": [memory.model_dump(mode="json") for memory in memories]}


@router.get("/runs/{run_id}/llm-calls")
def debug_llm_calls(run_id: str, session: Session = Depends(get_session)) -> dict:
    calls = session.exec(select(LLMCall).where(LLMCall.run_id == run_id)).all()
    return {"run_id": run_id, "llm_calls": [call.model_dump(mode="json") for call in calls]}
```

- [ ] **Step 4: Register debug router**

Modify `backend/app/main.py`:

```python
from app.api.debug import router as debug_router

app.include_router(debug_router)
```

- [ ] **Step 5: Run debug test**

Run:

```bash
cd backend && pytest tests/test_debug_api.py -v
```

Expected: PASS.

- [ ] **Step 6: Add LLM call logging helper**

In `backend/app/services/llm_service.py`, add a helper to write `LLMCall` rows for each provider call. If this is too intrusive, add logging in `SimulationService` around calls to provider methods.

Record:

- `run_id`
- `agent_id`
- `function_name`
- `prompt_version`
- `input_summary`
- `output_json`
- `status`
- `latency_ms`
- `error_message`

- [ ] **Step 7: Add fallback logging**

If provider call raises or validation fails, log `status="fallback"` and create a system event.

- [ ] **Step 8: Add test for offline llm call logging if implemented**

Run tick to reflection, then call `/api/debug/runs/{run_id}/llm-calls`; assert it returns list. If fake provider logging is not used, assert endpoint returns empty list and does not fail.

- [ ] **Step 9: Run backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all backend tests pass.

- [ ] **Step 10: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests
git commit -m "feat: add debug APIs and LLM call logging"
```

---

### Task 12: Add Frontend Tick Controls and Live State Refresh

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/SimulationHeader.tsx`
- Modify: `frontend/src/app/page.tsx`
- Create: `frontend/tests/simulation.spec.ts`

- [ ] **Step 1: Add frontend tick API**

Modify `frontend/src/lib/api.ts`:

```typescript
export async function tickRun(runId: string, tickCount = 1, llmMode = "offline"): Promise<{ run: RunState["run"]; new_events: RunState["recent_events"]; updated_agents: RunState["agents"] }> {
  const response = await fetch(`${API_BASE}/api/runs/${runId}/tick`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tick_count: tickCount, llm_mode: llmMode }),
  });
  if (!response.ok) throw new Error(`Failed to tick run: ${response.status}`);
  return response.json();
}
```

- [ ] **Step 2: Extend SimulationHeader props and UI**

Modify `frontend/src/components/SimulationHeader.tsx` to accept:

```tsx
type Props = {
  run: Run | null;
  isRunning: boolean;
  onCreateRun: () => void;
  onStep: () => void;
  onRun: () => void;
  onPause: () => void;
  onFastForwardHour: () => void;
};
```

Render buttons:

```tsx
<button onClick={onCreateRun}>初始化 / 重置</button>
<button onClick={onStep} disabled={!run}>单步</button>
<button onClick={onRun} disabled={!run || isRunning}>运行</button>
<button onClick={onPause} disabled={!isRunning}>暂停</button>
<button onClick={onFastForwardHour} disabled={!run}>快进 1 小时</button>
```

- [ ] **Step 3: Implement page tick state update**

Modify `frontend/src/app/page.tsx`:

- Import `getRunState`, `tickRun`, `submitIntervention`.
- Track `isRunning`.
- `handleStep`: call `tickRun(run.id, 1, "offline")`, then refresh `getRunState(run.id)`.
- `handleRun`: set interval to call step every 1500ms.
- `handlePause`: clear interval.
- `handleFastForwardHour`: call `tickRun(run.id, 2, "offline")`.

Use `useRef<number | null>` for interval ID.

- [ ] **Step 4: Add selected agent refresh safety**

After each refresh, if selected agent no longer exists, select first agent.

- [ ] **Step 5: Add Playwright smoke test**

Create `frontend/tests/simulation.spec.ts`:

```typescript
import { test, expect } from "@playwright/test";

test("user can see simulation shell", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("AI 南大")).toBeVisible();
  await expect(page.getByRole("button", { name: /初始化/ })).toBeVisible();
});
```

- [ ] **Step 6: Run frontend build**

Run:

```bash
cd frontend && npm run build
```

Expected: build succeeds.

- [ ] **Step 7: Manual browser verification**

Run backend and frontend:

```bash
cd backend && uvicorn app.main:app --reload
```

```bash
cd frontend && npm run dev
```

Open `http://localhost:3000` and verify:

- Initialize run.
- Click single step.
- Agent positions/actions update.
- Event feed grows.
- Click run; events continue updating.
- Click pause; updates stop.
- Submit intervention; a new intervention event appears.

- [ ] **Step 8: Commit checkpoint if git is available**

Run:

```bash
git add frontend
git commit -m "feat: add simulation controls to frontend"
```

---

### Task 13: Add Campus-Specific Event Templates

**Files:**
- Create: `backend/app/seed/event_templates.py`
- Modify: `backend/app/services/simulation.py`
- Modify: `backend/app/services/action_selector.py`
- Create: `backend/tests/test_campus_events.py`

- [ ] **Step 1: Write failing campus event test**

Create `backend/tests/test_campus_events.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_one_day_generates_campus_specific_events():
    client = TestClient(app)
    run_response = client.post("/api/runs", json={"name": "Campus Event Test"})
    run_id = run_response.json()["run"]["id"]

    response = client.post(f"/api/runs/{run_id}/tick", json={"tick_count": 30, "llm_mode": "offline"})

    summaries = "\n".join(event["summary"] for event in response.json()["new_events"])
    assert any(keyword in summaries for keyword in ["社团", "食堂", "教学楼", "图书馆", "校园卡"])
```

- [ ] **Step 2: Run campus event test**

Run:

```bash
cd backend && pytest tests/test_campus_events.py -v
```

Expected: may fail if current events are too generic. Use failure to guide template work.

- [ ] **Step 3: Create event templates**

Create `backend/app/seed/event_templates.py`:

```python
MEAL_EVENTS = [
    "{agent}在食堂排队时听到旁边同学讨论社团招新。",
    "{agent}在食堂快速吃完午饭，开始考虑下午的安排。",
]

CLASS_EVENTS = [
    "{agent}在教学楼赶上了上午课程，暂时松了一口气。",
    "{agent}在教学楼附近确认教室位置，避免了迟到。",
]

CLUB_EVENTS = [
    "{agent}在社团招新点停下脚步，被一个摊位的介绍吸引。",
    "{agent}在社团招新点和学长学姐聊了几句，对大学生活多了一点期待。",
]

LOST_ITEM_EVENTS = [
    "{agent}在图书馆附近看到一张遗落的校园卡，开始考虑是否送去失物招领处。",
]
```

- [ ] **Step 4: Use templates in SimulationService**

Modify `_apply_rule_action` to use templates based on event type. Keep deterministic selection first: use agent ID + day + minute hash modulo template count.

- [ ] **Step 5: Add occasional lost item event**

During afternoon ticks at library or canteen, occasionally create `lost_item` event for one agent. Keep deterministic condition such as:

```python
if run.current_day == 2 and run.current_minute == 15 * 60 and agent.current_location_id in {"library", "canteen"}:
    ...
```

Avoid randomness in tests.

- [ ] **Step 6: Run campus event test**

Run:

```bash
cd backend && pytest tests/test_campus_events.py -v
```

Expected: PASS.

- [ ] **Step 7: Run a 7-day offline simulation quality check**

Run:

```bash
cd backend && python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
state = client.post('/api/runs', json={'name': '7 Day Offline Smoke'}).json()
run_id = state['run']['id']
events = []
for _ in range(7 * 48):
    tick = client.post(f'/api/runs/{run_id}/tick', json={'tick_count': 1, 'llm_mode': 'offline'}).json()
    events.extend(tick['new_events'])
print('events', len(events))
print('types', sorted(set(e['event_type'] for e in events)))
print('last_run', tick['run'])
PY
```

Expected: no crash, at least 20 events, multiple event types, run reaches completed or near end depending loop count.

- [ ] **Step 8: Run backend tests**

Run:

```bash
cd backend && pytest -v
```

Expected: all backend tests pass.

- [ ] **Step 9: Commit checkpoint if git is available**

Run:

```bash
git add backend/app backend/tests
git commit -m "feat: add campus-specific event templates"
```

---

### Task 14: Add Documentation, Manual Test Checklist, and Demo Instructions

**Files:**
- Create or modify: `README.md`
- Create: `docs/testing/manual-test-checklist.md`
- Create: `frontend/src/app/about/page.tsx`

- [ ] **Step 1: Write README**

Create `README.md`:

```markdown
# AI 南大｜多智能体校园社会模拟系统

AI 南大是一个面向中国高校场景的轻量级多智能体校园社会模拟 MVP。它把校园抽象为地点、时间、课表、关系、事件和记忆，让 5-8 个虚构 AI 新生在一周内上课、吃饭、社交、参加社团、处理随机事件并进行每日反思。

## Architecture

- `frontend/`: Next.js TypeScript campus observer UI
- `backend/`: FastAPI simulation API, SQLite store, Agent Runtime, Game Master, Memory, LLM Service

```text
Next.js Frontend -> FastAPI Simulation API -> Simulation Engine -> Game Master -> SQLite
                                               -> LLM Provider -> Claude API / Fake Provider
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

Frontend runs at `http://localhost:3000`.

## LLM Modes

- `offline`: fake provider and templates, safe for tests and demos without API key
- `cheap`: reduced real LLM calls
- `normal`: real LLM calls for dialogue, reflection, intervention decisions

To use Claude:

```bash
ANTHROPIC_API_KEY=your_key
LLM_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-opus-4-6
```

## Tests

```bash
cd backend && pytest -v
cd frontend && npm run build
```

Real LLM tests are optional and cost API credits:

```bash
cd backend && RUN_LLM_TESTS=1 pytest -m llm -v
```
```

- [ ] **Step 2: Create manual test checklist**

Create `docs/testing/manual-test-checklist.md`:

```markdown
# AI 南大 Manual Test Checklist

## Startup

- [ ] Backend starts with `uvicorn app.main:app --reload`.
- [ ] Frontend starts with `npm run dev`.
- [ ] Browser opens `http://localhost:3000`.

## Static Observer

- [ ] User can initialize a simulation.
- [ ] Map shows at least 6 campus locations.
- [ ] Agent sidebar shows at least 5 Agents.
- [ ] Event feed shows an initialization event.
- [ ] Clicking Agent shows profile and state.

## Rule Simulation

- [ ] Single step advances time by 30 minutes.
- [ ] Agents move to teaching building before class.
- [ ] Agents move to canteen at meal time.
- [ ] Event feed grows after ticks.

## Memory and Intervention

- [ ] User can submit an intervention.
- [ ] Intervention appears as event.
- [ ] Intervention appears in Agent memory.
- [ ] Next tick can alter Agent action if suggestion is relevant.

## LLM / Fallback

- [ ] Offline mode completes without API key.
- [ ] If Claude API is configured, at least one dialogue/reflection returns schema-valid content.
- [ ] If LLM fails, fallback event appears and simulation continues.

## 7-Day Smoke

- [ ] 7-day offline simulation does not crash.
- [ ] At least 20 meaningful events generated.
- [ ] At least 3 event types appear.
- [ ] At least one reflection event appears.
- [ ] At least one user intervention has visible impact.

## Portfolio Demo

- [ ] Project value can be explained in 5 minutes.
- [ ] Viewer can identify how this differs from a normal chatbot.
- [ ] Viewer can remember at least one Agent story.
```

- [ ] **Step 3: Create about page**

Create `frontend/src/app/about/page.tsx`:

```tsx
export default function AboutPage() {
  return (
    <main className="page">
      <section className="panel">
        <h1>关于 AI 南大</h1>
        <p>
          AI 南大参考 Generative Agents、AI Town 和 Aivilization，把校园生活建模为地点、时间、课表、事件、关系和记忆。
        </p>
        <p>
          第一版聚焦 5-8 个虚构 AI 新生的一周生活，用规则推进日常行为，用 LLM 处理对话、反思和用户干预。
        </p>
      </section>
    </main>
  );
}
```

- [ ] **Step 4: Run final backend verification**

Run:

```bash
cd backend && pytest -v
```

Expected: all backend tests pass.

- [ ] **Step 5: Run final frontend verification**

Run:

```bash
cd frontend && npm run build
```

Expected: frontend production build succeeds.

- [ ] **Step 6: Run manual smoke commands**

Run the 7-day offline smoke command from Task 13 and record output in your implementation notes.

Expected: no crash, event count >= 20, multiple event types.

- [ ] **Step 7: Commit checkpoint if git is available**

Run:

```bash
git add README.md docs frontend backend
git commit -m "docs: add demo and manual test documentation"
```

---

## Final Verification Checklist Before Claiming MVP Complete

Do not claim completion until all checked with fresh output:

- [ ] `cd backend && pytest -v` passes.
- [ ] `cd frontend && npm run build` passes.
- [ ] Manual browser smoke test passes: initialize, step, run, pause, select Agent, submit intervention.
- [ ] 7-day offline smoke produces at least 20 events and no crash.
- [ ] If real LLM is configured, one `generate_dialogue`, one `reflect_day`, and one `decide_intervention` call return schema-valid outputs.
- [ ] If real LLM is not configured, README clearly states how to configure it and offline mode still works.
- [ ] `docs/testing/manual-test-checklist.md` is filled out for the demo run.

## Execution Handoff

Recommended execution mode: **Subagent-Driven Development**. Implement one task at a time, run the specified tests, then review the diff before moving to the next task. If working inline, use the same task boundaries and do not batch across milestone boundaries without verification.
