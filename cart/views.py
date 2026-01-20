from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone

from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm, CouponApplyForm
from .models import Coupon


def cart_detail(request):
    """Display cart contents"""
    cart = Cart(request)
    coupon_form = CouponApplyForm()
    
    # Get applied coupon from session
    coupon_id = request.session.get('coupon_id')
    coupon = None
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if not coupon.is_valid():
                del request.session['coupon_id']
                coupon = None
        except Coupon.DoesNotExist:
            pass
    
    # Update cart item forms
    for item in cart:
        item['update_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'update': True
        })
    
    context = {
        'cart': cart,
        'coupon_form': coupon_form,
        'coupon': coupon,
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def cart_add(request, product_id):
    """Add product to cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            update_quantity=cd['update']
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'{product.name} added to cart!',
                'cart_count': len(cart),
                'cart_total': str(cart.get_total_price())
            })
        
        messages.success(request, f'{product.name} added to cart!')
    
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    """Update cart item quantity"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart.add(product=product, quantity=quantity, update_quantity=True)
    else:
        cart.remove(product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price())
        })
    
    return redirect('cart:cart_detail')


def cart_remove(request, product_id):
    """Remove product from cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} removed from cart',
            'cart_count': len(cart),
            'cart_total': str(cart.get_total_price())
        })
    
    messages.success(request, f'{product.name} removed from cart.')
    return redirect('cart:cart_detail')


def cart_clear(request):
    """Clear entire cart"""
    cart = Cart(request)
    cart.clear()
    
    # Clear coupon as well
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
    
    messages.success(request, 'Cart cleared successfully.')
    return redirect('cart:cart_detail')


@require_POST
def coupon_apply(request):
    """Apply coupon to cart"""
    cart = Cart(request)
    form = CouponApplyForm(request.POST)
    
    if form.is_valid():
        code = form.cleaned_data['code']
        now = timezone.now()
        
        try:
            coupon = Coupon.objects.get(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now,
                is_active=True
            )
            
            if coupon.used_count >= coupon.usage_limit:
                messages.error(request, 'This coupon has reached its usage limit.')
            elif cart.get_total_price() < coupon.min_order_value:
                messages.error(
                    request,
                    f'Minimum order value of ₹{coupon.min_order_value} required for this coupon.'
                )
            else:
                request.session['coupon_id'] = coupon.id
                messages.success(request, f'Coupon "{code}" applied successfully! {coupon.discount}% off.')
                
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid or expired coupon code.')
    
    return redirect('cart:cart_detail')


def coupon_remove(request):
    """Remove applied coupon"""
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        messages.success(request, 'Coupon removed.')
    return redirect('cart:cart_detail')


def cart_count(request):
    """AJAX endpoint for cart count"""
    cart = Cart(request)
    return JsonResponse({
        'count': len(cart),
        'total': str(cart.get_total_price())
    })
