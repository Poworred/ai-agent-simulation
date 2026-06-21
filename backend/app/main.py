from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.agents import router as agents_router
from app.api.debug import router as debug_router
from app.api.events import router as events_router
from app.api.runs import router as runs_router
from app.db.session import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    yield


app = FastAPI(title="AI 南大 Simulation API", lifespan=lifespan)
app.include_router(runs_router)
app.include_router(agents_router)
app.include_router(events_router)
app.include_router(debug_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
