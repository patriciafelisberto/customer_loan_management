from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Loan, Payment
from .serializers import LoanSerializer, PaymentSerializer


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
    permission_classes = [IsAuthenticated]
    queryset = Loan.objects.all()

    def get_queryset(self):
        """
        Sobrescreve o método get_queryset para garantir que o usuário veja
        apenas seus próprios empréstimos.

        Retorna:
            QuerySet contendo os empréstimos do usuário autenticado.
        """
        return Loan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Sobrescreve o método perform_create para salvar o empréstimo,
        associando-o ao usuário autenticado e registrando o endereço IP.

        Args:
            serializer (LoanSerializer): O serializer validado para o empréstimo.
        """
        serializer.save(user=self.request.user, ip_address=self.get_client_ip())

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
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()

    def get_queryset(self):
        """
        Sobrescreve o método get_queryset para garantir que o usuário veja
        apenas os pagamentos associados aos seus próprios empréstimos.

        Retorna:
            QuerySet contendo os pagamentos dos empréstimos do usuário autenticado.
        """
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
        if loan.user != self.request.user:
            raise PermissionDenied("Você não pode fazer um pagamento em um empréstimo que não é seu.")
        serializer.save()