from rest_framework import serializers

from .models import Loan, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'loan', 'payment_date', 'amount']

    def validate_amount(self, value):
        """
        Valida se o valor do pagamento é positivo.
        """
        if value <= 0:
            raise serializers.ValidationError("The payment amount must be positive.")
        return value 


class LoanSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    outstanding_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'nominal_value', 'interest_rate', 'ip_address', 'request_date', 'bank', 'client', 'outstanding_balance', 'payments', 'user']
        read_only_fields = ['id', 'request_date', 'outstanding_balance', 'payments', 'ip_address', 'user']

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_superuser:
            attrs['user'] = user
        return attrs
