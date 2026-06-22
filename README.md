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

To use DeepSeek:

```bash
DEEPSEEK_API_KEY=your_key
LLM_PROVIDER=deepseek
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

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
cd frontend && npm run test:e2e
```

The Playwright E2E config starts both the local FastAPI backend and Next.js dev
server automatically.

Real LLM tests are optional and cost API credits:

```bash
cd backend && RUN_LLM_TESTS=1 pytest -m llm -v
```

For DeepSeek real-call smoke tests, also set `DEEPSEEK_API_KEY` and
`LLM_PROVIDER=deepseek`.
