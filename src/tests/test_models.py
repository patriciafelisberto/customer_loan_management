import pytest
from datetime import date
from decimal import Decimal
from django.contrib.auth.models import User

from loans.models import Loan, Payment


@pytest.mark.django_db
def test_loan_creation():
    """
    Testa a criação de um empréstimo e se os valores são salvos corretamente.
    """
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
    """
    Testa o cálculo do saldo devedor com um pagamento.
    """
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
    assert balance < loan.nominal_value


@pytest.mark.django_db
def test_outstanding_balance_with_multiple_payments():
    """
    Testa o cálculo do saldo devedor com múltiplos pagamentos.
    """
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
    Payment.objects.create(loan=loan, amount=Decimal('300.00'))
    
    balance = loan.outstanding_balance
    assert balance == Decimal('500.00')


@pytest.mark.django_db
def test_loan_soft_delete():
    """
    Testa o soft delete de um empréstimo.
    """
    user = User.objects.create(username="testuser", password="password")
    loan = Loan.objects.create(
        nominal_value=Decimal('1000.00'),
        interest_rate=Decimal('5.00'),
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user
    )
    
    loan.delete()
    
    assert loan.deleted_at is not None
    assert Loan.objects.alive().count() == 0
    assert Loan.objects.dead().count() == 1


@pytest.mark.django_db
def test_loan_restore():
    """
    Testa a restauração de um empréstimo que foi soft deleted.
    """
    user = User.objects.create(username="testuser", password="password")
    loan = Loan.objects.create(
        nominal_value=Decimal('1000.00'),
        interest_rate=Decimal('5.00'),
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user
    )
    
    loan.delete()
    assert loan.deleted_at is not None

    loan.restore()
    
    assert loan.deleted_at is None
    assert Loan.objects.alive().count() == 1
    assert Loan.objects.dead().count() == 0


@pytest.mark.django_db
def test_payment_creation():
    """
    Testa a criação de um pagamento e se ele está corretamente associado a um empréstimo.
    """
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
    
    assert payment.amount == Decimal('200.00')
    assert payment.loan == loan
    assert Payment.objects.count() == 1
