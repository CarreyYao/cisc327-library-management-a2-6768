"""
Unit tests for payment-related functions using stubbing techniques.
Tests for pay_late_fees() and refund_late_fee_payment() functions.
Using stubbing with mocker.patch() for database functions as required.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.library_service import (
    pay_late_fees, refund_late_fee_payment, calculate_late_fee_for_book,
    get_book_by_id
)

from services.payment_service import (
    PaymentGateway
)

""" ********************  Using Stubbing for Unit Testing  begin  ***********************  """

def test_pay_late_fees_successful_payment_with_stubbing():
    """
    Test successful late fee payment scenario.
    Stubs database functions using mocker.patch() to return valid test data.
    """
    # Test data setup
    test_patron_id = "123456"
    test_book_id = 1
    test_fee_amount = 10.50
    test_book_title = "Test Book Title"
    
    # Use mocker.patch() to stub database functions as required
    with patch('services.library_service.calculate_late_fee_for_book') as stub_calculate_fee, \
         patch('services.library_service.get_book_by_id') as stub_get_book, \
         patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        
        # Configure stubs to return test data without verification
        stub_calculate_fee.return_value = {
            'fee_amount': test_fee_amount,
            'days_overdue': 14,
            'status': 'Current late fee: $10.50 for 14 days overdue'
        }
        
        stub_get_book.return_value = {
            'id': test_book_id,
            'title': test_book_title,
            'author': 'Test Author',
            'isbn': '1234567890123',
            'total_copies': 5,
            'available_copies': 3
        }
        
        # Configure payment gateway mock
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        mock_gateway_instance.process_payment.return_value = (
            True, "txn_123456_789", "Payment processed successfully"
        )
        
        # Execute the function under test
        success, message, transaction_id = pay_late_fees(
            test_patron_id, test_book_id, mock_gateway_instance
        )
        
        # Verify successful payment results
        assert success is True
        assert transaction_id == "txn_123456_789"
        assert "successful" in message.lower()
        
        # Verify stubs were called with correct parameters
        stub_calculate_fee.assert_called_once_with(test_patron_id, test_book_id)
        stub_get_book.assert_called_once_with(test_book_id)


def test_pay_late_fees_payment_declined_by_gateway_with_stubbing():
    """
    Test payment declined by external gateway scenario.
    Stubs database functions using mocker.patch() and simulates gateway rejection.
    """
    test_patron_id = "123456"
    test_book_id = 2
    test_fee_amount = 25.00
    
    # Use mocker.patch() to stub database functions
    with patch('services.library_service.calculate_late_fee_for_book') as stub_calculate_fee, \
         patch('services.library_service.get_book_by_id') as stub_get_book, \
         patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        
        # Configure stubs with test data
        stub_calculate_fee.return_value = {
            'fee_amount': test_fee_amount,
            'days_overdue': 30,
            'status': 'Current late fee: $25.00 for 30 days overdue'
        }
        
        stub_get_book.return_value = {
            'id': test_book_id,
            'title': 'Declined Payment Book',
            'author': 'Test Author'
        }
        
        # Configure gateway to simulate decline
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        mock_gateway_instance.process_payment.return_value = (
            False, "", "Payment declined: amount exceeds limit"
        )
        
        # Execute function
        success, message, transaction_id = pay_late_fees(
            test_patron_id, test_book_id, mock_gateway_instance
        )
        
        # Verify payment decline scenario
        assert success is False
        assert transaction_id is None
        assert "declined" in message.lower() or "failed" in message.lower()


def test_pay_late_fees_invalid_patron_id_gateway_not_called_with_stubbing():
    """
    Test that payment gateway is NOT called when patron ID is invalid.
    Verifies early validation prevents external API calls.
    """
    invalid_patron_id = "123"  # Too short - invalid
    test_book_id = 3
    
    # Use mocker.patch() to stub database functions
    with patch('services.library_service.calculate_late_fee_for_book') as stub_calculate_fee, \
         patch('services.library_service.get_book_by_id') as stub_get_book, \
         patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        
        # Configure stubs (though they shouldn't be called due to early validation)
        stub_calculate_fee.return_value = {'fee_amount': 10.00}
        stub_get_book.return_value = {'title': 'Test Book'}
        
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        
        # Execute with invalid patron ID
        success, message, transaction_id = pay_late_fees(
            invalid_patron_id, test_book_id, mock_gateway_instance
        )
        
        # Verify failure due to invalid patron ID
        assert success is False
        assert "invalid patron id" in message.lower()
        assert transaction_id is None
        
        # Verify stubs and gateway were NOT called due to early validation
        stub_calculate_fee.assert_not_called()
        stub_get_book.assert_not_called()
        mock_gateway_instance.process_payment.assert_not_called()


def test_pay_late_fees_zero_late_fees_gateway_not_called_with_stubbing():
    """
    Test that payment gateway is NOT called when there are zero late fees.
    Verifies early return prevents unnecessary API calls.
    """
    test_patron_id = "123456"
    test_book_id = 4
    
    # Use mocker.patch() to stub database functions
    with patch('services.library_service.calculate_late_fee_for_book') as stub_calculate_fee, \
         patch('services.library_service.get_book_by_id') as stub_get_book, \
         patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        
        # Configure stub to return zero fees
        stub_calculate_fee.return_value = {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'No late fees - not yet due'
        }
        
        stub_get_book.return_value = {
            'id': test_book_id,
            'title': 'No Fee Book',
            'author': 'Test Author'
        }
        
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        
        # Execute function
        success, message, transaction_id = pay_late_fees(
            test_patron_id, test_book_id, mock_gateway_instance
        )
        
        # Verify no fees scenario
        assert success is False
        assert "no late fees" in message.lower()
        assert transaction_id is None
        
        # Verify stubs were called but gateway was NOT called
        stub_calculate_fee.assert_called_once_with(test_patron_id, test_book_id)
        stub_get_book.assert_not_called()  # Not called due to zero fees
        mock_gateway_instance.process_payment.assert_not_called()


def test_pay_late_fees_network_error_exception_handling_with_stubbing():
    """
    Test exception handling when payment gateway throws network error.
    Verifies graceful error handling and appropriate error messages.
    """
    test_patron_id = "123456"
    test_book_id = 5
    test_fee_amount = 8.50
    
    # Use mocker.patch() to stub database functions
    with patch('services.library_service.calculate_late_fee_for_book') as stub_calculate_fee, \
         patch('services.library_service.get_book_by_id') as stub_get_book, \
         patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        
        # Configure stubs with test data
        stub_calculate_fee.return_value = {
            'fee_amount': test_fee_amount,
            'days_overdue': 10,
            'status': 'Current late fee: $8.50 for 10 days overdue'
        }
        
        stub_get_book.return_value = {
            'id': test_book_id,
            'title': 'Network Error Book',
            'author': 'Test Author'
        }
        
        # Configure gateway to simulate network exception
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        mock_gateway_instance.process_payment.side_effect = Exception(
            "Network connection timeout"
        )
        
        # Execute function
        success, message, transaction_id = pay_late_fees(
            test_patron_id, test_book_id, mock_gateway_instance
        )
        
        # Verify exception handling
        assert success is False
        assert transaction_id is None
        assert "error" in message.lower()
        assert "network" in message.lower() or "processing" in message.lower()


def test_refund_late_fee_payment_successful_refund_with_stubbing():
    """
    Test successful refund scenario.
    Uses mocker.patch() for the payment gateway dependency.
    """
    test_transaction_id = "txn_123456_789"
    test_refund_amount = 10.50
    
    # Use mocker.patch() for payment gateway
    with patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        # Configure mock gateway instance
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        mock_gateway_instance.refund_payment.return_value = (
            True, "Refund of $10.50 processed successfully. Refund ID: refund_txn_123456_789_123"
        )
        
        # Execute refund function
        success, message = refund_late_fee_payment(
            test_transaction_id, test_refund_amount, mock_gateway_instance
        )
        
        # Verify successful refund
        assert success is True
        assert "successfully" in message.lower()
        assert str(test_refund_amount) in message


def test_refund_late_fee_payment_invalid_transaction_id_rejection_with_stubbing():
    """
    Test rejection of refund with invalid transaction ID.
    Verifies proper validation before calling external gateway.
    """
    invalid_transaction_id = "invalid_txn_123"  # Doesn't start with "txn_"
    test_refund_amount = 10.50
    
    # Use mocker.patch() for payment gateway
    with patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        
        # Execute with invalid transaction ID
        success, message = refund_late_fee_payment(
            invalid_transaction_id, test_refund_amount, mock_gateway_instance
        )
        
        # Verify rejection due to invalid transaction ID
        assert success is False
        assert "invalid transaction id" in message.lower()
        
        # Verify gateway was NOT called due to validation
        mock_gateway_instance.refund_payment.assert_not_called()


def test_refund_late_fee_payment_negative_refund_amount_rejection():
    """
    Test rejection of refund with negative amount.
    Verifies amount validation logic.
    """
    test_transaction_id = "txn_123456_789"
    negative_amount = -5.00
    
    # Use mocker.patch() for payment gateway
    with patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        
        # Execute with negative amount
        success, message = refund_late_fee_payment(
            test_transaction_id, negative_amount, mock_gateway_instance
        )
        
        # Verify rejection due to negative amount
        assert success is False
        assert "must be greater than 0" in message.lower()
        
        # Verify gateway was NOT called
        mock_gateway_instance.refund_payment.assert_not_called()


def test_refund_late_fee_payment_zero_refund_amount_rejection_with_stubbing():
    """
    Test rejection of refund with zero amount.
    Verifies amount validation logic.
    """
    test_transaction_id = "txn_123456_789"
    zero_amount = 0.00
    
    # Use mocker.patch() for payment gateway
    with patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        
        # Execute with zero amount
        success, message = refund_late_fee_payment(
            test_transaction_id, zero_amount, mock_gateway_instance
        )
        
        # Verify rejection due to zero amount
        assert success is False
        assert "must be greater than 0" in message.lower()
        
        # Verify gateway was NOT called
        mock_gateway_instance.refund_payment.assert_not_called()


def test_refund_late_fee_payment_exceeds_maximum_amount_rejection_with_stubbing():
    """
    Test rejection of refund when amount exceeds $15 maximum.
    Verifies maximum amount validation logic.
    """
    test_transaction_id = "txn_123456_789"
    exceeds_max_amount = 20.00  # Exceeds $15 maximum
    
    # Use mocker.patch() for payment gateway
    with patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        
        # Execute with amount exceeding maximum
        success, message = refund_late_fee_payment(
            test_transaction_id, exceeds_max_amount, mock_gateway_instance
        )
        
        # Verify rejection due to amount exceeding maximum
        assert success is False
        assert "exceeds maximum late fee" in message.lower()
        
        # Verify gateway was NOT called
        mock_gateway_instance.refund_payment.assert_not_called()


def test_refund_late_fee_payment_boundary_amount_success_with_stubbing():
    """
    Test successful refund with boundary amount ($15.00 maximum).
    Verifies that maximum allowed amount is accepted.
    """
    test_transaction_id = "txn_123456_789"
    boundary_amount = 15.00  # Maximum allowed amount
    
    # Use mocker.patch() for payment gateway
    with patch('services.payment_service.PaymentGateway') as mock_gateway_class:
        mock_gateway_instance = MagicMock()
        mock_gateway_class.return_value = mock_gateway_instance
        mock_gateway_instance.refund_payment.return_value = (
            True, f"Refund of ${boundary_amount:.2f} processed successfully"
        )
        
        # Execute with boundary amount
        success, message = refund_late_fee_payment(
            test_transaction_id, boundary_amount, mock_gateway_instance
        )
        
        # Verify successful refund with boundary amount
        assert success is True
        assert "successfully" in message.lower()
        assert str(boundary_amount) in message
        
""" ********************  Using Stubbing for Unit Testing  end  ***********************  """



""" ********************  Using Mocking for Unit Testing  being  ***********************  """

def test_pay_late_fees_successful_payment_with_mock_verification():
    """
    Test successful late fee payment with mock verification.
    Uses Mock(spec=PaymentGateway) and verifies correct parameter passing.
    """
    # Test data setup
    test_patron_id = "123456"
    test_book_id = 1
    test_fee_amount = 10.50
    test_book_title = "Test Book Title"
    
    # Create mock payment gateway with spec verification
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (
        True, "txn_123456_789", "Payment processed successfully"
    )
    
    # Mock database functions to return test data
    with patch('services.library_service.calculate_late_fee_for_book') as mock_calculate_fee, \
         patch('services.library_service.get_book_by_id') as mock_get_book:
        
        # Configure mock return values
        mock_calculate_fee.return_value = {
            'fee_amount': test_fee_amount,
            'days_overdue': 14,
            'status': 'Current late fee: $10.50 for 14 days overdue'
        }
        
        mock_get_book.return_value = {
            'id': test_book_id,
            'title': test_book_title,
            'author': 'Test Author'
        }
        
        # Execute the function under test
        success, message, transaction_id = pay_late_fees(
            test_patron_id, test_book_id, mock_gateway
        )
        
        # Verify successful payment results
        assert success is True
        assert transaction_id == "txn_123456_789"
        assert "successful" in message.lower()
        
        # MOCK VERIFICATION: Verify payment gateway was called with correct parameters
        mock_gateway.process_payment.assert_called_once()
        mock_gateway.process_payment.assert_called_with(
            patron_id=test_patron_id,
            amount=test_fee_amount,
            description=f"Late fees for '{test_book_title}'"
        )


def test_pay_late_fees_payment_declined_with_mock_verification():
    """
    Test payment declined scenario with mock verification.
    Verifies gateway interaction when payment is declined.
    """
    test_patron_id = "123456"
    test_book_id = 2
    test_fee_amount = 25.00
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (
        False, "", "Payment declined: amount exceeds limit"
    )
    
    with patch('services.library_service.calculate_late_fee_for_book') as mock_calculate_fee, \
         patch('services.library_service.get_book_by_id') as mock_get_book:
        
        # Configure mock return values
        mock_calculate_fee.return_value = {
            'fee_amount': test_fee_amount,
            'days_overdue': 30,
            'status': 'Current late fee: $25.00 for 30 days overdue'
        }
        
        mock_get_book.return_value = {
            'id': test_book_id,
            'title': 'Declined Payment Book',
            'author': 'Test Author'
        }
        
        # Execute function
        success, message, transaction_id = pay_late_fees(
            test_patron_id, test_book_id, mock_gateway
        )
        
        # Verify payment decline scenario
        assert success is False
        assert transaction_id is None
        assert "declined" in message.lower() or "failed" in message.lower()
        
        # MOCK VERIFICATION: Verify gateway was called despite decline
        mock_gateway.process_payment.assert_called_once()
        mock_gateway.process_payment.assert_called_with(
            patron_id=test_patron_id,
            amount=test_fee_amount,
            description="Late fees for 'Declined Payment Book'"
        )


def test_pay_late_fees_invalid_patron_id_mock_not_called():
    """
    Test that payment gateway mock is NOT called when patron ID is invalid.
    Demonstrates mock verification for negative test cases.
    """
    invalid_patron_id = "123"  # Too short - invalid
    test_book_id = 3
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute with invalid patron ID
    success, message, transaction_id = pay_late_fees(
        invalid_patron_id, test_book_id, mock_gateway
    )
    
    # Verify failure due to invalid patron ID
    assert success is False
    assert "invalid patron id" in message.lower()
    assert transaction_id is None
    
    # MOCK VERIFICATION: Critical assertion - verify mock was NOT called
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_late_fees_mock_not_called():
    """
    Test that payment gateway mock is NOT called when there are zero late fees.
    Verifies early return prevents unnecessary API calls.
    """
    test_patron_id = "123456"
    test_book_id = 4
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    
    with patch('services.library_service.calculate_late_fee_for_book') as mock_calculate_fee:
        
        # Configure mock to return zero fees
        mock_calculate_fee.return_value = {
            'fee_amount': 0.00,
            'days_overdue': 0,
            'status': 'No late fees - not yet due'
        }
        
        # Execute function
        success, message, transaction_id = pay_late_fees(
            test_patron_id, test_book_id, mock_gateway
        )
        
        # Verify no fees scenario
        assert success is False
        assert "no late fees" in message.lower()
        assert transaction_id is None
        
        # MOCK VERIFICATION: Verify payment gateway was NOT called
        mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_network_error_exception_handling_with_mock():
    """
    Test exception handling with mock verification.
    Verifies gateway interaction when network error occurs.
    """
    test_patron_id = "123456"
    test_book_id = 5
    test_fee_amount = 8.50
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Network connection timeout")
    
    with patch('services.library_service.calculate_late_fee_for_book') as mock_calculate_fee, \
         patch('services.library_service.get_book_by_id') as mock_get_book:
        
        # Configure mock return values
        mock_calculate_fee.return_value = {
            'fee_amount': test_fee_amount,
            'days_overdue': 10,
            'status': 'Current late fee: $8.50 for 10 days overdue'
        }
        
        mock_get_book.return_value = {
            'id': test_book_id,
            'title': 'Network Error Book',
            'author': 'Test Author'
        }
        
        # Execute function
        success, message, transaction_id = pay_late_fees(
            test_patron_id, test_book_id, mock_gateway
        )
        
        # Verify exception handling
        assert success is False
        assert transaction_id is None
        assert "error" in message.lower()
        
        # MOCK VERIFICATION: Verify gateway was called before exception
        mock_gateway.process_payment.assert_called_once()


def test_refund_late_fee_payment_successful_refund_with_mock_verification():
    """
    Test successful refund scenario with mock verification.
    Verifies correct parameter passing to refund_payment method.
    """
    test_transaction_id = "txn_123456_789"
    test_refund_amount = 10.50
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (
        True, "Refund of $10.50 processed successfully. Refund ID: refund_txn_123456_789_123"
    )
    
    # Execute refund function
    success, message = refund_late_fee_payment(
        test_transaction_id, test_refund_amount, mock_gateway
    )
    
    # Verify successful refund
    assert success is True
    assert "successfully" in message.lower()
    assert str(test_refund_amount) in message
    
    # MOCK VERIFICATION: Verify refund was called with correct parameters
    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_with(test_transaction_id, test_refund_amount)


def test_refund_late_fee_payment_invalid_transaction_id_mock_not_called():
    """
    Test that refund mock is NOT called when transaction ID is invalid.
    Verifies validation prevents unnecessary API calls.
    """
    invalid_transaction_id = "invalid_txn_123"  # Doesn't start with "txn_"
    test_refund_amount = 10.50
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute with invalid transaction ID
    success, message = refund_late_fee_payment(
        invalid_transaction_id, test_refund_amount, mock_gateway
    )
    
    # Verify rejection due to invalid transaction ID
    assert success is False
    assert "invalid transaction id" in message.lower()
    
    # MOCK VERIFICATION: Verify refund method was NOT called
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_negative_amount_mock_not_called():
    """
    Test that refund mock is NOT called when amount is negative.
    Verifies amount validation logic.
    """
    test_transaction_id = "txn_123456_789"
    negative_amount = -5.00
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute with negative amount
    success, message = refund_late_fee_payment(
        test_transaction_id, negative_amount, mock_gateway
    )
    
    # Verify rejection due to negative amount
    assert success is False
    assert "must be greater than 0" in message.lower()
    
    # MOCK VERIFICATION: Verify refund method was NOT called
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_zero_amount_mock_not_called():
    """
    Test that refund mock is NOT called when amount is zero.
    Verifies amount validation logic.
    """
    test_transaction_id = "txn_123456_789"
    zero_amount = 0.00
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute with zero amount
    success, message = refund_late_fee_payment(
        test_transaction_id, zero_amount, mock_gateway
    )
    
    # Verify rejection due to zero amount
    assert success is False
    assert "must be greater than 0" in message.lower()
    
    # MOCK VERIFICATION: Verify refund method was NOT called
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_exceeds_maximum_amount_mock_not_called():
    """
    Test that refund mock is NOT called when amount exceeds $15 maximum.
    Verifies maximum amount validation.
    """
    test_transaction_id = "txn_123456_789"
    exceeds_max_amount = 20.00  # Exceeds $15 maximum
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    
    # Execute with amount exceeding maximum
    success, message = refund_late_fee_payment(
        test_transaction_id, exceeds_max_amount, mock_gateway
    )
    
    # Verify rejection due to amount exceeding maximum
    assert success is False
    assert "exceeds maximum late fee" in message.lower()
    
    # MOCK VERIFICATION: Verify refund method was NOT called
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_boundary_amount_success_with_mock():
    """
    Test successful refund with boundary amount ($15.00 maximum).
    Verifies that maximum allowed amount is accepted and mock is called correctly.
    """
    test_transaction_id = "txn_123456_789"
    boundary_amount = 15.00  # Maximum allowed amount
    
    # Create mock payment gateway with spec
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (
        True, f"Refund of ${boundary_amount:.2f} processed successfully"
    )
    
    # Execute with boundary amount
    success, message = refund_late_fee_payment(
        test_transaction_id, boundary_amount, mock_gateway
    )
    
    # Verify successful refund with boundary amount
    assert success is True
    assert "successfully" in message.lower()
    assert str(boundary_amount) in message
    
    # MOCK VERIFICATION: Verify refund was called with boundary amount
    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_with(test_transaction_id, boundary_amount)


def test_refund_late_fee_payment_gateway_error_handling():
    """
    Test error handling when payment gateway returns failure.
    Verifies mock interaction and error propagation.
    """
    test_transaction_id = "txn_123456_789"
    test_refund_amount = 12.50
    
    # Create mock payment gateway with spec that returns error
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (
        False, "Refund failed: transaction not found"
    )
    
    # Execute refund function
    success, message = refund_late_fee_payment(
        test_transaction_id, test_refund_amount, mock_gateway
    )
    
    # Verify refund failure scenario
    assert success is False
    assert "failed" in message.lower()
    
    # MOCK VERIFICATION: Verify refund was called despite failure
    mock_gateway.refund_payment.assert_called_once()
    mock_gateway.refund_payment.assert_called_with(test_transaction_id, test_refund_amount)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])

""" ********************  Using Mocking for Unit Testing  end  ***********************  """

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
