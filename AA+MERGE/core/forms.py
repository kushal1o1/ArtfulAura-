from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import  Review

PAYMENT_CHOICES = (
    ('E', 'Esewa', 'images/esewa.png'),
    ('K', 'Khalti', 'images/khalti.png'),
    ('S','Stripe','images/stripe.png')
)

class CheckoutForm(forms.Form):
    address = forms.CharField(required=False,widget=forms.TextInput(attrs={
                'placeholder': '1234 Main St',
                'id': 'address',
                'class': 'form-control',
            }))
    street_address = forms.CharField(required=False,widget=forms.TextInput(attrs={
                'placeholder': 'Apartment or suite',
                'id': 'address2',
                'class': 'form-control',
            }))
    country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    zip = forms.CharField(required=False,widget=forms.TextInput(attrs={
                'placeholder': 'Zip code',
                'id': 'shipping_zip',
                'class': 'form-control',
            }))
    phone_number = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={
                'placeholder': '98********',
                'id': 'phone_number',
                'class': 'form-control',
            }))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert 3-item tuples to 2-item tuples for Django's validation
        self.fields['payment_option'].choices = [(value, name) for value, name, _ in PAYMENT_CHOICES]
        # Store the original choices with images for the template
        self.payment_choices_with_images = PAYMENT_CHOICES

    

    set_default_shipping = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={
                'class': 'custom-control-input',
                'id': 'set_default_shipping',
            }))
    use_default_shipping = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    
    
class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }),required=False)

class RefundForm(forms.Form):
    ref_code = forms.CharField(widget=forms.TextInput(attrs={
                'placeholder': 'aswHQbsjasj',
                'id': 'ref_code',
                'class': 'form-control',
            }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 8,
        'class': 'form-control',
        'placeholder': 'Reason for refund ',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
                'placeholder': 'We will mail you in this for further queries',
                'id': 'email',
                'class': 'form-control',
            }))
    