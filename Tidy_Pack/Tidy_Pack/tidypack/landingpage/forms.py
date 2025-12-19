from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Your Email',
        'id': 'email',
        'name': 'email',
        'required': 'required'
    }))
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Your Name',
        'id': 'username',
        'name': 'username',
        'required': 'required'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your Password',
        'id': 'password1',
        'name': 'password1',
        'required': 'required'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'id': 'password2',
        'name': 'password2',
        'required': 'required'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Your Email',
        'id': 'email',
        'name': 'email',
        'required': 'required'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your Password',
        'id': 'password',
        'name': 'password',
        'required': 'required'
    }))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not email:
            raise forms.ValidationError({'email': "Email is required."})
        if not password:
            raise forms.ValidationError({'password': "Password is required."})

        user = User.objects.filter(email=email).first()
        if user is None:
            raise forms.ValidationError({'email': "No account found with this email."})
        
        self.user_cache = authenticate(username=user.username, password=password)
        if self.user_cache is None:
            raise forms.ValidationError({'password': "Invalid email or password."})
        
        return cleaned_data

    def get_user(self):
        return self.user_cache
    
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError 


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Admin Username'}),
        error_messages={'required': 'Username is required.'}
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Admin Password'}),
        error_messages={'required': 'Password is required.'}
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = self.get_user()
            if user is None:
                raise ValidationError({'username': 'Invalid username or password.'})
            if not user.is_superuser:
                raise ValidationError({'username': 'This account is not a superuser account.'})
        return cleaned_data
    
from django import forms
from django.contrib.auth.models import User
from .models import  Order

class OrderForm(forms.Form):
    product_name = forms.CharField(max_length=100, required=True, widget=forms.HiddenInput)
    customer_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    quantity = forms.IntegerField(min_value=1, required=True)
    delivery_address = forms.CharField(widget=forms.Textarea, required=True)
    notes = forms.CharField(widget=forms.Textarea, required=False)

# forms.py (Create this file in your app if it doesn't exist)
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter product name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Enter product description'}),
        }
        labels = {
            'name': 'Product Name',
            'image': 'Product Image',
            'description': 'Description',
        }