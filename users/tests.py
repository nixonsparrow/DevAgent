from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse, reverse_lazy

User = get_user_model()


USER = {"name": "TestUser", "pass": "TestPassword123!@#", "email": "testuser@gmail.com"}


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER.get("name"),
            email=USER.get("email"),
            password=USER.get("pass"),
        )


class ProfilePageTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse_lazy("profile"))

    def test_login_by_email(self):
        self.client.login(username=USER.get("email"), password=USER.get("pass"))
        response = self.client.get(reverse_lazy("profile"))
        self.assertEqual(response.status_code, 200)

    def test_cant_login_by_username(self):
        self.client.login(username=USER.get("username"), password=USER.get("pass"))
        response = self.client.get(reverse_lazy("profile"))
        self.assertEqual(response.status_code, 302)

    def test_uses_proper_template_only_logged_in(self):
        self.assertTemplateNotUsed(self.response, "users/profile.html")

        self.client.login(username=USER.get("email"), password=USER.get("pass"))
        response_after_login = self.client.get(reverse_lazy("profile"))
        self.assertTemplateUsed(response_after_login, "users/profile.html")


class PasswordResetTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(reverse("password_reset"))

    def test_template_used(self):
        self.assertTemplateUsed(self.response, "users/password_reset.html")

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_password_reset(self):
        # post the response with our "email address"
        response = self.client.post(reverse("password_reset"), {"email": "testuser@gmail.com"})
        self.assertEqual(response.status_code, 302)
        # check email response
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Password reset on testserver")

        # get the token and userid from the response
        token = response.context[0]["token"]
        uid = response.context[0]["uid"]

        # Now we can use the token to get the password change form
        response = self.client.get(reverse("password_reset_confirm", kwargs={"token": token, "uidb64": uid}))
        self.assertRedirects(
            response,
            reverse(
                "password_reset_confirm",
                kwargs={"token": "set-password", "uidb64": uid},
            ),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
