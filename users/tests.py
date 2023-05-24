from unittest import mock

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.http.request import HttpRequest
from django.test import TestCase
from django.urls.base import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from partners.forms.auth import CustomUserNameLoginForm
from partners.models import PartnerUser
from partners.views.auth import CustomUserPasswordResetView
from tests.assertions import assert_dict_contains
from tests.common.test_utils import pass_side_effect
from tests.factories import BranchFactory, PartnerFactory, PartnerUserFactory
from tests.test_utils import TestUtils
from users.models import PasswordHistory, User
from users.utils import password_expiration_time


def get_reset_password_confirm_url(user, token=None):
    token_generator = CustomUserPasswordResetView.token_generator

    if not token:
        token = token_generator.make_token(user)

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return reverse("user_password_reset_confirm", kwargs={"uidb64": uid, "token": token})


class PartnerUserViewTestCase(TestCase, TestUtils):
    def setUp(self):
        self.login()
        self.data = build(
            dict, FACTORY_CLASS=PartnerUserFactory, branch=BranchFactory.create().id, partner=PartnerFactory.create().id
        )

    def test_create_partner_user(self):
        response = self.client.post("/admin/partners/partneruser/create/", self.data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PartnerUser.objects.all().count(), 1)

    def test_created_user_is_inactive(self):
        self.client.post("/admin/partners/partneruser/create/", self.data)
        user = PartnerUser.objects.last()

        self.assertFalse(user.is_active)

    def test_edit_partner_user(self):
        partner_user = PartnerUserFactory.create()

        response = self.client.post(partner_user.get_wagtail_url("edit"), self.data)

        updated_partner_user = PartnerUser.objects.first()

        self.assertEqual(response.status_code, 302)
        assert_dict_contains(
            self.data,
            updated_partner_user.__dict__,
            {"branch": "branch_id", "partner": "partner_id"},
            ["branch", "partner", "password_expiration"],
        )


class PartnerUserAuthViewsTestCase(TestCase):
    def setUp(self):
        self.inactive_user = PartnerUserFactory.create(is_active=False, is_superuser=False)
        self.form_data = {
            "new_password1": "StrongPassTest1!",
            "new_password2": "StrongPassTest1!",
        }

    def tearDown(self):
        self.inactive_user.delete()
        return super().tearDown()

    def test_password_reset_view(self):
        user = self.inactive_user
        old_password = "OldPassword1!"  # nosec
        user.set_password(old_password)
        user.save()

        get_url = get_reset_password_confirm_url(user)
        self.client.get(get_url, follow=True)

        post_url = get_reset_password_confirm_url(user, "set-password")
        self.client.post(post_url, data=self.form_data, follow=True)
        request = HttpRequest()

        self.assertIsNone(authenticate(request, username=user.username, password=old_password))
        self.assertIsNotNone(authenticate(request, username=user.username, password=self.form_data["new_password1"]))

    def test_password_reset_view_activates_user(self):
        user = self.inactive_user
        get_url = get_reset_password_confirm_url(user)
        self.client.get(get_url, follow=True)

        post_url = get_reset_password_confirm_url(user, "set-password")
        self.client.post(post_url, data=self.form_data, follow=True)

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_password_reset_view_not_activates_once_activated_user(self):
        user = self.inactive_user
        PasswordHistory.objects.create(user=user, password="SuperSecretPw1!")  # nosec

        get_url = get_reset_password_confirm_url(user)
        self.client.get(get_url, follow=True)

        post_url = get_reset_password_confirm_url(user, "set-password")
        self.client.post(post_url, data=self.form_data, follow=True)

        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_login_view_doesnt_pass_blocked_user(self):
        blocked_user = PartnerUserFactory.create(is_active=True, is_superuser=False, is_staff=False, is_blocked=True)
        blocked_user.set_password("password")
        blocked_user.save()
        login_url = reverse("user_login")

        form_data = {"username": blocked_user.username, "password": "password", "statute": True}
        response = self.client.post(login_url, form_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, CustomUserNameLoginForm.error_messages["blocked"])

    @mock.patch.object(User, "is_new", new_callable=mock.PropertyMock(return_value=False))
    def test_login_view_passes_unblocked_user(self, mock_is_new):
        user = PartnerUserFactory.create(
            is_active=True,
            is_superuser=False,
            is_staff=False,
            is_blocked=False,
            password_expiration=password_expiration_time(),
        )
        user.set_password("password")
        user.save()

        login_url = reverse("user_login")

        form_data = {"username": user.username, "password": "password", "statute": True}
        response = self.client.post(login_url, form_data, follow=True)

        self.assertRedirects(response, f"{settings.LOGIN_REDIRECT_URL}/", target_status_code=status.HTTP_200_OK)

    @mock.patch.object(PartnerUser, "send_confirmation_email", side_effect=pass_side_effect)
    def test_password_reset_view_doesnt_send_email_to_blocked_user(self, mock_send_confirmation_email):
        blocked_user = PartnerUserFactory.create(is_active=True, is_superuser=False, is_staff=False, is_blocked=True)
        form_data = {"email": blocked_user.email}

        self.client.post(reverse("user_password_expiration"), form_data, follow=True)

        self.assertFalse(
            mock_send_confirmation_email.called,
            "Reset-password email sending function was called but should not for blocked user.",
        )


class AdminLoginViewTestCase(TestCase):
    def setUp(self) -> None:
        self.admin_site_login_url = reverse("wagtailadmin_login")

        self.staff_credentials = {"username": "admin", "password": "admin_pw"}
        self.staff_user = get_user_model().objects.create_user(
            **self.staff_credentials, email="email1@xx.pl", is_staff=True
        )

        self.ordinary_credentials = {"username": "ordinary", "password": "ordinary_pw"}
        self.ordinary_user = get_user_model().objects.create_user(
            **self.ordinary_credentials, email="email2@xx.pl", is_staff=False
        )

        return super().setUp()

    def tearDown(self) -> None:
        self.staff_user.delete()
        self.ordinary_user.delete()
        return super().tearDown()

    def test_if_staff_user_can_login_to_admin_site(self):
        response = self.client.post(self.admin_site_login_url, self.staff_credentials, follow=True)

        self.assertTrue(response.context["user"].is_authenticated)

    def test_if_staff_user_can_not_login_into_admin_site_when_bad_credentials_were_sent(self):
        invalid_credentials = {"username": self.staff_user.username, "password": "wrong_pw"}

        response = self.client.post(self.admin_site_login_url, invalid_credentials, follow=True)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_if_staff_user_is_blocked_after_several_unsuccessful_attempts(self):
        invalid_credentials = {"username": self.staff_user.username, "password": "wrong_pw"}

        # Try several times to login with invalid credentials
        for _ in range(settings.BLUEBOOSTER_AUTH_LOGIN_ATTEMPTS_LIMIT):
            self.client.post(self.admin_site_login_url, invalid_credentials, follow=True)

        # Try to login with correct credentials
        response = self.client.post(self.admin_site_login_url, self.staff_credentials, follow=True)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_if_ordinary_user_is_blocked_after_several_unsuccessful_attempts(self):
        invalid_credentials = {"username": self.ordinary_user.username, "password": "wrong_pw"}

        # Try several times to login with invalid credentials
        for _ in range(settings.BLUEBOOSTER_AUTH_LOGIN_ATTEMPTS_LIMIT):
            self.client.post(self.admin_site_login_url, invalid_credentials, follow=True)

        # Try to login with correct credentials
        response = self.client.post(self.admin_site_login_url, self.ordinary_credentials, follow=True)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_if_blocked_due_to_inactivity_staff_user_can_not_login(self):
        self.staff_user.is_blocked = True
        self.staff_user.save(update_fields=["is_blocked", "is_superuser"])

        response = self.client.post(self.admin_site_login_url, self.staff_credentials, follow=True)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_if_blocked_due_to_inactivity_super_user_can_login(self):
        self.staff_user.is_blocked = True
        self.staff_user.is_superuser = True
        self.staff_user.save(update_fields=["is_blocked", "is_superuser"])

        response = self.client.post(self.admin_site_login_url, self.staff_credentials, follow=True)
        self.assertTrue(response.context["user"].is_authenticated)
