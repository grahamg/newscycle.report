from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
from .forms import UserRegisterForm

def index(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        return redirect('login')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'User account was created successfully.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})

def custom_signout(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)