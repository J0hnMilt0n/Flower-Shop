from django.contrib import admin
from django.utils import timezone
from .models import Address, Order, OrderItem, OrderTracking


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'city', 'state', 'pincode', 'is_default', 'address_type']
    list_filter = ['address_type', 'is_default', 'state', 'city']
    search_fields = ['full_name', 'phone', 'city', 'pincode']
    raw_id_fields = ['user']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'full_name', 'total', 'status', 'payment_status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_id', 'full_name', 'email', 'phone']
    raw_id_fields = ['user']
    inlines = [OrderItemInline, OrderTrackingInline]
    readonly_fields = ['order_id', 'created_at', 'updated_at']
    list_editable = ['status', 'payment_status']
    actions = ['mark_confirmed', 'mark_processing', 'mark_out_for_delivery', 'mark_delivered', 'mark_cancelled']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'status', 'payment_status', 'payment_method')
        }),
        ('Customer Details', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Delivery Address', {
            'fields': ('address_line1', 'address_line2', 'landmark', 'city', 'state', 'pincode')
        }),
        ('Order Amount', {
            'fields': ('subtotal', 'discount', 'coupon_code', 'coupon_discount', 'delivery_charge', 'total')
        }),
        ('Payment Details', {
            'fields': ('payment_id', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',)
        }),
        ('Delivery Details', {
            'fields': ('delivery_date', 'delivery_time_slot', 'special_instructions', 'gift_message', 'is_gift')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Auto-create tracking entry when status changes"""
        if change and 'status' in form.changed_data:
            old_status = Order.objects.get(pk=obj.pk).status
            new_status = obj.status
            
            # Set delivered_at timestamp when delivered
            if new_status == 'delivered' and not obj.delivered_at:
                obj.delivered_at = timezone.now()
            
            super().save_model(request, obj, form, change)
            
            # Create tracking entry
            status_messages = {
                'confirmed': ('Order Confirmed', 'Your order has been confirmed and is being processed.'),
                'processing': ('Order Processing', 'Your beautiful arrangement is being prepared with care.'),
                'out_for_delivery': ('Out for Delivery', 'Your flowers are on the way! Our delivery partner will reach you soon.'),
                'delivered': ('Delivered', 'Your order has been delivered successfully. Enjoy your flowers!'),
                'cancelled': ('Order Cancelled', 'Your order has been cancelled.'),
                'refunded': ('Order Refunded', 'Your payment has been refunded.'),
            }
            
            if new_status in status_messages:
                status_title, description = status_messages[new_status]
                OrderTracking.objects.create(
                    order=obj,
                    status=status_title,
                    description=description
                )
        else:
            super().save_model(request, obj, form, change)

    def _update_status(self, request, queryset, status, status_title, description):
        """Helper to update order status and create tracking"""
        updated = 0
        for order in queryset:
            if order.status != status:
                order.status = status
                if status == 'delivered' and not order.delivered_at:
                    order.delivered_at = timezone.now()
                order.save()
                OrderTracking.objects.create(
                    order=order,
                    status=status_title,
                    description=description
                )
                updated += 1
        self.message_user(request, f'{updated} order(s) marked as {status_title}.')

    @admin.action(description='Mark selected orders as Confirmed')
    def mark_confirmed(self, request, queryset):
        self._update_status(
            request, queryset, 'confirmed',
            'Order Confirmed',
            'Your order has been confirmed and is being processed.'
        )

    @admin.action(description='Mark selected orders as Processing')
    def mark_processing(self, request, queryset):
        self._update_status(
            request, queryset, 'processing',
            'Order Processing',
            'Your beautiful arrangement is being prepared with care.'
        )

    @admin.action(description='Mark selected orders as Out for Delivery')
    def mark_out_for_delivery(self, request, queryset):
        self._update_status(
            request, queryset, 'out_for_delivery',
            'Out for Delivery',
            'Your flowers are on the way! Our delivery partner will reach you soon.'
        )

    @admin.action(description='Mark selected orders as Delivered')
    def mark_delivered(self, request, queryset):
        self._update_status(
            request, queryset, 'delivered',
            'Delivered',
            'Your order has been delivered successfully. Enjoy your flowers!'
        )

    @admin.action(description='Mark selected orders as Cancelled')
    def mark_cancelled(self, request, queryset):
        self._update_status(
            request, queryset, 'cancelled',
            'Order Cancelled',
            'Your order has been cancelled.'
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'price', 'quantity', 'get_total']
    raw_id_fields = ['order', 'product']


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'location', 'created_at']
    list_filter = ['status', 'created_at']
    raw_id_fields = ['order']
