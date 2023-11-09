from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import UserProfile


User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

# You will use this form to update the UserProfile after creating the User.
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birthday', 'organization', 'photo', 'subscription', 
                  'phone_number', 'gender', 'email_verified', 'phone_verified', 
                  'registration_tokens']
