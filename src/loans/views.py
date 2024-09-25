from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound

from .models import Loan, Payment
from .permissions import IsOwnerOrSuperUser
from .serializers import LoanSerializer, PaymentSerializer
from .exceptions import (
    LoanNotFound, 
    PaymentNotAllowed, 
    InvalidPaymentAmount
)

class LoanViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar empréstimos (Loans) dos usuários autenticados.

    Funcionalidades:
        - Listar os empréstimos do usuário autenticado.
        - Criar um novo empréstimo, com o IP sendo automaticamente registrado.
        - Detalhar, atualizar ou deletar empréstimos existentes (somente do próprio usuário).

    Permissões:
        - Apenas usuários autenticados podem acessar esse endpoint.

    Métodos:
        get_queryset: Retorna apenas os empréstimos associados ao usuário autenticado.
        perform_create: Cria um novo empréstimo, associando-o ao usuário autenticado e registrando o IP.
        get_client_ip: Obtém o endereço IP do usuário solicitante.
    """
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSuperUser]
    queryset = Loan.objects.all()

    def get_queryset(self):
        """
        Retorna todos os empréstimos se o usuário for um superusuário.
        Caso contrário, retorna apenas os empréstimos do usuário autenticado.

        Retorna:
            QuerySet contendo os empréstimos do usuário autenticado.
        """
        if self.request.user.is_superuser:
            return Loan.objects.all()
        return Loan.objects.filter(user=self.request.user)
    
    def get_object(self):
        """
        Sobrescreve o get_object para garantir que o empréstimo seja encontrado, 
        mas verifica permissões de acesso posteriormente.
        """
        loan_id = self.kwargs.get('pk')
        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            raise NotFound("Loan not found.")

        return loan

    def perform_create(self, serializer):
        """
        Sobrescreve o método perform_create para salvar o empréstimo,
        associando-o ao usuário autenticado e registrando o endereço IP.

        Args:
            serializer (LoanSerializer): O serializer validado para o empréstimo.
        """
        ip_address = self.get_client_ip()
        if not self.request.user.is_superuser:
            serializer.save(user=self.request.user, ip_address=ip_address)
        else:
            serializer.save(ip_address=ip_address)

    def perform_destroy(self, instance):
            """
            Realiza a exclusão de uma instância de empréstimo.

            A exclusão só é permitida se o usuário associado ao empréstimo for o mesmo que está
            fazendo a solicitação ou se o usuário for um superusuário.

            Caso contrário, uma exceção de permissão negada será levantada.

            Parâmetros:
                instance: A instância do empréstimo que será excluída.

            Levanta:
                PermissionDenied: Se o usuário não tiver permissão para excluir o empréstimo.
            """
            if instance.user != self.request.user and not self.request.user.is_superuser:
                raise PermissionDenied("You do not have permission to delete this loan.")
            instance.delete()

    def get_client_ip(self):
        """
        Obtém o endereço IP do cliente a partir dos cabeçalhos da requisição.

        Retorna:
            str: O endereço IP do cliente.
        """
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar pagamentos (Payments) dos usuários autenticados.

    Funcionalidades:
        - Listar os pagamentos associados aos empréstimos do usuário autenticado.
        - Criar um novo pagamento para um empréstimo existente.
        - Detalhar, atualizar ou deletar pagamentos (somente de empréstimos do próprio usuário).

    Permissões:
        - Apenas usuários autenticados podem acessar esse endpoint.

    Métodos:
        get_queryset: Retorna os pagamentos associados aos empréstimos do usuário autenticado.
        perform_create: Valida e cria um pagamento, garantindo que o pagamento seja para um empréstimo do próprio usuário.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrSuperUser]
    queryset = Payment.objects.all()

    def get_queryset(self):
        """
        Sobrescreve o método get_queryset para garantir que o usuário veja
        apenas os pagamentos associados aos seus próprios empréstimos.

        Retorna:
            QuerySet contendo os pagamentos dos empréstimos do usuário autenticado.
        """
        if self.request.user.is_superuser:
            return Payment.objects.all()
        return Payment.objects.filter(loan__user=self.request.user)

    def perform_create(self, serializer):
        """
        Sobrescreve o método perform_create para garantir que o pagamento
        só possa ser feito para um empréstimo que pertence ao usuário autenticado.

        Args:
            serializer (PaymentSerializer): O serializer validado para o pagamento.

        Levanta:
            PermissionDenied: Se o empréstimo associado ao pagamento não pertencer ao usuário autenticado.
        """
        loan = serializer.validated_data['loan']

        if loan.user != self.request.user and not self.request.user.is_superuser:
            raise PaymentNotAllowed()

        if loan.deleted_at is not None:
            raise LoanNotFound("The loan you are trying to pay has been deleted.")

        amount = serializer.validated_data['amount']

        if amount <= 0:
            raise InvalidPaymentAmount("The payment amount must be positive.")

        outstanding_balance = loan.outstanding_balance

        if amount > outstanding_balance:
            raise InvalidPaymentAmount(
                f"The payment amount exceeds the outstanding balance of {outstanding_balance}."
            )

        serializer.save()

    def perform_destroy(self, instance):
        """
        Realiza a exclusão de uma instância de pagamento.

        A exclusão só é permitida se o usuário associado ao empréstimo do pagamento
        for o mesmo que está fazendo a solicitação ou se o usuário for um superusuário.

        Caso contrário, uma exceção de permissão negada será levantada.

        Parâmetros:
            instance: A instância do pagamento que será excluída.

        Levanta:
            PermissionDenied: Se o usuário não tiver permissão para excluir o pagamento.
        """
        if instance.loan.user != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this payment.")
        instance.delete()