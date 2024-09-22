import uuid
from decimal import Decimal
from datetime import date

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class SoftDeleteQuerySet(models.QuerySet):
    """
    Um QuerySet personalizado que implementa soft delete, ou seja, registros são
    "desativados" em vez de realmente excluídos do banco de dados.

    Métodos:
        delete: Executa um soft delete, definindo o campo 'deleted_at' com a data e hora atual.
        hard_delete: Exclui permanentemente o registro do banco de dados.
        alive: Retorna apenas registros que ainda não foram excluídos (soft delete).
        dead: Retorna apenas registros que foram excluídos (soft delete).
    """
    def delete(self):
        """
        Executa um soft delete marcando o campo 'deleted_at' com a data e hora atuais.
        Retorna o número de registros afetados.
        """
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        """
        Exclui permanentemente os registros do banco de dados.
        """
        return super().delete()

    def alive(self):
        """
        Retorna um QuerySet contendo apenas os registros que não foram marcados como deletados.
        """
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        """
        Retorna um QuerySet contendo apenas os registros que foram marcados como deletados.
        """
        return self.filter(deleted_at__isnull=False)


class BaseModel(models.Model):
    """
    Um modelo base abstrato que implementa os campos e comportamentos de soft delete.

    Atributos:
        created_at: Data e hora de criação do registro.
        updated_at: Data e hora da última atualização do registro.
        deleted_at: Data e hora de deleção (soft delete). Nulo se o registro não foi deletado.
    
    Métodos:
        delete: Executa um soft delete definindo o campo 'deleted_at' com a data e hora atuais.
        hard_delete: Exclui permanentemente o registro do banco de dados.
        restore: Restaura um registro que foi soft deleted, removendo o valor do campo 'deleted_at'.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteQuerySet.as_manager()

    def delete(self):
        """
        Executa um soft delete marcando o campo 'deleted_at' com a data e hora atuais.
        """
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        """
        Exclui permanentemente o registro do banco de dados.
        """
        super().delete()

    def restore(self):
        """
        Restaura o registro que foi excluído por soft delete, removendo o valor de 'deleted_at'.
        """
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True


class Loan(BaseModel):
    """
    Modelo que representa um empréstimo realizado pelo cliente.
    
    Atributos:
        nominal_value: O valor nominal do empréstimo.
        interest_rate: A taxa de juros mensal aplicada ao empréstimo.
        ip_address: O endereço IP do cliente que realizou o empréstimo.
        request_date: A data em que o empréstimo foi solicitado.
        bank: O nome do banco que emprestou o dinheiro.
        client: O nome do cliente que solicitou o empréstimo.
        user: O usuário associado a este empréstimo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nominal_value = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    ip_address = models.GenericIPAddressField()
    request_date = models.DateField(auto_now_add=True)
    bank = models.CharField(max_length=255)
    client = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loans')

    def __str__(self):
        return f"Loan {self.nominal_value} for {self.client} at {self.bank}"

    @property
    def outstanding_balance(self):
        """
        Calcula o saldo devedor do empréstimo.
        
        O saldo devedor é calculado com base no valor nominal e na taxa de juros acumulada 
        durante os meses que se passaram desde a data do empréstimo. Também considera os 
        pagamentos já feitos.
        
        Retorna:
            Decimal: O valor atual do saldo devedor.
        """
        months = (date.today().year - self.request_date.year) * 12 + date.today().month - self.request_date.month
        months = max(months, 0)
        interest_rate = self.interest_rate / Decimal('100')
        total_interest = self.nominal_value * interest_rate * months
        total_due = self.nominal_value + total_interest
        total_payments = sum(payment.amount for payment in self.payments.all())
        balance = total_due - total_payments
        return balance


class Payment(BaseModel):
    """
    Modelo que representa um pagamento realizado para um empréstimo.

    Atributos:
        loan: O empréstimo ao qual este pagamento está associado.
        payment_date: A data em que o pagamento foi realizado (preenchido automaticamente).
        amount: O valor do pagamento.
    """
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment of {self.amount} on {self.payment_date} for {self.loan.client}'s loan"
