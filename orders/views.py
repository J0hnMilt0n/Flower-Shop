from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from cart.cart import Cart
from cart.models import Coupon
from shop.models import SiteSettings
from .models import Address, Order, OrderItem, OrderTracking
from .forms import AddressForm, CheckoutForm


@login_required
def checkout(request):
    """Checkout page"""
    cart = Cart(request)
    site_settings = SiteSettings.load()
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty!')
        return redirect('shop:home')
    
    addresses = Address.objects.filter(user=request.user)
    
    # Get coupon if applied
    coupon_id = request.session.get('coupon_id')
    coupon = None
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = CheckoutForm(request.user, site_settings.enable_cod, request.POST)
        if form.is_valid():
            # Validate COD is enabled if selected
            payment_method = form.cleaned_data.get('payment_method', 'razorpay')
            if payment_method == 'cod' and not site_settings.enable_cod:
                messages.error(request, 'Cash on Delivery is currently not available.')
                return redirect('orders:checkout')
            
            address = form.cleaned_data['address']
            
            # Calculate totals
            subtotal = cart.get_total_price()
            discount = cart.get_discount(coupon)
            delivery_charge = 0 if subtotal >= 500 else 50
            total = subtotal - discount + delivery_charge
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                full_name=address.full_name,
                email=request.user.email,
                phone=address.phone,
                address_line1=address.address_line1,
                address_line2=address.address_line2,
                landmark=address.landmark,
                city=address.city,
                state=address.state,
                pincode=address.pincode,
                subtotal=subtotal,
                discount=discount,
                delivery_charge=delivery_charge,
                total=total,
                coupon_code=coupon.code if coupon else '',
                coupon_discount=discount,
                delivery_date=form.cleaned_data['delivery_date'],
                delivery_time_slot=form.cleaned_data['delivery_time_slot'],
                special_instructions=form.cleaned_data.get('special_instructions', ''),
                is_gift=form.cleaned_data.get('is_gift', False),
                gift_message=form.cleaned_data.get('gift_message', ''),
                payment_method=form.cleaned_data.get('payment_method', 'razorpay'),
            )
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    product_image=item['product'].image,
                    price=item['price'],
                    quantity=item['quantity']
                )
                
                # Update stock
                product = item['product']
                product.stock -= item['quantity']
                product.save()
            
            # Create tracking entry
            OrderTracking.objects.create(
                order=order,
                status='Order Placed',
                description='Your order has been placed successfully.'
            )
            
            # Store order ID in session for payment
            request.session['order_id'] = order.id
            
            # Clear cart
            cart.clear()
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
            
            # Redirect based on payment method
            if order.payment_method == 'cod':
                order.status = 'confirmed'
                order.save()
                OrderTracking.objects.create(
                    order=order,
                    status='Order Confirmed',
                    description='Your order has been confirmed. We will deliver it on the scheduled date.'
                )
                return redirect('orders:order_success', order_id=order.order_id)
            else:
                return redirect('payments:payment_process')
        else:
            # Form has errors - show them as messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field in form.fields and form.fields[field].label:
                        field_name = form.fields[field].label
                    else:
                        field_name = field.replace('_', ' ').title()
                    messages.error(request, f'{field_name}: {error}')
    else:
        form = CheckoutForm(request.user, site_settings.enable_cod)
    
    context = {
        'cart': cart,
        'addresses': addresses,
        'form': form,
        'coupon': coupon,
        'address_form': AddressForm(),
        'enable_cod': site_settings.enable_cod,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def add_address(request):
    """Add new address via AJAX"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'address': {
                        'id': address.id,
                        'full_name': address.full_name,
                        'address_line1': address.address_line1,
                        'city': address.city,
                        'state': address.state,
                        'pincode': address.pincode,
                    }
                })
            
            messages.success(request, 'Address added successfully!')
            return redirect('orders:checkout')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            })
    
    return redirect('orders:checkout')


@login_required
def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_success.html', context)


@login_required
def order_list(request):
    """List all orders for user"""
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list.html', context)


@login_required
def order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def track_order(request, order_id):
    """Track order status"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    tracking = order.tracking.all()
    
    context = {
        'order': order,
        'tracking': tracking,
    }
    return render(request, 'orders/track_order.html', context)


@login_required
def cancel_order(request, order_id):
    """Cancel order"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        
        OrderTracking.objects.create(
            order=order,
            status='Order Cancelled',
            description='Order has been cancelled by the customer.'
        )
        
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('orders:order_detail', order_id=order.order_id)


def check_pincode(request):
    """Check delivery availability by pincode"""
    pincode = request.GET.get('pincode', '')
    
    # Simulated delivery check - in production, integrate with actual delivery API
    available_pincodes = ['110001', '110002', '110003', '400001', '400002', '560001', '560002']
    
    if len(pincode) == 6 and pincode.isdigit():
        is_available = pincode in available_pincodes or int(pincode) % 2 == 0  # Simplified logic
        
        return JsonResponse({
            'available': is_available,
            'message': 'Delivery available!' if is_available else 'Sorry, delivery not available in this area.',
            'delivery_days': '2-3 days' if is_available else None
        })
    
    return JsonResponse({
        'available': False,
        'message': 'Please enter a valid 6-digit pincode.'
    })
