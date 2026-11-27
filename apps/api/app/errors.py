from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

PROBLEM_PREFIX = "https://api.ai-growth-operator.local/problems"


class Problem(Exception):
    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str | None = None,
        slug: str = "error",
        headers: dict[str, str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.slug = slug
        self.headers = headers
        self.extra = extra or {}
        super().__init__(title)


def _problem_response(
    request: Request,
    status_code: int,
    title: str,
    detail: str | None,
    slug: str,
    headers: dict[str, str] | None = None,
    extra: dict[str, Any] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": f"{PROBLEM_PREFIX}/{slug}",
        "title": title,
        "status": status_code,
        "instance": request.url.path,
    }
    if detail:
        body["detail"] = detail
    if extra:
        body.update(extra)
    return JSONResponse(
        status_code=status_code,
        content=body,
        media_type="application/problem+json",
        headers=headers,
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(Problem)
    async def problem_handler(request: Request, exc: Problem) -> JSONResponse:
        return _problem_response(
            request,
            exc.status_code,
            exc.title,
            exc.detail,
            exc.slug,
            exc.headers,
            exc.extra,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem_response(
            request,
            422,
            "Validation error",
            "The request payload is invalid.",
            "validation-error",
            extra={"errors": jsonable_encoder(exc.errors())},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _problem_response(
            request,
            exc.status_code,
            str(exc.detail),
            None,
            "http-error",
            dict(exc.headers) if exc.headers else None,
        )
