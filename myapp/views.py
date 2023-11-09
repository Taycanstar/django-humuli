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




def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
    if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User is not active until they confirm their email.
            user.save()
            
            # Create a UserProfile instance for the new user
            profile = UserProfile(
                user=user,
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                birthday=form.cleaned_data.get('birthday'),
                phone_number=form.cleaned_data.get('phone_number'),
                subscription="standard"
                # Fill in the additional fields from the form
            )
            profile.save()

            # Generate a one-time use token to verify the user's email address
            verification_token = secrets.token_hex(20)
            # Save the token with the user or profile for later verification

            # Send an email to the user with the token in a link they can click to verify
            verify_url = request.build_absolute_uri(
                reverse('your_verify_email_view', args=[verification_token])
            )
            send_mail(
                'Verify your account',
                f'Please click the following link to verify your account: {verify_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            # Redirect to a 'check your email' page or inform the user to check their email
            return redirect('check_your_email_page')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


@csrf_exempt  # Use this decorator to exempt the view from CSRF verification.
@require_http_methods(["POST"])  # This view will only accept POST requests.
def verify_email(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')
    confirmationToken = secrets.token_hex(20)

    # Hash the password
    hashed_password = make_password(password)

    # Create a confirmation instance
    confirmation = Confirmation(
        email=email,
        hashed_password=hashed_password,
        confirmation_token=confirmationToken,
    )

    # Save the confirmation instance
    confirmation.save()

    # Prepare and send the verification email
    subject = "Verify Your Email"
    frontend_url = config('FRONTEND_URL')
    message = (
        f"To continue setting up your Humuli account, please click the following link "
        f"to confirm your email: {frontend_url}/onboarding/details?"
        f"token={confirmationToken}&email={email}"
    )
    sender = config('EMAIL_SENDER')
    token = config('ONBOARDING_EMAIL_SERVER_TOKEN')

    send_email_via_postmark(subject, message, sender, [email], token)

    # Return a success response
    return JsonResponse({'message': 'Verification email sent successfully.'})
