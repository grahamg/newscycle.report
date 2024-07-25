from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()

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
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-black rounded-md', 'autocomplete': 'new-password'}),
        help_text='Your password must be at least 8 characters long and should not be entirely numeric.',
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-black rounded-md', 'autocomplete': 'new-password'}),
        help_text='Enter the same password as above, for verification.'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-black rounded-md'}),
            'email': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-black rounded-md'}),
        }