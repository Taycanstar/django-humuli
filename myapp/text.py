
import os
from twilio.rest import Client

from decouple import config

# Load Twilio credentials from environment variables
account_sid = config('TWILIO_SID')
auth_token = config('TWILIO_TOKEN')
verify_sid = config('TWILIO_VERIFY_SID')

client = Client(account_sid, auth_token)

def send_verification_code(number):
    """Send a verification code to the given phone number."""
    try:
        verification = client.verify.services(verify_sid).verifications.create(
            to=number,
            channel='sms'
        )
        return verification
    except Exception as e:
        # Handle any exceptions (log or raise)
        raise Exception(f"Failed to send verification SMS: {e}")
    
def verify_number(number, otp_code):
    """Verify the OTP code sent to the given phone number."""
    try:
        verification_check = client.verify.services(verify_sid).verification_checks.create(
            to=number,
            code=otp_code
        )
        return verification_check
    except Exception as e:
        # Handle any exceptions (log or raise)
        raise Exception(f"Failed to verify phone number: {e}")


