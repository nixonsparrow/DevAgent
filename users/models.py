from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from .utils import password_expiration_time


class PasswordHistory(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    user = GenericForeignKey("content_type", "object_id")

    password = models.CharField(_("password"), max_length=128)
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    class Meta:
        ordering = ["id"]
        verbose_name = _("password history")


class BaseUser(AbstractUser):
    email = models.EmailField(
        _("email address"),
        max_length=254,
        unique=True,
        error_messages={"unique": _("A user with that email address already exists.")},
    )

    password_expiration = models.DateTimeField(_("password expiration time"), default=password_expiration_time)
    passwords = GenericRelation(PasswordHistory, content_type_field="content_type", object_id_field="object_id")

    @property
    def is_new(self):
        return PasswordHistory.objects.filter(object_id=self.id).count() == 0

    def send_activation_message(self, subject, template_name=None):
        if not template_name:
            template_name = "users/account_activation.html"

        self.send_confirmation_email(subject, template_name)

    def send_confirmation_email(self, subject, template_name):
        context = {
            "email": self.email,
            "uid": urlsafe_base64_encode(force_bytes(self.pk)),
            "token": default_token_generator.make_token(self),
            "domain": settings.BASE_URL,
            "site_name": settings.BASE_URL,
            "user": self,
        }

        message = loader.render_to_string(template_name, context)
        html_message = loader.render_to_string(template_name, context)

        self.email_user(
            subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, html_message=html_message
        )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True
