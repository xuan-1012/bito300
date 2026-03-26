"""
AWS Clients Utility Module

This module initializes and manages boto3 clients for AWS services used in the
Crypto Suspicious Account Detection system. It provides connection pooling,
reuse, and error handling for:
- S3 (for storing raw data, features, risk scores, reports)
- DynamoDB (for account risk profiles)
- Bedrock Runtime (for AI risk analysis)
- Secrets Manager (for API credentials)

The module supports configuration via environment variables and provides
a clean interface for Lambda functions to access these clients.

**Validates: Requirements 1.1, 12.6**
"""

import os
import logging
from typing import Optional
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class AWSClientError(Exception):
    """Custom exception for AWS client initialization errors."""
    pass


class AWSClients:
    """
    Singleton class for managing AWS service clients with connection pooling.
    
    This class initializes boto3 clients for S3, DynamoDB, Bedrock Runtime,
    and Secrets Manager. Clients are created once and reused across invocations
    to improve performance and reduce connection overhead.
    
    Configuration is read from environment variables:
    - AWS_REGION: AWS region (default: us-east-1)
    - AWS_MAX_ATTEMPTS: Maximum retry attempts (default: 3)
    - AWS_CONNECT_TIMEOUT: Connection timeout in seconds (default: 5)
    - AWS_READ_TIMEOUT: Read timeout in seconds (default: 60)
    
    Example:
        >>> clients = AWSClients.get_instance()
        >>> s3 = clients.s3
        >>> dynamodb = clients.dynamodb
        >>> bedrock = clients.bedrock_runtime
        >>> secrets = clients.secrets_manager
    """
    
    _instance: Optional['AWSClients'] = None
    
    def __init__(self):
        """
        Initialize AWS clients with connection pooling and retry configuration.
        
        This constructor should not be called directly. Use get_instance() instead.
        """
        if AWSClients._instance is not None:
            raise RuntimeError(
                "AWSClients is a singleton. Use AWSClients.get_instance() instead."
            )
        
        # Read configuration from environment variables
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        max_attempts = int(os.environ.get('AWS_MAX_ATTEMPTS', '3'))
        connect_timeout = int(os.environ.get('AWS_CONNECT_TIMEOUT', '5'))
        read_timeout = int(os.environ.get('AWS_READ_TIMEOUT', '60'))
        
        # Configure boto3 with retry and timeout settings
        self.config = Config(
            region_name=self.region,
            retries={
                'max_attempts': max_attempts,
                'mode': 'adaptive'  # Adaptive retry mode for better handling
            },
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            max_pool_connections=50  # Connection pooling
        )
        
        # Initialize clients (lazy initialization)
        self._s3 = None
        self._dynamodb = None
        self._bedrock_runtime = None
        self._secrets_manager = None
        
        logger.info(
            f"AWSClients initialized with region={self.region}, "
            f"max_attempts={max_attempts}, "
            f"connect_timeout={connect_timeout}s, "
            f"read_timeout={read_timeout}s"
        )
    
    @classmethod
    def get_instance(cls) -> 'AWSClients':
        """
        Get the singleton instance of AWSClients.
        
        Returns:
            AWSClients: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance.
        
        This is primarily useful for testing to ensure a clean state.
        """
        cls._instance = None
        logger.info("AWSClients instance reset")
    
    @property
    def s3(self):
        """
        Get or create S3 client.
        
        Returns:
            boto3.client: S3 client
            
        Raises:
            AWSClientError: If client initialization fails
        """
        if self._s3 is None:
            try:
                self._s3 = boto3.client('s3', config=self.config)
                logger.info("S3 client initialized successfully")
            except (ClientError, BotoCoreError) as e:
                error_msg = f"Failed to initialize S3 client: {str(e)}"
                logger.error(error_msg)
                raise AWSClientError(error_msg) from e
        return self._s3
    
    @property
    def dynamodb(self):
        """
        Get or create DynamoDB resource.
        
        Returns:
            boto3.resource: DynamoDB resource
            
        Raises:
            AWSClientError: If resource initialization fails
        """
        if self._dynamodb is None:
            try:
                self._dynamodb = boto3.resource('dynamodb', config=self.config)
                logger.info("DynamoDB resource initialized successfully")
            except (ClientError, BotoCoreError) as e:
                error_msg = f"Failed to initialize DynamoDB resource: {str(e)}"
                logger.error(error_msg)
                raise AWSClientError(error_msg) from e
        return self._dynamodb
    
    @property
    def bedrock_runtime(self):
        """
        Get or create Bedrock Runtime client.
        
        Returns:
            boto3.client: Bedrock Runtime client
            
        Raises:
            AWSClientError: If client initialization fails
        """
        if self._bedrock_runtime is None:
            try:
                self._bedrock_runtime = boto3.client(
                    'bedrock-runtime',
                    config=self.config
                )
                logger.info("Bedrock Runtime client initialized successfully")
            except (ClientError, BotoCoreError) as e:
                error_msg = f"Failed to initialize Bedrock Runtime client: {str(e)}"
                logger.error(error_msg)
                raise AWSClientError(error_msg) from e
        return self._bedrock_runtime
    
    @property
    def secrets_manager(self):
        """
        Get or create Secrets Manager client.
        
        Returns:
            boto3.client: Secrets Manager client
            
        Raises:
            AWSClientError: If client initialization fails
        """
        if self._secrets_manager is None:
            try:
                self._secrets_manager = boto3.client(
                    'secretsmanager',
                    config=self.config
                )
                logger.info("Secrets Manager client initialized successfully")
            except (ClientError, BotoCoreError) as e:
                error_msg = f"Failed to initialize Secrets Manager client: {str(e)}"
                logger.error(error_msg)
                raise AWSClientError(error_msg) from e
        return self._secrets_manager
    
    def get_secret(self, secret_id: str) -> dict:
        """
        Retrieve a secret from AWS Secrets Manager.
        
        This is a convenience method that wraps the Secrets Manager client
        and handles common error cases.
        
        Args:
            secret_id: The ID or ARN of the secret to retrieve
            
        Returns:
            dict: The secret value as a dictionary
            
        Raises:
            AWSClientError: If secret retrieval fails
        """
        try:
            response = self.secrets_manager.get_secret_value(SecretId=secret_id)
            
            # Parse the secret string as JSON
            import json
            secret_string = response.get('SecretString')
            if secret_string:
                return json.loads(secret_string)
            else:
                # Binary secret
                return {'SecretBinary': response.get('SecretBinary')}
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = f"Failed to retrieve secret '{secret_id}': {error_code} - {str(e)}"
            logger.error(error_msg)
            raise AWSClientError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error retrieving secret '{secret_id}': {str(e)}"
            logger.error(error_msg)
            raise AWSClientError(error_msg) from e


# Convenience function for Lambda handlers
def get_aws_clients() -> AWSClients:
    """
    Get the singleton AWSClients instance.
    
    This is a convenience function for Lambda handlers to easily access
    AWS service clients.
    
    Returns:
        AWSClients: The singleton instance with initialized clients
        
    Example:
        >>> from common.aws_clients import get_aws_clients
        >>> clients = get_aws_clients()
        >>> s3 = clients.s3
        >>> dynamodb = clients.dynamodb
    """
    return AWSClients.get_instance()
