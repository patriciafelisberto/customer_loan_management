import pytest
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User

from loans.models import Loan, Payment
from loans.serializers import LoanSerializer, PaymentSerializer


@pytest.mark.django_db
def test_loan_serializer():
    user = User.objects.create(username="testuser", password="password")
    loan = Loan.objects.create(
        nominal_value=Decimal('1000.00'),
        interest_rate=Decimal('5.00'),
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user,
        request_date=date.today()
    )
    serializer = LoanSerializer(loan)
    data = serializer.data
    assert data["nominal_value"] == "1000.00"
    assert data["interest_rate"] == "5.00"
    assert "outstanding_balance" in data

@pytest.mark.django_db
def test_payment_serializer():
    user = User.objects.create(username="testuser", password="password")
    loan = Loan.objects.create(
        nominal_value=Decimal('1000.00'),
        interest_rate=Decimal('5.00'),
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user
    )
    payment = Payment.objects.create(loan=loan, amount=Decimal('200.00'))
    serializer = PaymentSerializer(payment)
    data = serializer.data
    assert data["amount"] == "200.00"
    assert str(data["loan"]) == str(loan.id)