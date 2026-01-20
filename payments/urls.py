from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/', views.payment_process, name='payment_process'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
    path('retry/<str:order_id>/', views.retry_payment, name='retry_payment'),
    path('webhook/', views.razorpay_webhook, name='razorpay_webhook'),
]
