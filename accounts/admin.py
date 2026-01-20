from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'subscribe_newsletter', 'created_at']
    list_filter = ['subscribe_newsletter', 'order_notifications', 'promo_notifications']
    search_fields = ['user__username', 'user__email', 'phone']
    raw_id_fields = ['user']
