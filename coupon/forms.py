from django import forms
from .models import Coupon

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['name', 'description', 'code', 'discount_value', 'min_amount', 'max_discount', 'used_limit', 'expiry_at', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter coupon name',
                'style': 'margin: 20px 0; border-radius: 8px; padding: 10px 20px; border: 1px solid #ccc;'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter coupon code',
                'style': 'margin: 20px 0; border-radius: 8px; padding: 10px 20px; border: 1px solid #ccc;'
            }),
             'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description',
                'style': 'margin: 20px 0; border-radius: 8px; padding: 10px 20px; border: 1px solid #ccc;'
            }),
            'discount_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter discount value',
                'style': 'margin: 20px 0; border-radius: 8px; padding: 10px 20px; border: 1px solid #ccc;'
            }),
            'min_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter minimum amount',
                'style': 'margin: 20px 0; border-radius: 8px; padding: 10px 20px; border: 1px solid #ccc;'
            }),
            'max_discount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter maximum discount',
                'style': 'margin: 20px 0; border-radius: 8px; padding: 10px 20px; border: 1px solid #ccc;'
            }),
            'used_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter usage limit',
                'style': 'margin: 20px 0; border-radius: 8px; padding: 10px 20px; border: 1px solid #ccc;'
            }),
            'expiry_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter expiry date',
                'style': 'margin: 20px 0; border-radius: 8px; padding: 10px 20px; border: 1px solid #ccc;',
                'type': 'datetime-local'
            }),
        }
