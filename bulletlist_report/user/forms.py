from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-black rounded-md'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-black rounded-md'
        })
    )

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-2 border border-black rounded-md'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-black rounded-md'}),
            'password1': forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-black rounded-md'}),
            'password2': forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-black rounded-md'}),
        }