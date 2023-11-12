from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    organization = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    birthday = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    registration_tokens = models.JSONField(default=list)
    subscription = models.CharField(max_length=100, blank=True)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    # Add any more fields you need

    def __str__(self):
        return self.user.email


class Confirmation(models.Model):
    email = models.EmailField()
    hashed_password = models.CharField(max_length=255)  # Adjust the max_length as appropriate
    confirmation_token = models.CharField(max_length=255)  # Adjust the max_length as appropriate
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email