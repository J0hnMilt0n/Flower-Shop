from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'min_order_value', 'valid_from', 'valid_to', 'is_active', 'used_count', 'usage_limit']
    list_filter = ['is_active', 'valid_from', 'valid_to']
    search_fields = ['code']
    list_editable = ['is_active']
