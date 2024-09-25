import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from loans.models import Loan


@pytest.mark.django_db
def test_create_loan():
    """
    Testa a criação de um novo empréstimo para um usuário autenticado.
    """
    client = APIClient()
    user = User.objects.create_user(username="testuser", password="password")
    client.force_authenticate(user=user)

    loan_data = {
        "nominal_value": 1000,
        "interest_rate": 5,
        "bank": "Test Bank",
        "client": "Test Client",
        "ip_address": "127.0.0.1"
    }

    response = client.post("/api/loans/", loan_data, format="json")

    assert response.status_code == 201
    assert response.data['nominal_value'] == '1000.00'
    assert response.data['interest_rate'] == '5.00'
    assert response.data['user'] == user.id


@pytest.mark.django_db
def test_delete_loan_authenticated():
    """
    Testa a exclusão de um empréstimo por um usuário autenticado (soft delete).
    """
    client = APIClient()
    user = User.objects.create_user(username="testuser", password="password")
    client.force_authenticate(user=user)

    loan = Loan.objects.create(
        nominal_value=1000,
        interest_rate=5,
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user
    )

    response = client.delete(f"/api/loans/{loan.id}/")
    assert response.status_code == 204

    loan.refresh_from_db()
    assert loan.deleted_at is not None


@pytest.mark.django_db
def test_delete_loan_unauthorized():
    """
    Testa a exclusão de um empréstimo por um usuário sem permissões.
    """
    client = APIClient()
    user1 = User.objects.create_user(username="testuser1", password="password")
    user2 = User.objects.create_user(username="testuser2", password="password")

    loan = Loan.objects.create(
        nominal_value=1000,
        interest_rate=5,
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user1
    )

    client.force_authenticate(user=user2)
    response = client.delete(f"/api/loans/{loan.id}/")
    
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_payment_for_loan():
    """
    Testa a criação de um pagamento para um empréstimo.
    """
    client = APIClient()
    user = User.objects.create_user(username="testuser", password="password")
    client.force_authenticate(user=user)

    loan = Loan.objects.create(
        nominal_value=1000,
        interest_rate=5,
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user
    )

    payment_data = {
        "loan": loan.id,
        "amount": 200
    }

    response = client.post("/api/payments/", payment_data, format="json")
    assert response.status_code == 201
    assert response.data['amount'] == '200.00'


@pytest.mark.django_db
def test_create_payment_for_loan_of_another_user():
    """
    Testa a tentativa de criar um pagamento para um empréstimo de outro usuário.
    """
    client = APIClient()
    user1 = User.objects.create_user(username="testuser1", password="password")
    user2 = User.objects.create_user(username="testuser2", password="password")
    
    loan = Loan.objects.create(
        nominal_value=1000,
        interest_rate=5,
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user1
    )

    client.force_authenticate(user=user2)
    payment_data = {
        "loan": loan.id,
        "amount": 200
    }
    
    response = client.post("/api/payments/", payment_data, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_payment_with_invalid_amount():
    """
    Testa a tentativa de criar um pagamento com um valor inválido (negativo ou zero).
    """
    client = APIClient()
    user = User.objects.create_user(username="testuser", password="password")
    client.force_authenticate(user=user)

    loan = Loan.objects.create(
        nominal_value=1000,
        interest_rate=5,
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user
    )

    payment_data = {
        "loan": loan.id,
        "amount": -100
    }
    response = client.post("/api/payments/", payment_data, format="json")
    assert response.status_code == 400

    payment_data['amount'] = 0
    response = client.post("/api/payments/", payment_data, format="json")
    assert response.status_code == 400
