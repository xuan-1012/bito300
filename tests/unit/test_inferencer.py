"""
Unit tests for SchemaInferencer.

Covers:
- Initialization and configuration validation
- Numeric type detection (_is_numeric)
- Datetime pattern matching (_is_datetime)
- ID-like pattern detection (_is_id_like / is_id_field_name)
- _infer_field_type logic (mixed types, ID-name heuristic, boolean, null)
- infer_schema() – nullable detection, null counts, field coverage
- export_schema() – JSON file output
"""

import json
import os
import tempfile

import pytest

from src.ingestion.inferencer import SchemaInferencer
from src.ingestion.models import FieldType


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestSchemaInferencerInit:
    def test_defaults(self):
        si = SchemaInferencer()
        assert si.sample_size == 100
        assert si.confidence_threshold == 0.8

    def test_custom_values(self):
        si = SchemaInferencer(sample_size=50, confidence_threshold=0.6)
        assert si.sample_size == 50
        assert si.confidence_threshold == 0.6

    def test_invalid_sample_size_zero(self):
        with pytest.raises(ValueError, match="sample_size"):
            SchemaInferencer(sample_size=0)

    def test_invalid_sample_size_negative(self):
        with pytest.raises(ValueError, match="sample_size"):
            SchemaInferencer(sample_size=-1)

    def test_invalid_confidence_below_zero(self):
        with pytest.raises(ValueError, match="confidence_threshold"):
            SchemaInferencer(confidence_threshold=-0.1)

    def test_invalid_confidence_above_one(self):
        with pytest.raises(ValueError, match="confidence_threshold"):
            SchemaInferencer(confidence_threshold=1.1)


# ---------------------------------------------------------------------------
# _is_numeric
# ---------------------------------------------------------------------------

class TestIsNumeric:
    def setup_method(self):
        self.si = SchemaInferencer()

    def test_int_is_numeric(self):
        assert self.si._is_numeric(42) is True

    def test_float_is_numeric(self):
        assert self.si._is_numeric(3.14) is True

    def test_negative_number(self):
        assert self.si._is_numeric(-7) is True

    def test_numeric_string(self):
        assert self.si._is_numeric("123") is True

    def test_float_string(self):
        assert self.si._is_numeric("3.14") is True

    def test_negative_numeric_string(self):
        assert self.si._is_numeric("-99.5") is True

    def test_non_numeric_string(self):
        assert self.si._is_numeric("hello") is False

    def test_bool_is_not_numeric(self):
        # booleans should not be treated as numeric
        assert self.si._is_numeric(True) is False
        assert self.si._is_numeric(False) is False

    def test_none_is_not_numeric(self):
        assert self.si._is_numeric(None) is False

    def test_list_is_not_numeric(self):
        assert self.si._is_numeric([1, 2]) is False


# ---------------------------------------------------------------------------
# _is_datetime
# ---------------------------------------------------------------------------

class TestIsDatetime:
    def setup_method(self):
        self.si = SchemaInferencer()

    def test_iso8601(self):
        assert self.si._is_datetime("2024-01-15T10:30:00") is True

    def test_date_only(self):
        assert self.si._is_datetime("2024-01-15") is True

    def test_mm_dd_yyyy(self):
        assert self.si._is_datetime("01/15/2024") is True

    def test_unix_timestamp_10_digits(self):
        assert self.si._is_datetime("1705312200") is True

    def test_unix_ms_13_digits(self):
        assert self.si._is_datetime("1705312200000") is True

    def test_plain_text_not_datetime(self):
        assert self.si._is_datetime("hello world") is False

    def test_short_number_not_datetime(self):
        assert self.si._is_datetime("12345") is False

    def test_non_string_not_datetime(self):
        assert self.si._is_datetime(1705312200) is False
        assert self.si._is_datetime(None) is False


# ---------------------------------------------------------------------------
# _is_id_like
# ---------------------------------------------------------------------------

class TestIsIdLike:
    def setup_method(self):
        self.si = SchemaInferencer()

    def test_uuid(self):
        assert self.si._is_id_like("550e8400-e29b-41d4-a716-446655440000") is True

    def test_uuid_uppercase(self):
        assert self.si._is_id_like("550E8400-E29B-41D4-A716-446655440000") is True

    def test_md5_hash(self):
        assert self.si._is_id_like("d41d8cd98f00b204e9800998ecf8427e") is True

    def test_sha256_hash(self):
        assert self.si._is_id_like("a" * 64) is True

    def test_alphanumeric_id(self):
        assert self.si._is_id_like("USR123456") is True

    def test_alphanumeric_id_short_prefix(self):
        assert self.si._is_id_like("TXN0001") is True

    def test_plain_word_not_id(self):
        assert self.si._is_id_like("hello") is False

    def test_numeric_string_not_id(self):
        assert self.si._is_id_like("12345") is False

    def test_non_string_not_id(self):
        assert self.si._is_id_like(12345) is False
        assert self.si._is_id_like(None) is False


# ---------------------------------------------------------------------------
# is_id_field_name
# ---------------------------------------------------------------------------

class TestIsIdFieldName:
    def test_field_named_id(self):
        assert SchemaInferencer.is_id_field_name("user_id") is True

    def test_field_named_uuid(self):
        assert SchemaInferencer.is_id_field_name("uuid") is True

    def test_field_named_key(self):
        assert SchemaInferencer.is_id_field_name("api_key") is True

    def test_field_named_hash(self):
        assert SchemaInferencer.is_id_field_name("tx_hash") is True

    def test_field_named_token(self):
        assert SchemaInferencer.is_id_field_name("access_token") is True

    def test_field_named_code(self):
        assert SchemaInferencer.is_id_field_name("order_code") is True

    def test_unrelated_field(self):
        assert SchemaInferencer.is_id_field_name("amount") is False

    def test_empty_field_name(self):
        assert SchemaInferencer.is_id_field_name("") is False


# ---------------------------------------------------------------------------
# _infer_field_type
# ---------------------------------------------------------------------------

class TestInferFieldType:
    def setup_method(self):
        self.si = SchemaInferencer()

    def test_all_numeric(self):
        ft, conf = self.si._infer_field_type([1, 2, 3, 4, 5])
        assert ft == FieldType.NUMERIC
        assert conf == 1.0

    def test_all_datetime(self):
        values = ["2024-01-01", "2024-02-01", "2024-03-01"]
        ft, conf = self.si._infer_field_type(values)
        assert ft == FieldType.DATETIME
        assert conf == 1.0

    def test_all_id_like(self):
        values = ["USR0001", "USR0002", "USR0003"]
        ft, conf = self.si._infer_field_type(values)
        assert ft == FieldType.ID_LIKE
        assert conf == 1.0

    def test_all_boolean(self):
        values = [True, False, True, True]
        ft, conf = self.si._infer_field_type(values)
        assert ft == FieldType.BOOLEAN
        assert conf == 1.0

    def test_all_text(self):
        values = ["apple", "banana", "cherry"]
        ft, conf = self.si._infer_field_type(values)
        assert ft == FieldType.TEXT
        assert conf == 1.0

    def test_empty_values_returns_null(self):
        ft, conf = self.si._infer_field_type([])
        assert ft == FieldType.NULL
        assert conf == 1.0

    def test_mixed_types_low_confidence(self):
        # 50% numeric, 50% text → confidence 0.5 < 0.6 → MIXED
        values = [1, 2, "hello", "world"]
        ft, conf = self.si._infer_field_type(values)
        assert ft == FieldType.MIXED
        assert conf < 0.6

    def test_numeric_with_id_field_name_prefers_id_like(self):
        values = [1001, 1002, 1003]
        ft, conf = self.si._infer_field_type(values, field_name="user_id")
        assert ft == FieldType.ID_LIKE

    def test_numeric_without_id_field_name_stays_numeric(self):
        values = [1001, 1002, 1003]
        ft, conf = self.si._infer_field_type(values, field_name="amount")
        assert ft == FieldType.NUMERIC


# ---------------------------------------------------------------------------
# infer_schema
# ---------------------------------------------------------------------------

class TestInferSchema:
    def setup_method(self):
        self.si = SchemaInferencer()

    def test_basic_schema_inference(self):
        data = [
            {"amount": 100.0, "status": "completed", "ts": "2024-01-01"},
            {"amount": 200.0, "status": "pending",   "ts": "2024-01-02"},
        ]
        schema = self.si.infer_schema(data)
        assert "amount" in schema
        assert "status" in schema
        assert "ts" in schema
        assert schema["amount"].inferred_type == FieldType.NUMERIC
        assert schema["ts"].inferred_type == FieldType.DATETIME

    def test_nullable_field_detected(self):
        data = [
            {"amount": 100.0, "note": None},
            {"amount": 200.0, "note": "ok"},
        ]
        schema = self.si.infer_schema(data)
        assert schema["note"].nullable is True
        assert schema["note"].null_count == 1

    def test_non_nullable_field(self):
        data = [{"amount": 1.0}, {"amount": 2.0}]
        schema = self.si.infer_schema(data)
        assert schema["amount"].nullable is False
        assert schema["amount"].null_count == 0

    def test_total_count_correct(self):
        data = [{"x": i} for i in range(10)]
        schema = self.si.infer_schema(data)
        assert schema["x"].total_count == 10

    def test_all_null_field(self):
        data = [{"x": None}, {"x": None}]
        schema = self.si.infer_schema(data)
        assert schema["x"].nullable is True
        assert schema["x"].null_count == 2
        assert schema["x"].inferred_type == FieldType.NULL

    def test_empty_data_returns_empty_schema(self):
        schema = self.si.infer_schema([])
        assert schema == {}

    def test_id_field_name_heuristic(self):
        data = [{"user_id": 1001}, {"user_id": 1002}, {"user_id": 1003}]
        schema = self.si.infer_schema(data)
        assert schema["user_id"].inferred_type == FieldType.ID_LIKE

    def test_sample_values_stored(self):
        data = [{"v": i} for i in range(20)]
        schema = self.si.infer_schema(data)
        # sample_values capped at 10
        assert len(schema["v"].sample_values) <= 10

    def test_fields_from_all_records_collected(self):
        # Field 'b' only appears in second record
        data = [{"a": 1}, {"a": 2, "b": "hello"}]
        schema = self.si.infer_schema(data)
        assert "a" in schema
        assert "b" in schema


# ---------------------------------------------------------------------------
# export_schema
# ---------------------------------------------------------------------------

class TestExportSchema:
    def setup_method(self):
        self.si = SchemaInferencer()

    def test_export_creates_file(self):
        data = [{"amount": 1.0, "label": "x"}]
        schema = self.si.infer_schema(data)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = tmp.name
        try:
            result_path = self.si.export_schema(schema, output_path=path)
            assert result_path == path
            assert os.path.exists(path)
        finally:
            os.unlink(path)

    def test_export_valid_json(self):
        data = [{"amount": 1.0}]
        schema = self.si.infer_schema(data)
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as tmp:
            path = tmp.name
        try:
            self.si.export_schema(schema, output_path=path)
            with open(path, "r") as fh:
                loaded = json.load(fh)
            assert "amount" in loaded
            assert loaded["amount"]["inferred_type"] == FieldType.NUMERIC.value
        finally:
            os.unlink(path)

    def test_export_field_count_in_output(self):
        data = [{"a": 1, "b": "x", "c": "2024-01-01"}]
        schema = self.si.infer_schema(data)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            path = tmp.name
        try:
            self.si.export_schema(schema, output_path=path)
            with open(path, "r") as fh:
                loaded = json.load(fh)
            assert len(loaded) == 3
        finally:
            os.unlink(path)
