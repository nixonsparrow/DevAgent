DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

SECRET_KEY = "yourOWNtotallySECUREsecretKEY-123456789!@#$%^&*("

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.your_domain.com"
EMAIL_PORT = 123
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "admin@your_domain.com"
EMAIL_HOST_PASSWORD = "12345!@#$%"
