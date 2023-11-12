from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import UserProfile

class EmailPhoneAuthenticationBackend(BaseBackend):
    def authenticate(self, request, email=None):
        try:
            user = User.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.phone_verified:
                return user
        except User.DoesNotExist:
            return None
        except UserProfile.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
