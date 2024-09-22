import pytest
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User

from loans.models import Loan, Payment


@pytest.mark.django_db
def test_loan_creation():
    user = User.objects.create(username="testuser", password="password")
    loan = Loan.objects.create(
        nominal_value=Decimal('1000.00'),
        interest_rate=Decimal('5.00'),
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user
    )
    
    assert loan.nominal_value == Decimal('1000.00')
    assert loan.interest_rate == Decimal('5.00')
    assert loan.user == user

@pytest.mark.django_db
def test_outstanding_balance():
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
    Payment.objects.create(loan=loan, amount=Decimal('200.00'))
    balance = loan.outstanding_balance
    assert balance > Decimal('0.00')
