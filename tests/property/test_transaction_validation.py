"""
Property-based tests for Transaction data model validation.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

This module tests the Transaction model validation logic using property-based testing
with Hypothesis to ensure data integrity across a wide range of inputs.
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, assume, settings
from src.common.models import Transaction


# Custom strategies for Transaction fields
@st.composite
def valid_transaction_id(draw):
    """Generate valid non-empty transaction IDs."""
    return draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters=['\x00', '\n'])))


@st.composite
def valid_account_id(draw):
    """Generate valid non-empty account IDs."""
    return draw(st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_characters=['\x00', '\n'])))


@st.composite
def valid_currency(draw):
    """Generate valid cryptocurrency codes."""
    currencies = ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'DOGE']
    return draw(st.sampled_from(currencies))


@st.composite
def valid_transaction_type(draw):
    """Generate valid transaction types."""
    return draw(st.sampled_from(['deposit', 'withdrawal', 'transfer']))


@st.composite
def valid_status(draw):
    """Generate valid transaction statuses."""
    return draw(st.sampled_from(['completed', 'pending', 'failed']))


@st.composite
def valid_datetime(draw):
    """Generate valid datetime objects."""
    # Generate datetime within reasonable range (last 5 years to now)
    days_ago = draw(st.integers(min_value=0, max_value=1825))
    return datetime.now() - timedelta(days=days_ago)


@st.composite
def valid_transaction(draw):
    """Generate valid Transaction objects."""
    return Transaction(
        transaction_id=draw(valid_transaction_id()),
        timestamp=draw(valid_datetime()),
        from_account=draw(valid_account_id()),
        to_account=draw(valid_account_id()),
        amount=draw(st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False)),
        currency=draw(valid_currency()),
        transaction_type=draw(valid_transaction_type()),
        status=draw(valid_status()),
        fee=draw(st.floats(min_value=0.0, max_value=10000, allow_nan=False, allow_infinity=False)),
        metadata=draw(st.none() | st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=100)))
    )


class TestTransactionValidation:
    """
    Property-based tests for Transaction model validation.
    
    **Property 1: Transaction validation ensures positive amounts and valid fields**
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
    """
    
    @settings(max_examples=10)
    @given(valid_transaction())
    def test_valid_transactions_are_accepted(self, transaction):
        """
        Property: All transactions with valid fields should be accepted.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        # If we can create the transaction without exception, it's valid
        assert transaction.transaction_id
        assert isinstance(transaction.timestamp, datetime)
        assert transaction.amount > 0
        assert transaction.from_account
        assert transaction.to_account
        assert transaction.currency
        assert transaction.transaction_type in ['deposit', 'withdrawal', 'transfer']
        assert transaction.status in ['completed', 'pending', 'failed']
        assert transaction.fee >= 0
    
    @settings(max_examples=10)
    @given(
        st.text(max_size=0),  # Empty transaction_id
        valid_datetime(),
        valid_account_id(),
        valid_account_id(),
        st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
        valid_currency(),
        valid_transaction_type(),
        valid_status(),
        st.floats(min_value=0.0, max_value=10000, allow_nan=False, allow_infinity=False)
    )
    def test_empty_transaction_id_raises_error(self, transaction_id, timestamp, from_account, 
                                                to_account, amount, currency, transaction_type, 
                                                status, fee):
        """
        Property: Transactions with empty transaction_id should raise ValueError.
        
        **Validates: Requirements 2.1**
        """
        with pytest.raises(ValueError, match="transaction_id cannot be empty"):
            Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                status=status,
                fee=fee
            )
    
    @settings(max_examples=10)
    @given(
        valid_transaction_id(),
        st.text(),  # Invalid timestamp (not datetime)
        valid_account_id(),
        valid_account_id(),
        st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
        valid_currency(),
        valid_transaction_type(),
        valid_status(),
        st.floats(min_value=0.0, max_value=10000, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_timestamp_raises_error(self, transaction_id, timestamp, from_account, 
                                           to_account, amount, currency, transaction_type, 
                                           status, fee):
        """
        Property: Transactions with non-datetime timestamp should raise ValueError.
        
        **Validates: Requirements 2.2**
        """
        with pytest.raises(ValueError, match="timestamp must be a datetime object"):
            Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                status=status,
                fee=fee
            )
    
    @settings(max_examples=10)
    @given(
        valid_transaction_id(),
        valid_datetime(),
        valid_account_id(),
        valid_account_id(),
        st.floats(max_value=0.0, allow_nan=False, allow_infinity=False),  # Non-positive amount
        valid_currency(),
        valid_transaction_type(),
        valid_status(),
        st.floats(min_value=0.0, max_value=10000, allow_nan=False, allow_infinity=False)
    )
    def test_non_positive_amount_raises_error(self, transaction_id, timestamp, from_account, 
                                              to_account, amount, currency, transaction_type, 
                                              status, fee):
        """
        Property: Transactions with non-positive amounts should raise ValueError.
        
        **Validates: Requirements 2.3**
        """
        with pytest.raises(ValueError, match="amount must be positive"):
            Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                status=status,
                fee=fee
            )
    
    @settings(max_examples=10)
    @given(
        valid_transaction_id(),
        valid_datetime(),
        st.text(max_size=0),  # Empty from_account
        valid_account_id(),
        st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
        valid_currency(),
        valid_transaction_type(),
        valid_status(),
        st.floats(min_value=0.0, max_value=10000, allow_nan=False, allow_infinity=False)
    )
    def test_empty_from_account_raises_error(self, transaction_id, timestamp, from_account, 
                                            to_account, amount, currency, transaction_type, 
                                            status, fee):
        """
        Property: Transactions with empty from_account should raise ValueError.
        
        **Validates: Requirements 2.4**
        """
        with pytest.raises(ValueError, match="from_account cannot be empty"):
            Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                status=status,
                fee=fee
            )
    
    @settings(max_examples=10)
    @given(
        valid_transaction_id(),
        valid_datetime(),
        valid_account_id(),
        st.text(max_size=0),  # Empty to_account
        st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
        valid_currency(),
        valid_transaction_type(),
        valid_status(),
        st.floats(min_value=0.0, max_value=10000, allow_nan=False, allow_infinity=False)
    )
    def test_empty_to_account_raises_error(self, transaction_id, timestamp, from_account, 
                                          to_account, amount, currency, transaction_type, 
                                          status, fee):
        """
        Property: Transactions with empty to_account should raise ValueError.
        
        **Validates: Requirements 2.4**
        """
        with pytest.raises(ValueError, match="to_account cannot be empty"):
            Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                status=status,
                fee=fee
            )
    
    @settings(max_examples=10)
    @given(
        valid_transaction_id(),
        valid_datetime(),
        valid_account_id(),
        valid_account_id(),
        st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
        st.text(max_size=0),  # Empty currency
        valid_transaction_type(),
        valid_status(),
        st.floats(min_value=0.0, max_value=10000, allow_nan=False, allow_infinity=False)
    )
    def test_empty_currency_raises_error(self, transaction_id, timestamp, from_account, 
                                        to_account, amount, currency, transaction_type, 
                                        status, fee):
        """
        Property: Transactions with empty currency should raise ValueError.
        
        **Validates: Requirements 2.5**
        """
        with pytest.raises(ValueError, match="currency cannot be empty"):
            Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                status=status,
                fee=fee
            )
    
    @settings(max_examples=10)
    @given(
        valid_transaction_id(),
        valid_datetime(),
        valid_account_id(),
        valid_account_id(),
        st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
        valid_currency(),
        st.text(min_size=1).filter(lambda x: x not in ['deposit', 'withdrawal', 'transfer']),  # Invalid type
        valid_status(),
        st.floats(min_value=0.0, max_value=10000, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_transaction_type_raises_error(self, transaction_id, timestamp, from_account, 
                                                   to_account, amount, currency, transaction_type, 
                                                   status, fee):
        """
        Property: Transactions with invalid transaction_type should raise ValueError.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        with pytest.raises(ValueError, match="transaction_type must be one of"):
            Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                status=status,
                fee=fee
            )
    
    @settings(max_examples=10)
    @given(
        valid_transaction_id(),
        valid_datetime(),
        valid_account_id(),
        valid_account_id(),
        st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
        valid_currency(),
        valid_transaction_type(),
        st.text(min_size=1).filter(lambda x: x not in ['completed', 'pending', 'failed']),  # Invalid status
        st.floats(min_value=0.0, max_value=10000, allow_nan=False, allow_infinity=False)
    )
    def test_invalid_status_raises_error(self, transaction_id, timestamp, from_account, 
                                        to_account, amount, currency, transaction_type, 
                                        status, fee):
        """
        Property: Transactions with invalid status should raise ValueError.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        with pytest.raises(ValueError, match="status must be one of"):
            Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                status=status,
                fee=fee
            )
    
    @settings(max_examples=10)
    @given(
        valid_transaction_id(),
        valid_datetime(),
        valid_account_id(),
        valid_account_id(),
        st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
        valid_currency(),
        valid_transaction_type(),
        valid_status(),
        st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False)  # Negative fee
    )
    def test_negative_fee_raises_error(self, transaction_id, timestamp, from_account, 
                                      to_account, amount, currency, transaction_type, 
                                      status, fee):
        """
        Property: Transactions with negative fees should raise ValueError.
        
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        with pytest.raises(ValueError, match="fee cannot be negative"):
            Transaction(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                status=status,
                fee=fee
            )
