"""
Unit tests for RawDataStorage components
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError
from src.ingestion.storage import StorageBackend, S3Storage


class ConcreteStorageBackend(StorageBackend):
    """Concrete implementation for testing abstract interface"""
    
    def __init__(self):
        self.storage = {}
    
    def save(self, data, key):
        self.storage[key] = data
        return f"test://{key}"
    
    def load(self, key):
        if key not in self.storage:
            raise KeyError(f"Key not found: {key}")
        return self.storage[key]


def test_storage_backend_is_abstract():
    """Test that StorageBackend cannot be instantiated directly"""
    with pytest.raises(TypeError):
        StorageBackend()


def test_concrete_implementation_save():
    """Test that concrete implementation can save data"""
    backend = ConcreteStorageBackend()
    data = {"test": "data", "value": 123}
    key = "test_key"
    
    uri = backend.save(data, key)
    
    assert uri == "test://test_key"
    assert backend.storage[key] == data


def test_concrete_implementation_load():
    """Test that concrete implementation can load data"""
    backend = ConcreteStorageBackend()
    data = {"test": "data", "value": 123}
    key = "test_key"
    
    backend.save(data, key)
    loaded_data = backend.load(key)
    
    assert loaded_data == data


def test_load_nonexistent_key_raises_error():
    """Test that loading non-existent key raises KeyError"""
    backend = ConcreteStorageBackend()
    
    with pytest.raises(KeyError):
        backend.load("nonexistent_key")


def test_save_and_load_complex_data():
    """Test saving and loading complex nested data"""
    backend = ConcreteStorageBackend()
    data = {
        "nested": {
            "field": "value",
            "list": [1, 2, 3]
        },
        "array": [{"id": 1}, {"id": 2}]
    }
    key = "complex_key"
    
    backend.save(data, key)
    loaded_data = backend.load(key)
    
    assert loaded_data == data


# S3Storage Tests

@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_initialization(mock_get_clients):
    """Test S3Storage initialization with bucket and prefix"""
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    storage = S3Storage(bucket_name="test-bucket", prefix="raw_data/")
    
    assert storage.bucket_name == "test-bucket"
    assert storage.prefix == "raw_data/"
    assert storage._s3_client == mock_s3_client


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_initialization_empty_bucket_raises_error(mock_get_clients):
    """Test S3Storage raises ValueError for empty bucket name"""
    with pytest.raises(ValueError, match="bucket_name cannot be empty"):
        S3Storage(bucket_name="")


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_initialization_normalizes_prefix(mock_get_clients):
    """Test S3Storage normalizes prefix with trailing slash"""
    mock_aws_clients = Mock()
    mock_aws_clients.s3 = Mock()
    mock_get_clients.return_value = mock_aws_clients
    
    # Test prefix without trailing slash
    storage1 = S3Storage(bucket_name="test-bucket", prefix="data")
    assert storage1.prefix == "data/"
    
    # Test prefix with trailing slash
    storage2 = S3Storage(bucket_name="test-bucket", prefix="data/")
    assert storage2.prefix == "data/"
    
    # Test empty prefix
    storage3 = S3Storage(bucket_name="test-bucket", prefix="")
    assert storage3.prefix == ""


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_save_success(mock_get_clients):
    """Test S3Storage saves data with encryption"""
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    storage = S3Storage(bucket_name="test-bucket", prefix="raw_data/")
    data = {"test": "data", "value": 123}
    key = "test_key.json"
    
    uri = storage.save(data, key)
    
    # Verify S3 put_object was called with correct parameters
    mock_s3_client.put_object.assert_called_once()
    call_args = mock_s3_client.put_object.call_args[1]
    
    assert call_args['Bucket'] == "test-bucket"
    assert call_args['Key'] == "raw_data/test_key.json"
    assert call_args['ServerSideEncryption'] == 'AES256'
    assert call_args['ContentType'] == 'application/json'
    assert json.loads(call_args['Body']) == data
    
    # Verify URI format
    assert uri == "s3://test-bucket/raw_data/test_key.json"


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_save_non_serializable_data_raises_error(mock_get_clients):
    """Test S3Storage raises ValueError for non-JSON-serializable data"""
    mock_aws_clients = Mock()
    mock_aws_clients.s3 = Mock()
    mock_get_clients.return_value = mock_aws_clients
    
    storage = S3Storage(bucket_name="test-bucket")
    
    # Create non-serializable data (e.g., object with circular reference)
    class NonSerializable:
        pass
    
    data = {"obj": NonSerializable()}
    
    with pytest.raises(ValueError, match="Data is not JSON-serializable"):
        storage.save(data, "test_key")


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_save_client_error_raises_ioerror(mock_get_clients):
    """Test S3Storage raises IOError on S3 ClientError"""
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    # Simulate S3 ClientError
    error_response = {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}}
    mock_s3_client.put_object.side_effect = ClientError(error_response, 'PutObject')
    
    storage = S3Storage(bucket_name="test-bucket")
    data = {"test": "data"}
    
    with pytest.raises(IOError, match="Failed to save to S3: AccessDenied"):
        storage.save(data, "test_key")


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_load_success(mock_get_clients):
    """Test S3Storage loads data successfully"""
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    # Mock S3 response
    data = {"test": "data", "value": 123}
    json_data = json.dumps(data)
    mock_body = Mock()
    mock_body.read.return_value = json_data.encode('utf-8')
    mock_s3_client.get_object.return_value = {'Body': mock_body}
    
    storage = S3Storage(bucket_name="test-bucket", prefix="raw_data/")
    loaded_data = storage.load("test_key.json")
    
    # Verify S3 get_object was called with correct parameters
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="raw_data/test_key.json"
    )
    
    # Verify loaded data matches
    assert loaded_data == data


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_load_nonexistent_key_raises_keyerror(mock_get_clients):
    """Test S3Storage raises KeyError for non-existent key"""
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    # Simulate NoSuchKey error
    error_response = {'Error': {'Code': 'NoSuchKey', 'Message': 'Key not found'}}
    mock_s3_client.get_object.side_effect = ClientError(error_response, 'GetObject')
    
    storage = S3Storage(bucket_name="test-bucket")
    
    with pytest.raises(KeyError, match="Key not found in S3"):
        storage.load("nonexistent_key")


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_load_invalid_json_raises_ioerror(mock_get_clients):
    """Test S3Storage raises IOError for invalid JSON data"""
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    # Mock S3 response with invalid JSON
    mock_body = Mock()
    mock_body.read.return_value = b"invalid json {{"
    mock_s3_client.get_object.return_value = {'Body': mock_body}
    
    storage = S3Storage(bucket_name="test-bucket")
    
    with pytest.raises(IOError, match="Invalid JSON data in S3 key"):
        storage.load("test_key")


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_load_client_error_raises_ioerror(mock_get_clients):
    """Test S3Storage raises IOError on S3 ClientError (non-NoSuchKey)"""
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    # Simulate S3 ClientError (not NoSuchKey)
    error_response = {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}}
    mock_s3_client.get_object.side_effect = ClientError(error_response, 'GetObject')
    
    storage = S3Storage(bucket_name="test-bucket")
    
    with pytest.raises(IOError, match="Failed to load from S3: AccessDenied"):
        storage.load("test_key")


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_save_and_load_complex_data(mock_get_clients):
    """Test S3Storage can save and load complex nested data"""
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    storage = S3Storage(bucket_name="test-bucket")
    
    # Complex nested data
    data = {
        "nested": {
            "field": "value",
            "list": [1, 2, 3]
        },
        "array": [{"id": 1}, {"id": 2}],
        "null_field": None,
        "boolean": True,
        "number": 123.45
    }
    
    # Save
    storage.save(data, "complex_key")
    
    # Mock load response
    json_data = json.dumps(data)
    mock_body = Mock()
    mock_body.read.return_value = json_data.encode('utf-8')
    mock_s3_client.get_object.return_value = {'Body': mock_body}
    
    # Load
    loaded_data = storage.load("complex_key")
    
    assert loaded_data == data



# LocalStorage Tests

def test_localstorage_initialization():
    """Test LocalStorage initialization with base path"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path="raw_data/")
    
    assert storage.base_path == Path("raw_data/")


def test_localstorage_initialization_default_path():
    """Test LocalStorage uses default base path"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage()
    
    assert storage.base_path == Path("raw_data/")


def test_localstorage_initialization_none_raises_error():
    """Test LocalStorage raises ValueError for None base_path"""
    from src.ingestion.storage import LocalStorage
    
    with pytest.raises(ValueError, match="base_path cannot be None"):
        LocalStorage(base_path=None)


def test_localstorage_save_success(tmp_path):
    """Test LocalStorage saves data to filesystem"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    data = {"test": "data", "value": 123}
    key = "test_key.json"
    
    uri = storage.save(data, key)
    
    # Verify URI format
    assert uri.startswith("file://")
    assert "test_key.json" in uri
    
    # Verify file was created
    file_path = tmp_path / key
    assert file_path.exists()
    
    # Verify file content
    with open(file_path, 'r') as f:
        saved_data = json.load(f)
    assert saved_data == data


def test_localstorage_save_creates_directory_structure(tmp_path):
    """Test LocalStorage creates nested directories if not exists"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    data = {"test": "data"}
    key = "nested/dir/structure/test_key.json"
    
    uri = storage.save(data, key)
    
    # Verify nested directories were created
    file_path = tmp_path / "nested" / "dir" / "structure" / "test_key.json"
    assert file_path.exists()
    assert file_path.parent.exists()
    
    # Verify file content
    with open(file_path, 'r') as f:
        saved_data = json.load(f)
    assert saved_data == data


def test_localstorage_save_non_serializable_data_raises_error(tmp_path):
    """Test LocalStorage raises ValueError for non-JSON-serializable data"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    
    # Create non-serializable data
    class NonSerializable:
        pass
    
    data = {"obj": NonSerializable()}
    
    with pytest.raises(ValueError, match="Data is not JSON-serializable"):
        storage.save(data, "test_key")


def test_localstorage_load_success(tmp_path):
    """Test LocalStorage loads data successfully"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    data = {"test": "data", "value": 123}
    key = "test_key.json"
    
    # Save data first
    storage.save(data, key)
    
    # Load data
    loaded_data = storage.load(key)
    
    # Verify loaded data matches
    assert loaded_data == data


def test_localstorage_load_nonexistent_key_raises_keyerror(tmp_path):
    """Test LocalStorage raises KeyError for non-existent key"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    
    with pytest.raises(KeyError, match="Key not found in local filesystem"):
        storage.load("nonexistent_key.json")


def test_localstorage_load_invalid_json_raises_ioerror(tmp_path):
    """Test LocalStorage raises IOError for invalid JSON data"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    key = "invalid.json"
    
    # Create file with invalid JSON
    file_path = tmp_path / key
    with open(file_path, 'w') as f:
        f.write("invalid json {{")
    
    with pytest.raises(IOError, match="Invalid JSON data in file"):
        storage.load(key)


def test_localstorage_save_and_load_complex_data(tmp_path):
    """Test LocalStorage can save and load complex nested data"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    
    # Complex nested data
    data = {
        "nested": {
            "field": "value",
            "list": [1, 2, 3]
        },
        "array": [{"id": 1}, {"id": 2}],
        "null_field": None,
        "boolean": True,
        "number": 123.45
    }
    
    key = "complex_key.json"
    
    # Save
    storage.save(data, key)
    
    # Load
    loaded_data = storage.load(key)
    
    assert loaded_data == data


def test_localstorage_multiple_saves_to_same_key(tmp_path):
    """Test LocalStorage overwrites existing file on save"""
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    key = "test_key.json"
    
    # First save
    data1 = {"version": 1}
    storage.save(data1, key)
    
    # Second save (overwrite)
    data2 = {"version": 2}
    storage.save(data2, key)
    
    # Load and verify latest data
    loaded_data = storage.load(key)
    assert loaded_data == data2
    assert loaded_data != data1


# RawDataStorage Tests

from datetime import datetime
from src.ingestion.storage import LocalStorage, RawDataStorage


def test_rawdatastorage_initialization():
    """Test RawDataStorage initializes with a backend"""
    backend = ConcreteStorageBackend()
    storage = RawDataStorage(backend=backend)
    assert storage.backend is backend


def test_rawdatastorage_initialization_none_backend_raises_error():
    """Test RawDataStorage raises ValueError for None backend"""
    with pytest.raises(ValueError, match="backend cannot be None"):
        RawDataStorage(backend=None)


def test_rawdatastorage_generate_key_format():
    """Test generate_key produces expected format"""
    backend = ConcreteStorageBackend()
    storage = RawDataStorage(backend=backend)
    ts = datetime(2024, 1, 15, 10, 30, 0)

    key = storage.generate_key("/v1/transactions", ts)

    assert key.endswith(".json")
    # Colons are replaced with dashes for filesystem safety
    assert "2024-01-15T10-30-00" in key
    assert key.startswith("v1")


def test_rawdatastorage_generate_key_sanitizes_endpoint():
    """Test generate_key sanitizes special characters in endpoint"""
    backend = ConcreteStorageBackend()
    storage = RawDataStorage(backend=backend)
    ts = datetime(2024, 1, 1, 0, 0, 0)

    key = storage.generate_key("/v1/order?pair=BTC_TWD", ts)

    # Should not contain raw ? or = characters
    assert "?" not in key
    assert "=" not in key


def test_rawdatastorage_generate_key_empty_endpoint_raises_error():
    """Test generate_key raises ValueError for empty endpoint"""
    backend = ConcreteStorageBackend()
    storage = RawDataStorage(backend=backend)
    ts = datetime(2024, 1, 1)

    with pytest.raises(ValueError, match="endpoint must be a non-empty string"):
        storage.generate_key("", ts)


def test_rawdatastorage_generate_key_none_timestamp_raises_error():
    """Test generate_key raises ValueError for None timestamp"""
    backend = ConcreteStorageBackend()
    storage = RawDataStorage(backend=backend)

    with pytest.raises(ValueError, match="timestamp cannot be None"):
        storage.generate_key("/v1/transactions", None)


def test_rawdatastorage_store_raw_response_returns_uri():
    """Test store_raw_response returns a storage URI"""
    backend = ConcreteStorageBackend()
    storage = RawDataStorage(backend=backend)
    response = {"data": [{"id": "TXN001", "amount": 100.0}]}
    ts = datetime(2024, 1, 15, 10, 0, 0)

    uri = storage.store_raw_response(response, "/v1/transactions", timestamp=ts)

    assert uri.startswith("test://")


def test_rawdatastorage_store_raw_response_without_modification():
    """Test store_raw_response stores data without modification (Req 5.1)"""
    backend = ConcreteStorageBackend()
    storage = RawDataStorage(backend=backend)
    original = {"data": [{"id": "TXN001"}], "pagination": {"page": 1}}
    ts = datetime(2024, 1, 15, 10, 0, 0)

    storage.store_raw_response(original, "/v1/transactions", timestamp=ts)

    # Find the stored value
    stored_key = list(backend.storage.keys())[0]
    assert backend.storage[stored_key] == original


def test_rawdatastorage_store_raw_response_defaults_timestamp():
    """Test store_raw_response uses current time when timestamp is None"""
    backend = ConcreteStorageBackend()
    storage = RawDataStorage(backend=backend)
    response = {"data": []}

    uri = storage.store_raw_response(response, "/v1/transactions")

    assert uri is not None
    assert len(backend.storage) == 1


def test_rawdatastorage_store_raw_response_non_serializable_raises_error():
    """Test store_raw_response raises ValueError for non-serializable data (Req 9.6)"""
    backend = ConcreteStorageBackend()
    storage = RawDataStorage(backend=backend)

    class NonSerializable:
        pass

    with pytest.raises(ValueError, match="not JSON-serializable"):
        storage.store_raw_response({"obj": NonSerializable()}, "/v1/transactions")


def test_rawdatastorage_with_local_storage(tmp_path):
    """Test RawDataStorage works end-to-end with LocalStorage backend"""
    local = LocalStorage(base_path=str(tmp_path))
    storage = RawDataStorage(backend=local)
    response = {"data": [{"id": "TXN001", "amount": 50.0}]}
    ts = datetime(2024, 3, 1, 12, 0, 0)

    uri = storage.store_raw_response(response, "/v1/transactions", timestamp=ts)

    assert uri.startswith("file://")
    # Verify the file was actually written and contains the original data
    key = storage.generate_key("/v1/transactions", ts)
    loaded = local.load(key)
    assert loaded == response
