from django.contrib import admin

from .models import Loan, Payment


class LoanAdmin(admin.ModelAdmin):
    exclude = ('deleted_at',)
    
    readonly_fields = ('created_at',)
    
    list_display = ('nominal_value', 'interest_rate', 'bank', 'client', 'user', 'created_at')
    
    list_filter = ('user', 'bank', 'request_date', 'created_at')


class PaymentAdmin(admin.ModelAdmin):
    exclude = ('deleted_at',)

    readonly_fields = ('created_at',)
    
    list_display = ('loan', 'amount', 'payment_date', 'created_at')
    
    list_filter = ('loan', 'payment_date', 'created_at')


admin.site.register(Loan, LoanAdmin)
admin.site.register(Payment, PaymentAdmin)
