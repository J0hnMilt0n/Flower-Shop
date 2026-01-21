from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.utils import timezone

from .models import Category, Product, ProductReview, Wishlist, Banner, FlowerType, SiteSettings
from .forms import ProductForm, CategoryForm, FlowerTypeForm
from orders.models import Order, OrderTracking


def home(request):
    """Homepage view"""
    banners = Banner.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)[:8]
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    bestsellers = Product.objects.filter(is_bestseller=True, is_available=True)[:8]
    new_arrivals = Product.objects.filter(is_new=True, is_available=True)[:8]
    
    # Occasion-based categories
    occasions = [
        {'name': 'Marriage & Wedding', 'slug': 'marriage', 'icon': '💒'},
        {'name': 'Birthday', 'slug': 'birthday', 'icon': '🎂'},
        {'name': 'Anniversary', 'slug': 'anniversary', 'icon': '💕'},
        {'name': "Valentine's Day", 'slug': 'valentines', 'icon': '❤️'},
        {'name': 'Congratulations', 'slug': 'congratulations', 'icon': '🎉'},
        {'name': 'Get Well Soon', 'slug': 'get_well', 'icon': '💐'},
        {'name': 'Corporate Events', 'slug': 'corporate', 'icon': '🏢'},
        {'name': 'Festival', 'slug': 'festival', 'icon': '🎊'},
    ]
    
    context = {
        'banners': banners,
        'categories': categories,
        'featured_products': featured_products,
        'bestsellers': bestsellers,
        'new_arrivals': new_arrivals,
        'occasions': occasions,
    }
    return render(request, 'shop/home.html', context)


class ProductListView(ListView):
    """List all products with filtering"""
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)
        
        # Category filter
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)
        else:
            self.category = None
        
        # Occasion filter
        occasion = self.request.GET.get('occasion')
        if occasion:
            queryset = queryset.filter(category__occasion=occasion)
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Size filter
        size = self.request.GET.get('size')
        if size:
            queryset = queryset.filter(size=size)
        
        # Same day delivery filter
        same_day = self.request.GET.get('same_day')
        if same_day:
            queryset = queryset.filter(same_day_delivery=True)
        
        # Sort
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'rating':
            queryset = queryset.order_by('-rating')
        elif sort == 'bestseller':
            queryset = queryset.filter(is_bestseller=True)
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['current_category'] = getattr(self, 'category', None)
        context['flower_types'] = FlowerType.objects.all()
        context['size_choices'] = Product.SIZE_CHOICES
        context['current_filters'] = {
            'occasion': self.request.GET.get('occasion', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'size': self.request.GET.get('size', ''),
            'same_day': self.request.GET.get('same_day', ''),
            'sort': self.request.GET.get('sort', 'newest'),
        }
        return context


class ProductDetailView(DetailView):
    """Product detail view"""
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:4]
        
        # Reviews
        context['reviews'] = product.reviews.all()[:10]
        context['avg_rating'] = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Check if user has wishlisted
        if self.request.user.is_authenticated:
            context['is_wishlisted'] = Wishlist.objects.filter(
                user=self.request.user,
                product=product
            ).exists()
        
        return context


def search(request):
    """Search products"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_available=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(flower_types__name__icontains=query)
        ).distinct()
    
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'query': query,
        'total_results': paginator.count,
    }
    return render(request, 'shop/search_results.html', context)


def products_by_occasion(request, occasion):
    """Filter products by occasion"""
    products = Product.objects.filter(
        category__occasion=occasion,
        is_available=True
    )
    
    occasion_names = dict(Category.OCCASION_CHOICES)
    occasion_name = occasion_names.get(occasion, 'Products')
    
    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'occasion': occasion,
        'occasion_name': occasion_name,
        'categories': Category.objects.filter(is_active=True),
    }
    return render(request, 'shop/products_by_occasion.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'added' if created else 'exists',
            'message': 'Added to wishlist!' if created else 'Already in wishlist'
        })
    
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist.')
    
    return redirect('shop:product_detail', slug=product.slug)


@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'removed',
            'message': 'Removed from wishlist'
        })
    
    messages.success(request, f'{product.name} removed from wishlist.')
    return redirect('accounts:wishlist')


@login_required
def add_review(request, product_id):
    """Add product review"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Check if user already reviewed
        if ProductReview.objects.filter(user=request.user, product=product).exists():
            messages.error(request, 'You have already reviewed this product.')
            return redirect('shop:product_detail', slug=product.slug)
        
        rating = int(request.POST.get('rating', 5))
        title = request.POST.get('title', '')
        comment = request.POST.get('comment', '')
        
        review = ProductReview.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            title=title,
            comment=comment
        )
        
        # Update product rating
        avg_rating = product.reviews.aggregate(Avg('rating'))['rating__avg']
        product.rating = avg_rating
        product.num_reviews = product.reviews.count()
        product.save()
        
        messages.success(request, 'Thank you for your review!')
        return redirect('shop:product_detail', slug=product.slug)
    
    return redirect('shop:home')


def quick_view(request, product_id):
    """Quick view modal data"""
    product = get_object_or_404(Product, id=product_id)
    
    data = {
        'id': product.id,
        'name': product.name,
        'price': str(product.price),
        'discount_price': str(product.discount_price) if product.discount_price else None,
        'discount_percentage': product.discount_percentage,
        'image': product.image.url if product.image else '',
        'short_description': product.short_description,
        'size': product.get_size_display(),
        'in_stock': product.in_stock,
        'same_day_delivery': product.same_day_delivery,
        'rating': float(product.rating),
        'num_reviews': product.num_reviews,
        'url': product.get_absolute_url(),
    }
    
    return JsonResponse(data)


# ============================================
# PRODUCT MANAGEMENT VIEWS (Staff Only)
# ============================================

@staff_member_required
def product_management(request):
    """Product management dashboard"""
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    flower_types = FlowerType.objects.all()
    
    # Search
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query)
        )
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filter by status
    status = request.GET.get('status')
    if status == 'active':
        products = products.filter(is_available=True)
    elif status == 'inactive':
        products = products.filter(is_available=False)
    elif status == 'low_stock':
        products = products.filter(stock__lte=10)
    
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': categories,
        'flower_types': flower_types,
        'total_products': Product.objects.count(),
        'active_products': Product.objects.filter(is_available=True).count(),
        'low_stock_count': Product.objects.filter(stock__lte=10).count(),
        'query': query,
    }
    return render(request, 'shop/manage/product_list.html', context)


@staff_member_required
def product_add(request):
    """Add new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('shop:product_management')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'categories': Category.objects.all(),
        'flower_types': FlowerType.objects.all(),
        'title': 'Add New Product',
    }
    return render(request, 'shop/manage/product_form.html', context)


@staff_member_required
def product_edit(request, product_id):
    """Edit existing product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('shop:product_management')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'categories': Category.objects.all(),
        'flower_types': FlowerType.objects.all(),
        'title': f'Edit Product: {product.name}',
    }
    return render(request, 'shop/manage/product_form.html', context)


@staff_member_required
def product_delete(request, product_id):
    """Delete product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully!')
        return redirect('shop:product_management')
    
    return render(request, 'shop/manage/product_delete.html', {'product': product})


@staff_member_required
def product_toggle_status(request, product_id):
    """Toggle product availability"""
    product = get_object_or_404(Product, id=product_id)
    product.is_available = not product.is_available
    product.save()
    
    status = 'activated' if product.is_available else 'deactivated'
    messages.success(request, f'Product "{product.name}" {status}!')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'is_available': product.is_available})
    
    return redirect('shop:product_management')


@staff_member_required
def category_management(request):
    """Category management"""
    categories = Category.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('shop:category_management')
    else:
        form = CategoryForm()
    
    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'shop/manage/category_list.html', context)


@staff_member_required
def category_edit(request, category_id):
    """Edit category"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('shop:category_management')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'shop/manage/category_form.html', {'form': form, 'category': category})


@staff_member_required
def category_delete(request, category_id):
    """Delete category"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
    return redirect('shop:category_management')


@staff_member_required
def flower_type_management(request):
    """Flower type management"""
    flower_types = FlowerType.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = FlowerTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Flower type added successfully!')
            return redirect('shop:flower_type_management')
    else:
        form = FlowerTypeForm()
    
    context = {
        'flower_types': flower_types,
        'form': form,
    }
    return render(request, 'shop/manage/flower_type_list.html', context)


@staff_member_required
def flower_type_delete(request, flower_type_id):
    """Delete flower type"""
    flower_type = get_object_or_404(FlowerType, id=flower_type_id)
    if request.method == 'POST':
        flower_type.delete()
        messages.success(request, 'Flower type deleted successfully!')
    return redirect('shop:flower_type_management')


# ============================================
# ORDER MANAGEMENT VIEWS (Staff Only)
# ============================================

@staff_member_required
def order_management(request):
    """Order management dashboard"""
    orders = Order.objects.all().order_by('-created_at')
    
    # Search
    query = request.GET.get('q', '')
    if query:
        orders = orders.filter(
            Q(order_id__icontains=query) |
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Filter by payment status
    payment = request.GET.get('payment')
    if payment:
        orders = orders.filter(payment_status=payment)
    
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'processing_orders': Order.objects.filter(status='processing').count(),
        'out_for_delivery_orders': Order.objects.filter(status='out_for_delivery').count(),
        'delivered_orders': Order.objects.filter(status='delivered').count(),
        'query': query,
    }
    return render(request, 'shop/manage/order_list.html', context)


@staff_member_required
def order_detail_manage(request, order_id):
    """Order detail for management"""
    order = get_object_or_404(Order, order_id=order_id)
    tracking = order.tracking.all().order_by('-created_at')
    
    context = {
        'order': order,
        'tracking': tracking,
    }
    return render(request, 'shop/manage/order_detail.html', context)


@staff_member_required
def order_update_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(Order, order_id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status and new_status != order.status:
            old_status = order.status
            order.status = new_status
            
            # Set delivered_at timestamp when delivered
            if new_status == 'delivered' and not order.delivered_at:
                order.delivered_at = timezone.now()
            
            order.save()
            
            # Create tracking entry
            status_messages = {
                'pending': ('Order Pending', 'Order is waiting to be processed.'),
                'confirmed': ('Order Confirmed', 'Your order has been confirmed and is being processed.'),
                'processing': ('Order Processing', 'Your beautiful arrangement is being prepared with care.'),
                'out_for_delivery': ('Out for Delivery', 'Your flowers are on the way! Our delivery partner will reach you soon.'),
                'delivered': ('Delivered', 'Your order has been delivered successfully. Enjoy your flowers!'),
                'cancelled': ('Order Cancelled', 'Your order has been cancelled.'),
                'refunded': ('Order Refunded', 'Your payment has been refunded.'),
            }
            
            if new_status in status_messages:
                status_title, description = status_messages[new_status]
                if notes:
                    description = notes
                OrderTracking.objects.create(
                    order=order,
                    status=status_title,
                    description=description
                )
            
            messages.success(request, f'Order status updated to {order.get_status_display()}!')
        else:
            messages.info(request, 'No status change made.')
    
    # Redirect back to the referring page or order detail
    referer = request.META.get('HTTP_REFERER', '')
    if 'order_management' in referer or referer.endswith('/manage/orders/'):
        return redirect('shop:order_management')
    return redirect('shop:order_detail_manage', order_id=order_id)


@staff_member_required
def order_add_tracking(request, order_id):
    """Add custom tracking entry"""
    order = get_object_or_404(Order, order_id=order_id)
    
    if request.method == 'POST':
        status = request.POST.get('status', '')
        description = request.POST.get('description', '')
        location = request.POST.get('location', '')
        
        if status:
            OrderTracking.objects.create(
                order=order,
                status=status,
                description=description,
                location=location
            )
            messages.success(request, 'Tracking entry added successfully!')
    
    return redirect('shop:order_detail_manage', order_id=order_id)


@staff_member_required
def settings_management(request):
    """Site settings management"""
    settings = SiteSettings.load()
    
    if request.method == 'POST':
        # Update settings
        settings.enable_cod = request.POST.get('enable_cod') == 'on'
        settings.free_delivery_threshold = request.POST.get('free_delivery_threshold', 500)
        settings.standard_delivery_charge = request.POST.get('standard_delivery_charge', 50)
        settings.store_open = request.POST.get('store_open') == 'on'
        settings.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        settings.maintenance_message = request.POST.get('maintenance_message', '')
        settings.contact_email = request.POST.get('contact_email', '')
        settings.contact_phone = request.POST.get('contact_phone', '')
        settings.whatsapp_number = request.POST.get('whatsapp_number', '')
        settings.updated_by = request.user
        settings.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('shop:settings_management')
    
    context = {
        'settings': settings,
    }
    return render(request, 'shop/manage/settings.html', context)
