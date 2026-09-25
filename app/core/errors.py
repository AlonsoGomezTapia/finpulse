from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException, EntityNotFoundException


def problem_details_response(
    status_code: int,
    title: str,
    detail: str,
    instance: str,
    type_: str = "about:blank",
    invalid_params: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    """Construye un payload JSON conforme a la especificación RFC 7807."""
    payload: dict[str, Any] = {
        "type": type_,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
    }
    if invalid_params:
        payload["invalid_params"] = invalid_params

    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json",
    )


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Atrapa excepciones de dominio y las traduce a códigos HTTP correspondientes."""
    if isinstance(exc, EntityNotFoundException):
        return problem_details_response(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Resource Not Found",
            detail=str(exc),
            instance=request.url.path,
            type_="https://errors.finpulse.dev/not-found",
        )
    if isinstance(exc, AppException):
        return problem_details_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Business Rule Violation",
            detail=str(exc),
            instance=request.url.path,
            type_="https://errors.finpulse.dev/bad-request",
        )
    # Errores 500 no filtran detalles internos en producción
    return problem_details_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        title="Internal Server Error",
        detail="Ocurrió un error inesperado al procesar la solicitud.",
        instance=request.url.path,
        type_="https://errors.finpulse.dev/internal-error",
    )
