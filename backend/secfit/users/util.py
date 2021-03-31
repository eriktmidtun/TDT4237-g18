from rest_framework_simplejwt.tokens import Token, BlacklistMixin
from rest_framework_simplejwt.settings import api_settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from datetime import timedelta
import qrcode
import pyotp


def send_email_verification_mail(user, request):
    token = EmailVerificationToken.for_user(user)
    protocol = "https://" if request.is_secure() else "http://"
    url = protocol + \
        get_current_site(request).domain + \
        '/verify-email.html?token=' + str(token)
    mail_body = "Hi, " + user.username + \
        "! Click the link below to verify your email \n\n" + url
    return send_mail('Verify your email', mail_body, None, [user.email], fail_silently=False)


class EmailVerificationToken(BlacklistMixin, Token):
    token_type = 'email_verification'
    lifetime = timedelta(hours=1)
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        'exp',

        # Both of these claims are included even though they may be the same.
        # It seems possible that a third party token might have a custom or
        # namespaced JTI claim as well as a default "jti" claim.  In that case,
        # we wouldn't want to copy either one.
        api_settings.JTI_CLAIM,
        'jti',
    )


def generateTwoFactorURI(user, secret):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=user.username, issuer_name='Secfit')

# Can use frontend generation of qr-code image,
# see branch feat-3/two-factor-authentication


def generateQrCode(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def isCorrectTotpToken(user, inputToken):
    totp = pyotp.TOTP(user.t)


def generateSecret():
    return pyotp.random_base32()


class TOTPVerificationToken(BlacklistMixin, Token):
    token_type = 'TOTP_verification'
    lifetime = timedelta(minutes=5)
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        'exp',

        # Both of these claims are included even though they may be the same.
        # It seems possible that a third party token might have a custom or
        # namespaced JTI claim as well as a default "jti" claim.  In that case,
        # we wouldn't want to copy either one.
        api_settings.JTI_CLAIM,
        'jti',
    )
