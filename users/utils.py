from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

AUTH_PASSWORD_AGE = getattr(settings, "AUTH_PASSWORD_AGE", 7)


def password_expiration_time():
    return now() + timedelta(days=AUTH_PASSWORD_AGE)
