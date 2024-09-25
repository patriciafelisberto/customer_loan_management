from rest_framework.exceptions import APIException
from rest_framework import status


class LoanNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Loan not found.'
    default_code = 'loan_not_found'


class PaymentNotAllowed(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You are not allowed to make a payment on this loan.'
    default_code = 'payment_not_allowed'


class InvalidPaymentAmount(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'The payment amount is invalid.'
    default_code = 'invalid_payment_amount'
