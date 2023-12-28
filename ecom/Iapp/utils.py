import pyotp
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings


def send_otp(request):
    totp = pyotp.TOTP(pyotp.random_base32(),interval=60)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    valid_date = datetime.now() + timedelta(minutes=1)
    request.session['otp_valid_date'] = str(valid_date)

    ###change this
    user_data = request.session.get('user_data', {})
    user_email = user_data.get('email', None)
    if user_email:
        # Subject and message for the email
        subject = 'Verification OTP for Registration'
        message = f'Your OTP for registration is: {otp}. Please enter this OTP to complete the registration process.'

        # Sender email address
        from_email = settings.EMAIL_HOST_USER

        # Recipient email address
        recipient_list = [user_email]

        try:
            # Send the email
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            # Save the OTP in the session for verification
            request.session['registration_otp'] = otp

            

        except Exception as e:
            pass

    else:
        pass
    
    print(f'Your OTP is {otp}')