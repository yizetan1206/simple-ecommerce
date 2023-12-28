from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from multiupload.fields import MultiFileField

class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    email = forms.EmailField(label='Email')
    message = forms.CharField(label='Message', widget=forms.Textarea)

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required attribute for all fields
        for field_name, field in self.fields.items():
            field.required = True



class AddressForm(forms.ModelForm):
    class Meta:
        model = UsersAddress
        fields = ['address_line1', 'address_line2', 'city', 'postal_code', 'country', 'phone_number']
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required attribute for all fields
        for field_name, field in self.fields.items():
            field.required = True


# class LoginForm(forms.Form):
#     username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
#     password = forms.CharField(widget=forms.PasswordInput(
    

class AddCategoryform(forms.ModelForm):
    class Meta:
        model = ProductsCategories
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }


class AddProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=ProductsCategories.objects.all(), label='Product Category')

    class Meta:
        model = Products
        fields = ['category', 'name', 'description']

    def save(self, commit=True):
        product = super().save(commit)

        return product
    
class AddVariationForm(forms.ModelForm):
    class Meta:
        model = Products_variation
        fields = ['id', 'features', 'price', 'quantity']
        widgets = {
            'price': forms.NumberInput(attrs={'min': 0, 'step': 'any'}),
        }
        error_messages = {
            'variation_name': {
                'required': 'Please enter name properly',
            },
            'price': {
                'required': 'Please enter price properly',
            },
        }
        def save(self, commit=True):
            variation = super().save(commit)

            return variation
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['features'].widget.attrs['placeholder'] = 'Features (eg.10kW,50kW)'
        self.fields['price'].widget.attrs['placeholder'] = 'Price'
        self.fields['price'].widget.attrs['min'] = 0
        self.fields['price'].widget.attrs['step'] = 'any'
        self.fields['quantity'].widget.attrs['min'] = 0




class ImageForm(forms.ModelForm):
    class Meta:
        model = ProductsImages
        fields = ["image"]


class CartItemForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['quantity']
