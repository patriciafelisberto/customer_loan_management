from rest_framework import serializers

from .models import Loan, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'loan', 'payment_date', 'amount']


class LoanSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    outstanding_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'nominal_value', 'interest_rate', 'ip_address', 'request_date', 'bank', 'client', 'outstanding_balance', 'payments']
        read_only_fields = ['id', 'request_date', 'outstanding_balance', 'payments', 'ip_address']
