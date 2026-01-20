from django.db import models
from django.contrib.auth.models import User


class Coupon(models.Model):
    """Discount coupons"""
    code = models.CharField(max_length=50, unique=True)
    discount = models.PositiveIntegerField(help_text="Percentage discount")
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} - {self.discount}%"
    
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            self.used_count < self.usage_limit
        )
