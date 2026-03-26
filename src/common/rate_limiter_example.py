"""
Example usage of RateLimiter class for Bedrock API calls.

This example demonstrates how to use the RateLimiter to ensure
compliance with Bedrock API rate limits (< 1 request/second).
"""

import json
from src.common.rate_limiter import RateLimiter


def analyze_accounts_with_bedrock(account_features, bedrock_client):
    """
    Analyze multiple accounts using Bedrock API with rate limiting.
    
    Args:
        account_features: Dictionary mapping account_id to features
        bedrock_client: Boto3 Bedrock client
    
    Returns:
        List of risk assessments
    """
    # Initialize rate limiter with max 0.9 requests/second (< 1 req/sec)
    rate_limiter = RateLimiter(max_requests_per_second=0.9)
    
    risk_assessments = []
    
    for account_id, features in account_features.items():
        # Wait if needed to maintain rate limit
        rate_limiter.wait_if_needed()
        
        # Build prompt for Bedrock
        prompt = build_risk_analysis_prompt(features)
        
        # Call Bedrock API
        try:
            response = bedrock_client.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            llm_output = response_body['content'][0]['text']
            
            # Store assessment
            risk_assessments.append({
                "account_id": account_id,
                "assessment": llm_output
            })
            
        except Exception as e:
            print(f"Error analyzing account {account_id}: {e}")
            # Use fallback scoring if Bedrock fails
            continue
    
    # Log total requests made
    print(f"Total Bedrock API calls: {rate_limiter.get_request_count()}")
    
    return risk_assessments


def build_risk_analysis_prompt(features):
    """Build prompt for Bedrock risk analysis."""
    return f"""
    Analyze the following cryptocurrency account for suspicious activity:
    
    - Total Volume: ${features.get('total_volume', 0):,.2f}
    - Transaction Count: {features.get('transaction_count', 0)}
    - Night Transaction Ratio: {features.get('night_transaction_ratio', 0):.2%}
    - Round Number Ratio: {features.get('round_number_ratio', 0):.2%}
    
    Provide a risk score (0-100) and explanation.
    """


def example_with_retry_logic():
    """
    Example showing rate limiter with retry logic.
    
    This demonstrates how to use the rate limiter when implementing
    retry logic for failed API calls.
    """
    rate_limiter = RateLimiter(max_requests_per_second=0.9)
    
    max_retries = 3
    account_id = "account_123"
    
    for attempt in range(max_retries):
        # Wait to maintain rate limit (even for retries)
        rate_limiter.wait_if_needed()
        
        try:
            # Attempt API call
            result = call_bedrock_api(account_id)
            print(f"Success on attempt {attempt + 1}")
            return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("All retries exhausted")
                raise
    
    print(f"Total API calls (including retries): {rate_limiter.get_request_count()}")


def call_bedrock_api(account_id):
    """Placeholder for actual Bedrock API call."""
    # This would be replaced with actual Bedrock API call
    pass


if __name__ == "__main__":
    # Example: Create rate limiter
    limiter = RateLimiter(max_requests_per_second=0.9)
    
    print("Rate Limiter Configuration:")
    print(f"  Max RPS: {limiter.max_rps}")
    print(f"  Min Interval: {limiter.min_interval:.3f}s")
    print(f"  Initial Request Count: {limiter.get_request_count()}")
    
    # Simulate 3 API calls
    print("\nSimulating 3 API calls...")
    for i in range(3):
        limiter.wait_if_needed()
        print(f"  API call #{i + 1} completed")
    
    print(f"\nFinal Request Count: {limiter.get_request_count()}")
