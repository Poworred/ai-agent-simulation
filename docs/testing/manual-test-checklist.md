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

## Latest Automated Smoke Output

Run on 2026-06-22 with offline LLM mode:

```text
events 1967
types ['class', 'club', 'lost_item', 'meal', 'move', 'reflection', 'social', 'system']
last_run {'id': 'run_ecec006d4777', 'name': '7 Day Offline Smoke', 'current_day': 7, 'current_minute': 1410, 'tick_minutes': 30, 'status': 'completed'}
```

Playwright smoke currently covers opening the shell, initializing a run, stepping once,
selecting 王一诺, and submitting a user intervention.
