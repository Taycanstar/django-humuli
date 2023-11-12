from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import UserRegisterForm
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
import secrets
from .models import UserProfile
from .email import send_email_via_postmark
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.http import JsonResponse
from decouple import config
from .models import Confirmation
from django.contrib.auth.hashers import make_password
import secrets
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from .text import send_verification_code, verify_number
import traceback
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    confirmationToken = secrets.token_hex(20)

    # Create a new User instance. Django hashes the password internally here
    user = User.objects.create_user(username=email, email=email, password=password)

    # Create a UserProfile instance with email_verified set to False
    user_profile = UserProfile(
        user=user,
        email=email,
        email_verified=False,
        phone_verified=False,
    )
    user_profile.save()

    # Create a confirmation instance for email verification
    confirmation = Confirmation(
        email=email,
        confirmation_token=confirmationToken,
    )
    confirmation.save()

    # Prepare and send the verification email
    subject = "Verify Your Email"
    frontend_url = config('FRONTEND_URL')
    message = f"To continue setting up your Humuli account, please click the following link to confirm your email: {frontend_url}/onboarding/info?token={confirmationToken}&email={email}"
    
    sender = config('EMAIL_SENDER')
    token = config('ONBOARDING_EMAIL_SERVER_TOKEN')

    send_email_via_postmark(subject, message, sender, [email], token)

    # Return a success response
    return JsonResponse({'message': 'Verification email sent successfully.'})

@csrf_exempt
@require_http_methods(["PUT"])
def add_info(request):
    try:
        # Load data from the request
        data = json.loads(request.body)
        email = data.get('email')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        organization = data.get('organization')
        birthday = data.get('birthday') 
        phone_number = data.get('phoneNumber')

        # Find the user by email
        user = User.objects.get(email=email)

        # Retrieve or create the user's profile
        profile, created = UserProfile.objects.get_or_create(user=user)

        # Update the profile with new data
        if first_name:
            profile.first_name = first_name
        if last_name:
            profile.last_name = last_name
        if organization is not None:  # Allow empty string for organization
            profile.organization = organization
        if birthday:
            birthday_date = datetime.strptime(birthday, '%m/%d/%Y').date()
            profile.birthday = birthday_date
        if phone_number:
            profile.phone_number = phone_number   

        # Save the updated profile
        profile.save()

           # Send verification SMS
        if phone_number:
            send_verification_code(phone_number)  # Send SMS using Twilio

        return JsonResponse({'message': 'User profile updated successfully and SMS sent.'})

    except ObjectDoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def confirm_email(request):
    try:
        data = json.loads(request.body)
        confirmation_token = data.get('confirmationToken')
        email = data.get('email')

        # Retrieve the confirmation instance
        try:
            confirmation = Confirmation.objects.get(confirmation_token=confirmation_token)
        except Confirmation.DoesNotExist:
            return JsonResponse({'message': 'Confirmation token not found'}, status=404)

        # Check if email matches
        if confirmation.email != email:
            return JsonResponse({'message': 'Invalid confirmation token or email'}, status=401)

        # Find or create the user
        user, created = User.objects.get_or_create(email=email)

        # Update or create the user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.email_verified = True
        profile.save()

        # Delete the confirmation instance
        confirmation.delete()

        return JsonResponse({'message': 'User confirmed and email verified'})

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:

        traceback.print_exc()  # This will print the full traceback to your console or logs
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def resend_email(request):
    data = json.loads(request.body)
    email = data.get('email')

    # Retrieve the user and their associated UserProfile
    try:
        user = User.objects.get(email=email)
        user_profile = UserProfile.objects.get(user=user)
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        return JsonResponse({'error': 'User not found.'}, status=404)

    # Check if the user's email is already verified
    if user_profile.email_verified:
        return JsonResponse({'message': 'Email is already verified.'})

    # Retrieve the existing confirmation token
    try:
        confirmation = Confirmation.objects.get(email=email)
        confirmationToken = confirmation.confirmation_token
    except Confirmation.DoesNotExist:
        return JsonResponse({'error': 'Confirmation token not found.'}, status=404)

    # Prepare and resend the verification email
    subject = "Verify Your Email"
    frontend_url = config('FRONTEND_URL')
    message = f"To continue setting up your Humuli account, please click the following link to confirm your email: {frontend_url}/onboarding/info?token={confirmationToken}&email={email}"
    
    sender = config('EMAIL_SENDER')
    token = config('ONBOARDING_EMAIL_SERVER_TOKEN')

    send_email_via_postmark(subject, message, sender, [email], token)

    # Return a success response
    return JsonResponse({'message': 'Verification email resent successfully.'})


@csrf_exempt
@require_http_methods(["POST"])
def resend_code(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')

        # Retrieve the user's profile
      
        try:
            user = User.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile not found'}, status=404)

        # Resend the OTP code
        phone_number = user_profile.phone_number
        if phone_number:
            send_verification_code(phone_number)  # Replace with your OTP sending logic
            return JsonResponse({'message': 'OTP code resent successfully'})
        else:
            return JsonResponse({'error': 'Phone number not found'}, status=404)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def confirm_phone_number(request):
    try:
        data = json.loads(request.body)
        phone_number = data.get('phoneNumber')
        email = data.get('email')
        otp_code = data.get('code')

        verification_check = verify_number(phone_number, otp_code)

        try:
            user = User.objects.get(email=email)
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile not found'}, status=404)
        
        if verification_check.status == "approved":
            user_profile.phone_verified = True
            user_profile.save()
            return JsonResponse({'message': 'Phone number verified.'})
        else:
            return JsonResponse({'message': 'Invalid verification code.'}, status=400)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
    

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        # Parse the request body to get the credentials
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Authenticate the user
        user = authenticate(username=email, password=password)

        if user is not None:
            # User is authenticated, proceed to generate and return the token
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({
                'message': 'Login successful',
                'token': token.key,
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                    # Add other user fields you need
                }
            })
        else:
            # Authentication failed
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({'error': str(e)}, status=500)