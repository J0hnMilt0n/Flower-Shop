import razorpay
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.contrib import messages

from orders.models import Order, OrderTracking
from .models import Payment


# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def payment_process(request):
    """Process payment"""
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, 'No order found. Please try again.')
        return redirect('cart:cart_detail')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        return redirect('orders:order_success', order_id=order.order_id)
    
    # Create Razorpay order
    amount = int(order.total * 100)  # Amount in paise
    
    razorpay_order = razorpay_client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': 1,
        'notes': {
            'order_id': order.order_id,
            'user_id': request.user.id,
        }
    })
    
    # Save Razorpay order ID
    order.razorpay_order_id = razorpay_order['id']
    order.save()
    
    # Create payment record
    Payment.objects.create(
        order=order,
        gateway='razorpay',
        amount=order.total,
        gateway_order_id=razorpay_order['id'],
        status='initiated'
    )
    
    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'currency': 'INR',
        'callback_url': request.build_absolute_uri('/payments/callback/'),
    }
    return render(request, 'payments/payment_process.html', context)


@csrf_exempt
def payment_callback(request):
    """Razorpay payment callback"""
    if request.method == 'POST':
        try:
            # Get payment details from POST data
            razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            razorpay_signature = request.POST.get('razorpay_signature', '')
            
            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                signature_verified = True
            except:
                signature_verified = False
            
            # Get order
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            
            # Update payment record
            payment = Payment.objects.filter(
                order=order,
                gateway_order_id=razorpay_order_id
            ).first()
            
            if signature_verified:
                order.payment_status = 'paid'
                order.status = 'confirmed'
                order.razorpay_payment_id = razorpay_payment_id
                order.razorpay_signature = razorpay_signature
                order.save()
                
                if payment:
                    payment.status = 'completed'
                    payment.gateway_payment_id = razorpay_payment_id
                    payment.gateway_signature = razorpay_signature
                    payment.transaction_id = razorpay_payment_id
                    payment.save()
                
                OrderTracking.objects.create(
                    order=order,
                    status='Payment Received',
                    description=f'Payment of ₹{order.total} received via Razorpay.'
                )
                
                OrderTracking.objects.create(
                    order=order,
                    status='Order Confirmed',
                    description='Your order has been confirmed and is being processed.'
                )
                
                # Clear order from session
                if 'order_id' in request.session:
                    del request.session['order_id']
                
                return redirect('orders:order_success', order_id=order.order_id)
            else:
                order.payment_status = 'failed'
                order.save()
                
                if payment:
                    payment.status = 'failed'
                    payment.error_message = 'Signature verification failed'
                    payment.save()
                
                return redirect('payments:payment_failed')
                
        except Exception as e:
            return redirect('payments:payment_failed')
    
    return HttpResponseBadRequest()


@login_required
def payment_success(request):
    """Payment success page"""
    return render(request, 'payments/payment_success.html')


@login_required
def payment_failed(request):
    """Payment failed page"""
    order_id = request.session.get('order_id')
    order = None
    if order_id:
        order = Order.objects.filter(id=order_id).first()
    
    context = {
        'order': order,
    }
    return render(request, 'payments/payment_failed.html', context)


@login_required
def retry_payment(request, order_id):
    """Retry failed payment"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        return redirect('orders:order_detail', order_id=order.order_id)
    
    request.session['order_id'] = order.id
    return redirect('payments:payment_process')


@csrf_exempt
def razorpay_webhook(request):
    """Razorpay webhook handler"""
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            event = payload.get('event')
            
            if event == 'payment.captured':
                payment_entity = payload['payload']['payment']['entity']
                razorpay_order_id = payment_entity.get('order_id')
                razorpay_payment_id = payment_entity.get('id')
                
                try:
                    order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                    order.payment_status = 'paid'
                    order.status = 'confirmed'
                    order.razorpay_payment_id = razorpay_payment_id
                    order.save()
                except Order.DoesNotExist:
                    pass
            
            elif event == 'payment.failed':
                payment_entity = payload['payload']['payment']['entity']
                razorpay_order_id = payment_entity.get('order_id')
                
                try:
                    order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                    order.payment_status = 'failed'
                    order.save()
                except Order.DoesNotExist:
                    pass
            
            return JsonResponse({'status': 'ok'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
