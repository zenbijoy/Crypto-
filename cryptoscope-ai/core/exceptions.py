"""
CryptoScope AI - Exceptions & Domain Errors
"""
class CryptoScopeException(Exception):
    """Base exception for CryptoScope AI domain errors"""
    def __init__(self, message: str, code: str = "CRYPTOSCOPE_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code

class DataUnavailableException(CryptoScopeException):
    def __init__(self, message: str = "Market feed or quantitative data is currently unavailable"):
        super().__init__(message, code="DATA_UNAVAILABLE")

class CircuitBreakerTriggeredException(CryptoScopeException):
    def __init__(self, reason: str):
        super().__init__(f"Circuit breaker active: {reason}", code="CIRCUIT_BREAKER_TRIGGERED")

class ModelDriftException(CryptoScopeException):
    def __init__(self, message: str):
        super().__init__(message, code="MODEL_DRIFT_DETECTED")

class InsufficientMarginException(CryptoScopeException):
    def __init__(self, message: str = "Insufficient simulated balance for order execution"):
        super().__init__(message, code="INSUFFICIENT_MARGIN")
