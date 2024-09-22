import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from loans.models import Loan


@pytest.mark.django_db
def test_get_loans_authenticated():
    client = APIClient()
    user = User.objects.create_user(username="testuser", password="password")
    client.force_authenticate(user=user)

    # Crie um empréstimo para o usuário autenticado
    Loan.objects.create(
        nominal_value=1000,
        interest_rate=5,
        ip_address="127.0.0.1",
        bank="Test Bank",
        client="Test Client",
        user=user
    )

    response = client.get("/api/loans/")
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_create_loan():
    client = APIClient()
    user = User.objects.create_user(username="testuser", password="password")
    client.force_authenticate(user=user)

    loan_data = {
        "nominal_value": 1000,
        "interest_rate": 5,
        "bank": "Test Bank",
        "client": "Test Client"
    }

    response = client.post("/api/loans/", loan_data, format="json")
    assert response.status_code == 201
