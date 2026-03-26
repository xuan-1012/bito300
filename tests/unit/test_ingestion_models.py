"""
Unit tests for ingestion data models

Tests validation rules and basic functionality of core data models.
"""

import pytest
from datetime import datetime
from src.ingestion.models import (
    HTTPMethod,
    FieldType,
    APIConfig,
    APIRequest,
    APIResponse,
    FlattenedRecord,
    FieldSchema,
)


class TestHTTPMethod:
    """Tests for HTTPMethod enum"""
    
    def test_http_method_values(self):
        """Test HTTPMethod enum has correct values"""
        assert HTTPMethod.GET.value == "GET"
        assert HTTPMethod.POST.value == "POST"


class TestFieldType:
    """Tests for FieldType enum"""
    
    def test_field_type_values(self):
        """Test FieldType enum has all expected values"""
        assert FieldType.NUMERIC.value == "numeric"
        assert FieldType.CATEGORICAL.value == "categorical"
        assert FieldType.DATETIME.value == "datetime"
        assert FieldType.TEXT.value == "text"
        assert FieldType.ID_LIKE.value == "id_like"
        assert FieldType.BOOLEAN.value == "boolean"
        assert FieldType.NULL.value == "null"
        assert FieldType.MIXED.value == "mixed"


class TestAPIConfig:
    """Tests for APIConfig dataclass"""
    
    def test_api_config_defaults(self):
        """Test APIConfig has correct default values"""
        config = APIConfig()
        assert config.base_url == "https://aws-event-api.bitopro.com/"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_backoff == 2.0
        assert config.rate_limit_per_second == 0.9
    
    def test_api_config_custom_values(self):
        """Test APIConfig accepts custom values"""
        config = APIConfig(
            base_url="https://custom.api.com/",
            timeout=60,
            max_retries=5,
            retry_backoff=3.0,
            rate_limit_per_second=1.5
        )
        assert config.base_url == "https://custom.api.com/"
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.retry_backoff == 3.0
        assert config.rate_limit_per_second == 1.5
    
    def test_api_config_validation_empty_base_url(self):
        """Test APIConfig rejects empty base_url"""
        with pytest.raises(ValueError, match="base_url must be non-empty"):
            APIConfig(base_url="")
    
    def test_api_config_validation_negative_timeout(self):
        """Test APIConfig rejects negative timeout"""
        with pytest.raises(ValueError, match="timeout must be positive"):
            APIConfig(timeout=-1)
    
    def test_api_config_validation_negative_max_retries(self):
        """Test APIConfig rejects negative max_retries"""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            APIConfig(max_retries=-1)
    
    def test_api_config_validation_negative_retry_backoff(self):
        """Test APIConfig rejects negative retry_backoff"""
        with pytest.raises(ValueError, match="retry_backoff must be positive"):
            APIConfig(retry_backoff=-1.0)
    
    def test_api_config_validation_negative_rate_limit(self):
        """Test APIConfig rejects negative rate_limit_per_second"""
        with pytest.raises(ValueError, match="rate_limit_per_second must be positive"):
            APIConfig(rate_limit_per_second=-0.5)


class TestAPIRequest:
    """Tests for APIRequest dataclass"""
    
    def test_api_request_valid(self):
        """Test APIRequest with valid parameters"""
        request = APIRequest(
            endpoint="/v1/transactions",
            method=HTTPMethod.GET,
            params={"limit": 100},
            headers={"Authorization": "Bearer token"},
            timeout=30,
            retry_count=0,
            max_retries=3
        )
        assert request.endpoint == "/v1/transactions"
        assert request.method == HTTPMethod.GET
        assert request.params == {"limit": 100}
        assert request.headers == {"Authorization": "Bearer token"}
        assert request.timeout == 30
        assert request.retry_count == 0
        assert request.max_retries == 3
    
    def test_api_request_validation_empty_endpoint(self):
        """Test APIRequest rejects empty endpoint"""
        with pytest.raises(ValueError, match="endpoint must be a non-empty string"):
            APIRequest(endpoint="", method=HTTPMethod.GET)
    
    def test_api_request_validation_invalid_method(self):
        """Test APIRequest rejects invalid method"""
        with pytest.raises(ValueError, match="method must be HTTPMethod.GET or HTTPMethod.POST"):
            APIRequest(endpoint="/v1/test", method="GET")  # String instead of enum
    
    def test_api_request_validation_negative_timeout(self):
        """Test APIRequest rejects negative timeout"""
        with pytest.raises(ValueError, match="timeout must be positive"):
            APIRequest(endpoint="/v1/test", method=HTTPMethod.GET, timeout=-1)
    
    def test_api_request_validation_retry_count_exceeds_max(self):
        """Test APIRequest rejects retry_count > max_retries"""
        with pytest.raises(ValueError, match="retry_count must not exceed max_retries"):
            APIRequest(
                endpoint="/v1/test",
                method=HTTPMethod.GET,
                retry_count=5,
                max_retries=3
            )


class TestAPIResponse:
    """Tests for APIResponse dataclass"""
    
    def test_api_response_valid(self):
        """Test APIResponse with valid parameters"""
        now = datetime.now()
        response = APIResponse(
            status_code=200,
            data={"result": "success"},
            headers={"Content-Type": "application/json"},
            timestamp=now,
            request_id="req-123",
            pagination_info={"page": 1, "total": 10}
        )
        assert response.status_code == 200
        assert response.data == {"result": "success"}
        assert response.headers == {"Content-Type": "application/json"}
        assert response.timestamp == now
        assert response.request_id == "req-123"
        assert response.pagination_info == {"page": 1, "total": 10}
    
    def test_api_response_validation_invalid_status_code(self):
        """Test APIResponse rejects invalid status codes"""
        with pytest.raises(ValueError, match="status_code must be a valid HTTP status code"):
            APIResponse(
                status_code=999,
                data={},
                headers={},
                timestamp=datetime.now(),
                request_id="req-123"
            )
    
    def test_api_response_validation_non_dict_data(self):
        """Test APIResponse rejects non-dict data"""
        with pytest.raises(ValueError, match="data must be a dictionary"):
            APIResponse(
                status_code=200,
                data="not a dict",
                headers={},
                timestamp=datetime.now(),
                request_id="req-123"
            )
    
    def test_api_response_validation_empty_request_id(self):
        """Test APIResponse rejects empty request_id"""
        with pytest.raises(ValueError, match="request_id must be a non-empty string"):
            APIResponse(
                status_code=200,
                data={},
                headers={},
                timestamp=datetime.now(),
                request_id=""
            )


class TestFlattenedRecord:
    """Tests for FlattenedRecord dataclass"""
    
    def test_flattened_record_valid(self):
        """Test FlattenedRecord with valid parameters"""
        now = datetime.now()
        record = FlattenedRecord(
            record_id="rec-123",
            source_endpoint="/v1/transactions",
            flattened_data={"user_id": "USR123", "amount": 100.0},
            original_structure={"user": {"id": "USR123"}, "amount": 100.0},
            flatten_timestamp=now
        )
        assert record.record_id == "rec-123"
        assert record.source_endpoint == "/v1/transactions"
        assert record.flattened_data == {"user_id": "USR123", "amount": 100.0}
        assert record.flatten_timestamp == now
    
    def test_flattened_record_validation_nested_data(self):
        """Test FlattenedRecord rejects nested structures in flattened_data"""
        with pytest.raises(ValueError, match="flattened_data must have no nested structures"):
            FlattenedRecord(
                record_id="rec-123",
                source_endpoint="/v1/test",
                flattened_data={"user": {"id": "USR123"}},  # Nested dict
                original_structure={},
                flatten_timestamp=datetime.now()
            )
    
    def test_flattened_record_validation_empty_record_id(self):
        """Test FlattenedRecord rejects empty record_id"""
        with pytest.raises(ValueError, match="record_id must be a non-empty string"):
            FlattenedRecord(
                record_id="",
                source_endpoint="/v1/test",
                flattened_data={},
                original_structure={},
                flatten_timestamp=datetime.now()
            )


class TestFieldSchema:
    """Tests for FieldSchema dataclass"""
    
    def test_field_schema_valid(self):
        """Test FieldSchema with valid parameters"""
        schema = FieldSchema(
            name="transaction_id",
            inferred_type=FieldType.ID_LIKE,
            nullable=False,
            sample_values=["TXN001", "TXN002"],
            null_count=0,
            total_count=100,
            confidence=0.95
        )
        assert schema.name == "transaction_id"
        assert schema.inferred_type == FieldType.ID_LIKE
        assert schema.nullable is False
        assert schema.sample_values == ["TXN001", "TXN002"]
        assert schema.null_count == 0
        assert schema.total_count == 100
        assert schema.confidence == 0.95
    
    def test_field_schema_to_dict(self):
        """Test FieldSchema.to_dict() serialization"""
        schema = FieldSchema(
            name="amount",
            inferred_type=FieldType.NUMERIC,
            nullable=True,
            sample_values=[100.0, 200.0],
            null_count=5,
            total_count=100,
            confidence=1.0
        )
        result = schema.to_dict()
        assert result == {
            "name": "amount",
            "inferred_type": "numeric",
            "nullable": True,
            "sample_values": [100.0, 200.0],
            "null_count": 5,
            "total_count": 100,
            "confidence": 1.0
        }
    
    def test_field_schema_validation_null_count_exceeds_total(self):
        """Test FieldSchema rejects null_count > total_count"""
        with pytest.raises(ValueError, match="null_count must not exceed total_count"):
            FieldSchema(
                name="test_field",
                inferred_type=FieldType.TEXT,
                nullable=True,
                sample_values=[],
                null_count=150,
                total_count=100,
                confidence=0.8
            )
    
    def test_field_schema_validation_invalid_confidence(self):
        """Test FieldSchema rejects confidence outside [0, 1]"""
        with pytest.raises(ValueError, match="confidence must be a number between 0 and 1"):
            FieldSchema(
                name="test_field",
                inferred_type=FieldType.TEXT,
                nullable=False,
                sample_values=[],
                null_count=0,
                total_count=100,
                confidence=1.5
            )
    
    def test_field_schema_validation_empty_name(self):
        """Test FieldSchema rejects empty name"""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            FieldSchema(
                name="",
                inferred_type=FieldType.TEXT,
                nullable=False,
                sample_values=[],
                null_count=0,
                total_count=100,
                confidence=0.8
            )
