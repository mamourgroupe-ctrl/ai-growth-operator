from fastapi import FastAPI

from .errors import register_error_handlers
from .routers.auth import router as auth_router

app = FastAPI(
    title="AI Growth Operator API",
    version="0.1.0",
    description="Phase 1 foundation: auth, organizations, RBAC, RLS, and job queue.",
)

register_error_handlers(app)
app.include_router(auth_router)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz() -> dict[str, str]:
    return {"status": "ok"}
