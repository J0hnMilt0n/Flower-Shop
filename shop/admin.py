from django.contrib import admin
from .models import Category, FlowerType, Product, ProductReview, Wishlist, Banner, SiteSettings


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'occasion', 'is_active', 'created_at']
    list_filter = ['occasion', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(FlowerType)
class FlowerTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_available', 'is_featured', 'is_bestseller']
    list_filter = ['category', 'is_available', 'is_featured', 'is_bestseller', 'is_new', 'size', 'same_day_delivery']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'discount_price', 'is_available', 'is_featured', 'is_bestseller']
    raw_id_fields = ['category']
    filter_horizontal = ['flower_types']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'flower_types', 'description', 'short_description')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'discount_percentage')
        }),
        ('Product Details', {
            'fields': ('size', 'contains', 'care_instructions')
        }),
        ('Images', {
            'fields': ('image', 'image_2', 'image_3', 'image_4')
        }),
        ('Inventory', {
            'fields': ('stock', 'is_available')
        }),
        ('Flags', {
            'fields': ('is_featured', 'is_bestseller', 'is_new')
        }),
        ('Delivery', {
            'fields': ('same_day_delivery', 'delivery_time')
        }),
        ('Ratings', {
            'fields': ('rating', 'num_reviews'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    raw_id_fields = ['product', 'user']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    raw_id_fields = ['user', 'product']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order', 'created_at']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Prevent adding more than one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False
    
    fieldsets = (
        ('Payment Settings', {
            'fields': ('enable_cod',),
            'description': 'Configure payment options for customers'
        }),
        ('Delivery Settings', {
            'fields': ('free_delivery_threshold', 'standard_delivery_charge'),
            'description': 'Configure delivery charges and thresholds'
        }),
        ('Store Status', {
            'fields': ('store_open', 'maintenance_mode', 'maintenance_message'),
            'description': 'Control store availability'
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'whatsapp_number'),
            'description': 'Store contact details',
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
