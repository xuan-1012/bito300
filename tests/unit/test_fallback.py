"""
Unit tests for FallbackManager.

Covers:
- Initialization (default and custom logger)
- handle_missing_field: present field, missing field, default values
- handle_type_mismatch: successful conversion, failed conversion, already correct type
- with_fallback: primary success, primary failure + fallback success,
                 both fail → default, custom error_handler invocation
"""

import logging
import pytest

from src.ingestion.fallback import FallbackManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_manager(capture_logs=False):
    """Return a FallbackManager and optionally a list that captures log records."""
    if not capture_logs:
        return FallbackManager(), None

    records = []

    class _Handler(logging.Handler):
        def emit(self, record):
            records.append(record)

    logger = logging.getLogger(f"test_fallback_{id(records)}")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_Handler())
    return FallbackManager(logger=logger), records


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestFallbackManagerInit:
    def test_default_logger_created(self):
        fm = FallbackManager()
        assert fm.logger is not None
        assert fm.logger.name == "FallbackManager"

    def test_custom_logger_used(self):
        custom = logging.getLogger("custom_test_logger")
        fm = FallbackManager(logger=custom)
        assert fm.logger is custom

    def test_none_logger_creates_default(self):
        fm = FallbackManager(logger=None)
        assert fm.logger.name == "FallbackManager"


# ---------------------------------------------------------------------------
# handle_missing_field
# ---------------------------------------------------------------------------

class TestHandleMissingField:
    def setup_method(self):
        self.fm, self.logs = _make_manager(capture_logs=True)

    def test_present_field_returned(self):
        data = {"name": "Alice", "age": 30}
        assert self.fm.handle_missing_field(data, "name") == "Alice"
        assert self.fm.handle_missing_field(data, "age") == 30

    def test_missing_field_returns_none_by_default(self):
        data = {"name": "Alice"}
        result = self.fm.handle_missing_field(data, "email")
        assert result is None

    def test_missing_field_returns_custom_default(self):
        data = {}
        result = self.fm.handle_missing_field(data, "score", default=0)
        assert result == 0

    def test_missing_field_returns_string_default(self):
        data = {"name": "Alice"}
        result = self.fm.handle_missing_field(data, "email", default="unknown@example.com")
        assert result == "unknown@example.com"

    def test_missing_field_logs_warning(self):
        data = {}
        self.fm.handle_missing_field(data, "missing_key", default="x")
        assert any(r.levelno == logging.WARNING for r in self.logs)

    def test_present_field_does_not_log_warning(self):
        data = {"key": "value"}
        self.fm.handle_missing_field(data, "key")
        assert not any(r.levelno == logging.WARNING for r in self.logs)

    def test_field_with_none_value_is_not_missing(self):
        """A field explicitly set to None is present; no warning should fire."""
        data = {"note": None}
        result = self.fm.handle_missing_field(data, "note", default="fallback")
        assert result is None  # returns the stored None, not the default
        assert not any(r.levelno == logging.WARNING for r in self.logs)

    def test_field_with_falsy_value_is_not_missing(self):
        data = {"count": 0, "flag": False, "label": ""}
        assert self.fm.handle_missing_field(data, "count", default=99) == 0
        assert self.fm.handle_missing_field(data, "flag", default=True) is False
        assert self.fm.handle_missing_field(data, "label", default="default") == ""


# ---------------------------------------------------------------------------
# handle_type_mismatch
# ---------------------------------------------------------------------------

class TestHandleTypeMismatch:
    def setup_method(self):
        self.fm, self.logs = _make_manager(capture_logs=True)

    def test_already_correct_type_returned_unchanged(self):
        assert self.fm.handle_type_mismatch(42, int) == 42
        assert self.fm.handle_type_mismatch(3.14, float) == 3.14
        assert self.fm.handle_type_mismatch("hello", str) == "hello"

    def test_string_to_int_conversion(self):
        result = self.fm.handle_type_mismatch("10", int)
        assert result == 10
        assert isinstance(result, int)

    def test_string_to_float_conversion(self):
        result = self.fm.handle_type_mismatch("3.14", float)
        assert abs(result - 3.14) < 1e-9

    def test_int_to_float_conversion(self):
        result = self.fm.handle_type_mismatch(5, float)
        assert result == 5.0

    def test_float_to_str_conversion(self):
        result = self.fm.handle_type_mismatch(1.5, str)
        assert result == "1.5"

    def test_unconvertible_string_returns_default(self):
        result = self.fm.handle_type_mismatch("not_a_number", float, default=0.0)
        assert result == 0.0

    def test_unconvertible_returns_none_default(self):
        result = self.fm.handle_type_mismatch("bad", int)
        assert result is None

    def test_conversion_failure_logs_error(self):
        self.fm.handle_type_mismatch("bad", int, default=-1)
        assert any(r.levelno == logging.ERROR for r in self.logs)

    def test_successful_conversion_does_not_log_error(self):
        self.fm.handle_type_mismatch("42", int)
        assert not any(r.levelno == logging.ERROR for r in self.logs)

    def test_bool_not_treated_as_int(self):
        """bool is a subclass of int; True should still be converted, not passed through."""
        result = self.fm.handle_type_mismatch(True, int)
        # True can be converted to int(1) — conversion should succeed
        assert result == 1

    def test_none_to_int_returns_default(self):
        result = self.fm.handle_type_mismatch(None, int, default=-1)
        assert result == -1

    def test_list_to_str_conversion(self):
        result = self.fm.handle_type_mismatch([1, 2], str)
        assert result == "[1, 2]"


# ---------------------------------------------------------------------------
# with_fallback
# ---------------------------------------------------------------------------

class TestWithFallback:
    def setup_method(self):
        self.fm, self.logs = _make_manager(capture_logs=True)

    def test_primary_success_returns_primary_result(self):
        result = self.fm.with_fallback(primary_func=lambda: 42)
        assert result == 42

    def test_primary_failure_executes_fallback(self):
        def bad():
            raise ValueError("oops")

        result = self.fm.with_fallback(
            primary_func=bad,
            fallback_func=lambda: "fallback_result",
        )
        assert result == "fallback_result"

    def test_both_fail_returns_default_value(self):
        def bad():
            raise RuntimeError("primary error")

        def also_bad():
            raise RuntimeError("fallback error")

        result = self.fm.with_fallback(
            primary_func=bad,
            fallback_func=also_bad,
            default_value="default",
        )
        assert result == "default"

    def test_primary_failure_no_fallback_returns_default(self):
        def bad():
            raise KeyError("missing")

        result = self.fm.with_fallback(primary_func=bad, default_value=0)
        assert result == 0

    def test_primary_failure_logs_error(self):
        def bad():
            raise ValueError("boom")

        self.fm.with_fallback(primary_func=bad)
        assert any(r.levelno == logging.ERROR for r in self.logs)

    def test_error_handler_called_on_primary_failure(self):
        captured = []

        def bad():
            raise TypeError("type error")

        def handler(exc):
            captured.append(exc)

        self.fm.with_fallback(primary_func=bad, error_handler=handler)
        assert len(captured) == 1
        assert isinstance(captured[0], TypeError)

    def test_error_handler_not_called_on_success(self):
        called = []
        self.fm.with_fallback(
            primary_func=lambda: "ok",
            error_handler=lambda e: called.append(e),
        )
        assert called == []

    def test_default_value_none_when_not_specified(self):
        def bad():
            raise Exception("err")

        result = self.fm.with_fallback(primary_func=bad)
        assert result is None

    def test_fallback_not_called_when_primary_succeeds(self):
        fallback_called = []

        def fallback():
            fallback_called.append(True)
            return "fallback"

        result = self.fm.with_fallback(
            primary_func=lambda: "primary",
            fallback_func=fallback,
        )
        assert result == "primary"
        assert fallback_called == []

    def test_error_handler_exception_does_not_propagate(self):
        """A buggy error_handler should not crash the caller."""
        def bad():
            raise ValueError("primary")

        def bad_handler(exc):
            raise RuntimeError("handler also broken")

        # Should not raise; should return default
        result = self.fm.with_fallback(
            primary_func=bad,
            error_handler=bad_handler,
            default_value="safe",
        )
        assert result == "safe"
