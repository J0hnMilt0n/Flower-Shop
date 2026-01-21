from django import forms
from django.conf import settings
from .models import Address, Order


class AddressForm(forms.ModelForm):
    """Form for adding/editing addresses"""
    class Meta:
        model = Address
        fields = [
            'address_type', 'full_name', 'phone', 'alternate_phone',
            'address_line1', 'address_line2', 'landmark', 'city', 'state', 'pincode', 'is_default'
        ]
        widgets = {
            'address_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
                'placeholder': 'Full Name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
                'placeholder': 'Phone Number'
            }),
            'alternate_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
                'placeholder': 'Alternate Phone (Optional)'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
                'placeholder': 'House No., Building Name, Street'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
                'placeholder': 'Area, Colony (Optional)'
            }),
            'landmark': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
                'placeholder': 'Nearby Landmark (Optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
                'placeholder': 'State'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
                'placeholder': 'PIN Code'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-pink-600 focus:ring-pink-500 border-gray-300 rounded'
            }),
        }


class CheckoutForm(forms.Form):
    """Checkout form"""
    DELIVERY_TIME_CHOICES = [
        ('09:00-12:00', '9:00 AM - 12:00 PM'),
        ('12:00-15:00', '12:00 PM - 3:00 PM'),
        ('15:00-18:00', '3:00 PM - 6:00 PM'),
        ('18:00-21:00', '6:00 PM - 9:00 PM'),
    ]
    
    address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        widget=forms.RadioSelect(attrs={
            'class': 'h-4 w-4 text-pink-600 focus:ring-pink-500 border-gray-300'
        }),
        empty_label=None
    )
    
    delivery_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500'
        })
    )
    
    delivery_time_slot = forms.ChoiceField(
        choices=DELIVERY_TIME_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500'
        })
    )
    
    special_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
            'rows': 3,
            'placeholder': 'Any special instructions for delivery...'
        })
    )
    
    is_gift = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-pink-600 focus:ring-pink-500 border-gray-300 rounded'
        })
    )
    
    gift_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500',
            'rows': 3,
            'placeholder': 'Your message for the gift recipient...'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'h-4 w-4 text-pink-600 focus:ring-pink-500 border-gray-300'
        })
    )

    def __init__(self, user, enable_cod=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].queryset = Address.objects.filter(user=user)
        
        # Filter payment methods based on enable_cod parameter
        if not enable_cod:
            # Remove COD from choices
            choices = [choice for choice in Order.PAYMENT_METHOD_CHOICES if choice[0] != 'cod']
            self.fields['payment_method'].choices = choices
            # Set default to first available option
            if choices:
                self.fields['payment_method'].initial = choices[0][0]
