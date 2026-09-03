"""
CryptoScope AI - Exceptions & Domain Errors
"""
from typing import Optional

class CryptoScopeException(Exception):
    """Base exception for CryptoScope AI domain errors"""
    def __init__(self, message: str, code: str = "CRYPTOSCOPE_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

class DataUnavailableException(CryptoScopeException):
    def __init__(self, message: str = "Market feed or quantitative data is currently unavailable"):
        super().__init__(message, code="DATA_UNAVAILABLE")

class DataUnavailableError(DataUnavailableException):
    pass

class ProviderError(CryptoScopeException):
    def __init__(self, message: str = "Exchange provider error encountered"):
        super().__init__(message, code="PROVIDER_ERROR")

class RateLimitError(CryptoScopeException):
    def __init__(self, message: str = "Provider rate limit reached", retry_after_seconds: Optional[int] = None):
        super().__init__(message, code="RATE_LIMIT_EXCEEDED")
        self.retry_after_seconds = retry_after_seconds

class ProviderUnavailableError(CryptoScopeException):
    def __init__(self, message: str = "Provider is currently unavailable or unreachable"):
        super().__init__(message, code="PROVIDER_UNAVAILABLE")

class ModelUnavailableException(CryptoScopeException):
    def __init__(self, message: str = "Trained ML model artifact is unavailable"):
        super().__init__(message, code="MODEL_UNAVAILABLE")

class DataQualityException(CryptoScopeException):
    def __init__(self, message: str = "Data quality invariant violation"):
        super().__init__(message, code="DATA_QUALITY_VIOLATION")

class CircuitBreakerTriggeredException(CryptoScopeException):
    def __init__(self, reason: str):
        super().__init__(f"Circuit breaker active: {reason}", code="CIRCUIT_BREAKER_TRIGGERED")

class ModelDriftException(CryptoScopeException):
    def __init__(self, message: str):
        super().__init__(message, code="MODEL_DRIFT_DETECTED")

class InsufficientMarginException(CryptoScopeException):
    def __init__(self, message: str = "Insufficient simulated balance for order execution"):
        super().__init__(message, code="INSUFFICIENT_MARGIN")

