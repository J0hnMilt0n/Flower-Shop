from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Category model for flower arrangements"""
    OCCASION_CHOICES = [
        ('marriage', 'Marriage & Wedding'),
        ('birthday', 'Birthday'),
        ('anniversary', 'Anniversary'),
        ('valentines', "Valentine's Day"),
        ('funeral', 'Funeral & Sympathy'),
        ('congratulations', 'Congratulations'),
        ('get_well', 'Get Well Soon'),
        ('thank_you', 'Thank You'),
        ('housewarming', 'Housewarming'),
        ('corporate', 'Corporate Events'),
        ('festival', 'Festival & Celebrations'),
        ('everyday', 'Everyday Flowers'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    occasion = models.CharField(max_length=50, choices=OCCASION_CHOICES, default='everyday')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class FlowerType(models.Model):
    """Different types of flowers"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='flower_types/', blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Product model for flower arrangements"""
    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('premium', 'Premium'),
    ]
    
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    flower_types = models.ManyToManyField(FlowerType, related_name='products', blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    
    # Product details
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='medium')
    contains = models.TextField(help_text="List of flowers and items included", blank=True)
    care_instructions = models.TextField(blank=True)
    
    # Images
    image = models.ImageField(upload_to='products/')
    image_2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='products/', blank=True, null=True)
    image_4 = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Inventory
    stock = models.PositiveIntegerField(default=10)
    is_available = models.BooleanField(default=True)
    
    # Flags
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    
    # Delivery
    same_day_delivery = models.BooleanField(default=True)
    delivery_time = models.CharField(max_length=100, default="2-4 hours")
    
    # Ratings
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    num_reviews = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.discount_price and self.price:
            self.discount_percentage = int(((self.price - self.discount_price) / self.price) * 100)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.slug])

    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price

    @property
    def is_on_sale(self):
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def in_stock(self):
        return self.stock > 0 and self.is_available


class ProductReview(models.Model):
    """Customer reviews for products"""
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}"


class Wishlist(models.Model):
    """User wishlist"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username}'s wishlist - {self.product.name}"


class Banner(models.Model):
    """Homepage banners"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True)
    button_text = models.CharField(max_length=50, default="Shop Now")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
