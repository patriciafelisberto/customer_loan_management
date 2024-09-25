from rest_framework.permissions import BasePermission

from .models import Loan, Payment


class IsOwnerOrSuperUser(BasePermission):
    """
    Permissão que permite acesso apenas ao dono do objeto ou ao superusuário.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Loan):
            return obj.user == request.user or request.user.is_superuser
        elif isinstance(obj, Payment):
            return obj.loan.user == request.user or request.user.is_superuser
        return False