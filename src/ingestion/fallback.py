"""
FallbackManager - Error handling and fallback mechanisms

Provides graceful degradation when errors occur during data ingestion,
including missing field handling, type mismatch recovery, and general
function fallback execution.
"""

import logging
from typing import Any, Callable, Dict, Optional


class FallbackManager:
    """
    Handles errors and provides fallback mechanisms to ensure the system
    never crashes during data ingestion.

    Requirements:
    - Req 8.1: Missing field → default value + warning log
    - Req 8.2: Type mismatch → attempt conversion or default
    - Req 8.3: Conversion failure → default value + error log
    - Req 11.5: Log error type, context, and recovery action taken
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize fallback manager with optional logger.

        Args:
            logger: Logger instance for error tracking. If None, a default
                    logger named 'FallbackManager' is created.
        """
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger("FallbackManager")

    def with_fallback(
        self,
        primary_func: Callable,
        fallback_func: Optional[Callable] = None,
        default_value: Any = None,
        error_handler: Optional[Callable] = None,
    ) -> Any:
        """
        Execute a function with fallback on error.

        Tries primary_func first. On failure, tries fallback_func if provided.
        If both fail (or no fallback), returns default_value. Calls
        error_handler with the exception if provided.

        Args:
            primary_func: Primary callable to execute.
            fallback_func: Optional fallback callable executed on primary failure.
            default_value: Value returned if both primary and fallback fail.
            error_handler: Optional callable(exception) invoked on primary error.

        Returns:
            Result from primary_func, fallback_func, or default_value.

        Requirements: 8.1, 8.2, 8.3
        """
        try:
            return primary_func()
        except Exception as primary_exc:
            self.logger.error(
                "Primary function failed. "
                "error_type=%s, error=%s, recovery_action=%s",
                type(primary_exc).__name__,
                primary_exc,
                "executing fallback" if fallback_func is not None else "returning default value",
            )

            if error_handler is not None:
                try:
                    error_handler(primary_exc)
                except Exception as handler_exc:
                    self.logger.error(
                        "Error handler raised an exception. "
                        "error_type=%s, error=%s",
                        type(handler_exc).__name__,
                        handler_exc,
                    )

            if fallback_func is not None:
                try:
                    return fallback_func()
                except Exception as fallback_exc:
                    self.logger.error(
                        "Fallback function also failed. "
                        "error_type=%s, error=%s, recovery_action=returning default value",
                        type(fallback_exc).__name__,
                        fallback_exc,
                    )

            return default_value

    def handle_missing_field(
        self,
        data: Dict[str, Any],
        field: str,
        default: Any = None,
    ) -> Any:
        """
        Return the field value from data, or default if the field is absent.

        Logs a warning when the field is missing so callers can track
        data quality issues.

        Args:
            data: Dictionary to look up.
            field: Key to retrieve.
            default: Value returned when the field is not present.

        Returns:
            data[field] if present, otherwise default.

        Requirements: 8.1
        """
        if field not in data:
            self.logger.warning(
                "Missing field detected. "
                "field=%s, recovery_action=using default value %r",
                field,
                default,
            )
            return default
        return data[field]

    def handle_type_mismatch(
        self,
        value: Any,
        expected_type: type,
        default: Any = None,
    ) -> Any:
        """
        Attempt to coerce value to expected_type; return default on failure.

        Logs an error with type details when conversion fails so the issue
        can be investigated.

        Args:
            value: The value to convert.
            expected_type: The target Python type (e.g. int, float, str).
            default: Value returned when conversion fails.

        Returns:
            Converted value on success, default on failure.

        Requirements: 8.2, 8.3
        """
        if isinstance(value, expected_type) and not (
            expected_type is int and isinstance(value, bool)
        ):
            return value

        try:
            converted = expected_type(value)
            return converted
        except (ValueError, TypeError) as exc:
            self.logger.error(
                "Type conversion failed. "
                "value=%r, value_type=%s, expected_type=%s, error=%s, "
                "recovery_action=using default value %r",
                value,
                type(value).__name__,
                expected_type.__name__,
                exc,
                default,
            )
            return default
