from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('add-address/', views.add_address, name='add_address'),
    path('success/<str:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.order_list, name='order_list'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),
    path('track/<str:order_id>/', views.track_order, name='track_order'),
    path('cancel/<str:order_id>/', views.cancel_order, name='cancel_order'),
    path('check-pincode/', views.check_pincode, name='check_pincode'),
]
