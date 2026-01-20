from django import forms
from django.utils.text import slugify
from .models import Product, Category, FlowerType


class ProductForm(forms.ModelForm):
    """Form for adding/editing products"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'flower_types',
            'description', 'short_description',
            'price', 'discount_price',
            'size', 'contains',
            'image', 'image_2', 'image_3', 'image_4',
            'stock',
            'is_available', 'is_featured', 'is_bestseller', 'is_new',
            'care_instructions', 'same_day_delivery', 'delivery_time',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'placeholder': 'Enter product name'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300'
            }),
            'flower_types': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'size': '5'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'rows': 4,
                'placeholder': 'Detailed product description'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'rows': 2,
                'placeholder': 'Brief description for product cards'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01'
            }),
            'discount_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'placeholder': '0.00 (leave empty for no discount)',
                'min': '0',
                'step': '0.01'
            }),
            'size': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300'
            }),
            'contains': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'rows': 2,
                'placeholder': 'e.g., 12 Red Roses, Baby Breath, Greenery'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'min': '0'
            }),
            'care_instructions': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'rows': 3,
                'placeholder': 'How to care for this flower arrangement'
            }),
            'delivery_time': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'placeholder': 'e.g., 2-4 hours'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discount_price'].required = False
        self.fields['short_description'].required = False
        self.fields['contains'].required = False
        self.fields['care_instructions'].required = False
        self.fields['image_2'].required = False
        self.fields['image_3'].required = False
        self.fields['image_4'].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Auto-generate slug if not set
        if not instance.slug:
            instance.slug = slugify(instance.name)
            # Ensure uniqueness
            original_slug = instance.slug
            counter = 1
            while Product.objects.filter(slug=instance.slug).exclude(pk=instance.pk).exists():
                instance.slug = f"{original_slug}-{counter}"
                counter += 1
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class CategoryForm(forms.ModelForm):
    """Form for adding/editing categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'occasion', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'placeholder': 'Category name'
            }),
            'occasion': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'rows': 3
            }),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance


class FlowerTypeForm(forms.ModelForm):
    """Form for adding/editing flower types"""
    
    class Meta:
        model = FlowerType
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'placeholder': 'Flower type name (e.g., Roses, Lilies)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-300',
                'rows': 2
            }),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance
