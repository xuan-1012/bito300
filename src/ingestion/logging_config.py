"""
Logging configuration with sensitive data filtering.

Provides a logging.Filter subclass that redacts API keys, secrets, and
authentication tokens from log records before they are emitted.

Requirements: 12.5
"""

import logging
import re
from typing import List, Pattern

# Patterns that identify sensitive values in log messages.
# Each pattern captures the sensitive portion in group 1 so it can be
# replaced with [REDACTED].
_SENSITIVE_PATTERNS: List[Pattern] = [
    # Explicit key=value style: api_key=abc123, apiKey=abc123
    re.compile(
        r'((?:api[_-]?key|api[_-]?secret|auth[_-]?token|access[_-]?token'
        r'|secret[_-]?key|password|passwd|bearer)\s*[=:]\s*)([^\s,\'"&]+)',
        re.IGNORECASE,
    ),
    # JSON-style: "api_key": "value" or "apiKey": "value"
    re.compile(
        r'("(?:api[_-]?key|api[_-]?secret|auth[_-]?token|access[_-]?token'
        r'|secret[_-]?key|password|passwd|bearer)"\s*:\s*)"([^"]*)"',
        re.IGNORECASE,
    ),
    # HTTP header style: X-BITOPRO-APIKEY: value
    re.compile(
        r'(X-BITOPRO-(?:APIKEY|APISECRET)\s*[=:]\s*)([^\s,\'"&]+)',
        re.IGNORECASE,
    ),
    # Bearer token in Authorization header
    re.compile(
        r'(Authorization\s*[=:]\s*Bearer\s+)([^\s,\'"&]+)',
        re.IGNORECASE,
    ),
]

_REDACTED = "[REDACTED]"


def sanitize_message(message: str) -> str:
    """
    Replace sensitive values in *message* with ``[REDACTED]``.

    Args:
        message: The log message string to sanitize.

    Returns:
        The sanitized message with sensitive values replaced.
    """
    for pattern in _SENSITIVE_PATTERNS:
        # Replace only the captured sensitive value (group 2), keep the key
        message = pattern.sub(lambda m: m.group(1) + _REDACTED, message)
    return message


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter that redacts sensitive data from log records.

    Attach this filter to any logger or handler to ensure that API keys,
    secrets, and tokens are never written to log output.

    Example::

        import logging
        from src.ingestion.logging_config import SensitiveDataFilter

        logger = logging.getLogger("my_module")
        logger.addFilter(SensitiveDataFilter())

    Requirements: 12.5
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Sanitize the log record's message in-place.

        Always returns True so the record is still emitted (just sanitized).
        """
        # Sanitize the formatted message
        record.msg = sanitize_message(str(record.msg))

        # Also sanitize any string arguments that will be interpolated
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: sanitize_message(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    sanitize_message(str(a)) if isinstance(a, str) else a
                    for a in record.args
                )

        return True


def configure_sensitive_logging(logger_name: str = "") -> logging.Logger:
    """
    Attach a :class:`SensitiveDataFilter` to the named logger.

    Args:
        logger_name: Logger name (empty string targets the root logger).

    Returns:
        The logger with the filter attached.
    """
    target_logger = logging.getLogger(logger_name)
    target_logger.addFilter(SensitiveDataFilter())
    return target_logger
