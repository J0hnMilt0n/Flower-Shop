from django import forms


class CartAddProductForm(forms.Form):
    """Form to add products to cart"""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-16 text-center border border-gray-300 rounded-md py-2',
        })
    )
    update = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )


class CouponApplyForm(forms.Form):
    """Form to apply coupon"""
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
            'placeholder': 'Enter coupon code'
        })
    )
