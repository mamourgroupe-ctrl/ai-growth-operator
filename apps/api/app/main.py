from fastapi import FastAPI

from .errors import register_error_handlers

app = FastAPI(
    title="AI Growth Operator API",
    version="0.1.0",
    description="Phase 1 foundation: auth, organizations, RBAC, RLS, and job queue.",
)

register_error_handlers(app)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz() -> dict[str, str]:
    return {"status": "ok"}
