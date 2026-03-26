"""
Integration tests for S3Storage with AWS services

These tests verify S3Storage integration with boto3 and AWS clients.
"""

import pytest
import json
from unittest.mock import patch, Mock
from src.ingestion.storage import S3Storage


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_full_workflow(mock_get_clients):
    """
    Integration test: Full workflow of saving and loading data
    
    **Validates: Requirements 5.3, 12.3**
    """
    # Setup mock AWS clients
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    # Initialize S3Storage
    storage = S3Storage(
        bucket_name="crypto-raw-data-bucket",
        prefix="bitopro/transactions/"
    )
    
    # Test data (simulating BitoPro API response)
    api_response = {
        "data": [
            {
                "id": "TXN001",
                "amount": 100.50,
                "timestamp": "2024-01-01T10:00:00Z",
                "user_id": "USR123"
            },
            {
                "id": "TXN002",
                "amount": 200.75,
                "timestamp": "2024-01-01T11:00:00Z",
                "user_id": "USR456"
            }
        ],
        "pagination": {
            "page": 1,
            "total_pages": 1
        }
    }
    
    # Save data
    key = "2024-01-01/transactions_10-00-00.json"
    uri = storage.save(api_response, key)
    
    # Verify save operation
    assert uri == "s3://crypto-raw-data-bucket/bitopro/transactions/2024-01-01/transactions_10-00-00.json"
    mock_s3_client.put_object.assert_called_once()
    
    # Verify encryption was enabled
    call_args = mock_s3_client.put_object.call_args[1]
    assert call_args['ServerSideEncryption'] == 'AES256'
    assert call_args['Bucket'] == "crypto-raw-data-bucket"
    assert call_args['Key'] == "bitopro/transactions/2024-01-01/transactions_10-00-00.json"
    
    # Mock load response
    json_data = json.dumps(api_response)
    mock_body = Mock()
    mock_body.read.return_value = json_data.encode('utf-8')
    mock_s3_client.get_object.return_value = {'Body': mock_body}
    
    # Load data
    loaded_data = storage.load(key)
    
    # Verify load operation
    assert loaded_data == api_response
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="crypto-raw-data-bucket",
        Key="bitopro/transactions/2024-01-01/transactions_10-00-00.json"
    )


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_with_aws_clients_singleton(mock_get_clients):
    """
    Test S3Storage uses AWSClients singleton correctly
    
    **Validates: Requirements 5.3**
    """
    # Setup mock
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    # Create multiple S3Storage instances
    storage1 = S3Storage(bucket_name="bucket1")
    storage2 = S3Storage(bucket_name="bucket2")
    
    # Verify get_aws_clients was called for each instance
    assert mock_get_clients.call_count == 2
    
    # Verify both use the same S3 client (from singleton)
    assert storage1._s3_client == storage2._s3_client


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_handles_large_data(mock_get_clients):
    """
    Test S3Storage can handle large JSON payloads
    
    **Validates: Requirements 5.1, 5.3**
    """
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    storage = S3Storage(bucket_name="test-bucket", prefix="")
    
    # Create large data (1000 records)
    large_data = {
        "data": [
            {
                "id": f"TXN{i:06d}",
                "amount": i * 10.5,
                "timestamp": f"2024-01-01T{i % 24:02d}:00:00Z"
            }
            for i in range(1000)
        ]
    }
    
    # Save large data
    uri = storage.save(large_data, "large_dataset.json")
    
    # Verify save was called
    assert uri == "s3://test-bucket/large_dataset.json"
    mock_s3_client.put_object.assert_called_once()
    
    # Verify data was serialized correctly
    call_args = mock_s3_client.put_object.call_args[1]
    saved_data = json.loads(call_args['Body'])
    assert len(saved_data['data']) == 1000


@patch('src.ingestion.storage.get_aws_clients')
def test_s3storage_private_bucket_configuration(mock_get_clients):
    """
    Test S3Storage is configured for private bucket access
    
    **Validates: Requirements 12.3**
    """
    mock_aws_clients = Mock()
    mock_s3_client = Mock()
    mock_aws_clients.s3 = mock_s3_client
    mock_get_clients.return_value = mock_aws_clients
    
    storage = S3Storage(bucket_name="private-bucket")
    data = {"sensitive": "data"}
    
    # Save data
    storage.save(data, "sensitive_key.json")
    
    # Verify encryption is enabled (requirement for private buckets)
    call_args = mock_s3_client.put_object.call_args[1]
    assert call_args['ServerSideEncryption'] == 'AES256'
    
    # Note: Bucket ACL and policies are configured at infrastructure level,
    # not in the application code. This test verifies encryption is enabled.



# LocalStorage Integration Tests

def test_localstorage_full_workflow(tmp_path):
    """
    Integration test: Full workflow of saving and loading data with LocalStorage
    
    **Validates: Requirements 5.4**
    """
    from src.ingestion.storage import LocalStorage
    
    # Initialize LocalStorage
    storage = LocalStorage(
        base_path=str(tmp_path / "bitopro" / "transactions")
    )
    
    # Test data (simulating BitoPro API response)
    api_response = {
        "data": [
            {
                "id": "TXN001",
                "amount": 100.50,
                "timestamp": "2024-01-01T10:00:00Z",
                "user_id": "USR123"
            },
            {
                "id": "TXN002",
                "amount": 200.75,
                "timestamp": "2024-01-01T11:00:00Z",
                "user_id": "USR456"
            }
        ],
        "pagination": {
            "page": 1,
            "total_pages": 1
        }
    }
    
    # Save data
    key = "2024-01-01/transactions_10-00-00.json"
    uri = storage.save(api_response, key)
    
    # Verify save operation
    assert uri.startswith("file://")
    assert "2024-01-01/transactions_10-00-00.json" in uri
    
    # Verify file exists
    file_path = tmp_path / "bitopro" / "transactions" / "2024-01-01" / "transactions_10-00-00.json"
    assert file_path.exists()
    
    # Load data
    loaded_data = storage.load(key)
    
    # Verify load operation
    assert loaded_data == api_response


def test_localstorage_handles_large_data(tmp_path):
    """
    Test LocalStorage can handle large JSON payloads
    
    **Validates: Requirements 5.1, 5.4**
    """
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    
    # Create large data (1000 records)
    large_data = {
        "data": [
            {
                "id": f"TXN{i:06d}",
                "amount": i * 10.5,
                "timestamp": f"2024-01-01T{i % 24:02d}:00:00Z"
            }
            for i in range(1000)
        ]
    }
    
    # Save large data
    uri = storage.save(large_data, "large_dataset.json")
    
    # Verify save was successful
    assert uri.startswith("file://")
    
    # Load and verify
    loaded_data = storage.load("large_dataset.json")
    assert len(loaded_data['data']) == 1000
    assert loaded_data == large_data


def test_localstorage_concurrent_saves_different_keys(tmp_path):
    """
    Test LocalStorage can handle multiple saves to different keys
    
    **Validates: Requirements 5.4**
    """
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    
    # Save multiple files
    data1 = {"id": 1, "value": "first"}
    data2 = {"id": 2, "value": "second"}
    data3 = {"id": 3, "value": "third"}
    
    uri1 = storage.save(data1, "file1.json")
    uri2 = storage.save(data2, "file2.json")
    uri3 = storage.save(data3, "nested/file3.json")
    
    # Verify all files exist
    assert (tmp_path / "file1.json").exists()
    assert (tmp_path / "file2.json").exists()
    assert (tmp_path / "nested" / "file3.json").exists()
    
    # Load and verify each file
    assert storage.load("file1.json") == data1
    assert storage.load("file2.json") == data2
    assert storage.load("nested/file3.json") == data3


def test_localstorage_preserves_data_integrity(tmp_path):
    """
    Test LocalStorage preserves complete data without modification
    
    **Validates: Requirements 5.1**
    """
    from src.ingestion.storage import LocalStorage
    
    storage = LocalStorage(base_path=str(tmp_path))
    
    # Original data with various types
    original_data = {
        "string": "test",
        "integer": 42,
        "float": 3.14159,
        "boolean": True,
        "null": None,
        "array": [1, 2, 3],
        "nested": {
            "deep": {
                "value": "preserved"
            }
        },
        "unicode": "测试数据",
        "special_chars": "!@#$%^&*()"
    }
    
    # Save and load
    storage.save(original_data, "integrity_test.json")
    loaded_data = storage.load("integrity_test.json")
    
    # Verify exact match
    assert loaded_data == original_data
    assert type(loaded_data["integer"]) == int
    assert type(loaded_data["float"]) == float
    assert type(loaded_data["boolean"]) == bool
    assert loaded_data["null"] is None
