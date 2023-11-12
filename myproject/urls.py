"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import add_info, confirm_phone_number, signup, confirm_email, resend_email, resend_code, login_without_password, login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup, name='signup'), 
    path('add-info/', add_info, name='add_info'), 
    path('confirm-email/', confirm_email, name='confirm_email'), 
    path('resend-email/', resend_email, name='resend_email'), 
    path('resend-code/', resend_code, name='resend_code'),
    path('confirm-phone-number/', confirm_phone_number,name='confirm_phone_number'),
    path('login/', login,name='login'),
    path('login-without-password/', login_without_password,name='login_without_password'),

]