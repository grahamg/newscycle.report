from django.urls import path, include
from django.contrib.auth import views as auth_views
from user import views as user_views
from .forms import CustomAuthenticationForm

urlpatterns = [
    path('', user_views.index, name='auth'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(authentication_form=CustomAuthenticationForm, template_name='user/login.html'), name='login'),
    path('logout/', user_views.custom_signout, name='logout'),
]