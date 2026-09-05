"""
CryptoScope AI - Canonical API Error Envelope & Exceptions (Phase 24)
Standardizes all API error responses to:
{
  "error": {
    "code": "...",
    "message": "...",
    "request_id": "...",
    "details": {}
  }
}
"""
import uuid
from typing import Any, Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class ApiErrorCode:
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    DATA_STALE = "DATA_STALE"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    UNAUTHORIZED = "UNAUTHORIZED"
    RATE_LIMITED = "RATE_LIMITED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class CryptoScopeApiException(HTTPException):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
        self.details = details or {}


def format_error_response(
    code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": request_id or str(uuid.uuid4()),
                "details": details or {}
            }
        }
    )


async def api_exception_handler(request: Request, exc: CryptoScopeApiException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return format_error_response(
        code=exc.code,
        message=exc.message,
        request_id=request_id,
        details=exc.details,
        status_code=exc.status_code
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    code = ApiErrorCode.INTERNAL_ERROR
    if exc.status_code == 401:
        code = ApiErrorCode.UNAUTHORIZED
    elif exc.status_code == 404:
        code = ApiErrorCode.DATA_UNAVAILABLE
    elif exc.status_code == 429:
        code = ApiErrorCode.RATE_LIMITED
    elif exc.status_code == 503:
        code = ApiErrorCode.PROVIDER_UNAVAILABLE

    return format_error_response(
        code=code,
        message=str(exc.detail),
        request_id=request_id,
        details={},
        status_code=exc.status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return format_error_response(
        code=ApiErrorCode.VALIDATION_ERROR,
        message="Request payload validation failed",
        request_id=request_id,
        details={"errors": exc.errors()},
        status_code=422
    )


def register_error_handlers(app: Any):
    """Registers canonical error handlers conforming to Phase 24 specification."""
    from fastapi import FastAPI
    app.add_exception_handler(CryptoScopeApiException, api_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
