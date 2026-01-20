from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'gateway', 'amount', 'status', 'created_at']
    list_filter = ['gateway', 'status', 'created_at']
    search_fields = ['transaction_id', 'order__order_id', 'gateway_payment_id']
    raw_id_fields = ['order']
    readonly_fields = ['created_at', 'updated_at']
