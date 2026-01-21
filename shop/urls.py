from django.urls import path
from . import views
app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/category/<slug:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('search/', views.search, name='search'),
    path('occasion/<str:occasion>/', views.products_by_occasion, name='products_by_occasion'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    path('quick-view/<int:product_id>/', views.quick_view, name='quick_view'),
    
    # Product Management URLs (Staff Only)
    path('manage/', views.product_management, name='product_management'),
    path('manage/product/add/', views.product_add, name='product_add'),
    path('manage/product/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('manage/product/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('manage/product/<int:product_id>/toggle/', views.product_toggle_status, name='product_toggle_status'),
    path('manage/categories/', views.category_management, name='category_management'),
    path('manage/category/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('manage/category/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path('manage/flower-types/', views.flower_type_management, name='flower_type_management'),
    path('manage/flower-type/<int:flower_type_id>/delete/', views.flower_type_delete, name='flower_type_delete'),
    
    # Order Management URLs (Staff Only)
    path('manage/orders/', views.order_management, name='order_management'),
    path('manage/orders/<str:order_id>/', views.order_detail_manage, name='order_detail_manage'),
    path('manage/orders/<str:order_id>/update-status/', views.order_update_status, name='order_update_status'),
    path('manage/orders/<str:order_id>/add-tracking/', views.order_add_tracking, name='order_add_tracking'),
    
    # Settings Management
    path('manage/settings/', views.settings_management, name='settings_management'),
]
