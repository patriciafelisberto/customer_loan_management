from rest_framework import routers

from .views import LoanViewSet, PaymentViewSet


router = routers.DefaultRouter()
router.register(r'loans', LoanViewSet, basename='loan')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = router.urls