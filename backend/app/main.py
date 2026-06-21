from fastapi import FastAPI

app = FastAPI(title="AI 南大 Simulation API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
