import pytest
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory

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


@pytest.mark.django_db
def test_loan_serializer_assigns_user():
    """
    Verifica se o LoanSerializer atribui automaticamente o usuário correto para um usuário comum.
    """
    factory = APIRequestFactory()
    user = User.objects.create(username="testuser", password="password")
    request = factory.post('/api/loans/', {})
    request.user = user

    loan_data = {
        "nominal_value": Decimal('1000.00'),
        "interest_rate": Decimal('5.00'),
        "bank": "Test Bank",
        "client": "Test Client",
        "ip_address": "127.0.0.1"
    }

    serializer = LoanSerializer(data=loan_data, context={'request': request})
    
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['user'] == user


@pytest.mark.django_db
def test_loan_serializer_superuser_does_not_override_user():
    """
    Verifica se o LoanSerializer não sobrescreve o campo 'user' para um superusuário.
    """
    factory = APIRequestFactory()
    superuser = User.objects.create(username="superuser", password="password", is_superuser=True)
    request = factory.post('/api/loans/', {})
    request.user = superuser
    
    loan_data = {
        "nominal_value": Decimal('1000.00'),
        "interest_rate": Decimal('5.00'),
        "bank": "Test Bank",
        "client": "Test Client",
        "ip_address": "127.0.0.1"
    }

    serializer = LoanSerializer(data=loan_data, context={'request': request})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data.get('user') is None


@pytest.mark.django_db
def test_loan_serializer_missing_required_fields():
    """
    Verifica se o LoanSerializer valida corretamente os campos obrigatórios.
    """
    factory = APIRequestFactory()
    user = User.objects.create(username="testuser", password="password")
    request = factory.post('/api/loans/', {})
    request.user = user

    loan_data = {
        "interest_rate": Decimal('5.00'),
        "bank": "Test Bank",
        "client": "Test Client",
        "ip_address": "127.0.0.1"
    }

    serializer = LoanSerializer(data=loan_data, context={'request': request})
    
    assert not serializer.is_valid()
    assert 'nominal_value' in serializer.errors


@pytest.mark.django_db
def test_payment_serializer_validations():
    """
    Verifica a criação de um pagamento inválido, como um pagamento sem valor ou com valor negativo.
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

    invalid_payment_data = {
        "loan": loan.id,
        "amount": Decimal('-100.00')
    }
    serializer = PaymentSerializer(data=invalid_payment_data)
    assert not serializer.is_valid()
    assert 'amount' in serializer.errors
    assert serializer.errors['amount'][0] == "The payment amount must be positive."

    zero_payment_data = {
        "loan": loan.id,
        "amount": Decimal('0.00')
    }
    serializer = PaymentSerializer(data=zero_payment_data)
    assert not serializer.is_valid()
    assert 'amount' in serializer.errors
    assert serializer.errors['amount'][0] == "The payment amount must be positive."