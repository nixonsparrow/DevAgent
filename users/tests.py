import time

from django.test import TestCase
from users.models import User
from django.urls import reverse_lazy, reverse
from django.core import mail


class ProfilePageTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='TestUser', password='TestPassword123!@#')
        self.response = self.client.get(reverse_lazy('profile'))

    def test_login(self):
        self.client.login(username='TestUser', password='TestPassword123!@#')
        response = self.client.get(reverse_lazy('profile'))
        self.assertEqual(response.status_code, 200)

    def test_uses_proper_template_only_logged_in(self):
        self.assertTemplateNotUsed(self.response, 'users/profile.html')

        self.client.login(username='TestUser', password='TestPassword123!@#')
        response_after_login = self.client.get(reverse_lazy('profile'))
        self.assertTemplateUsed(response_after_login, 'users/profile.html')


class PasswordResetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='TestUser', password='TestPassword123!@#', email='testuser@gmail.com')

    def test_template_used(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0], 'users/password_reset.html')

    def test_password_reset(self):
        # post the response with our "email address"
        response = self.client.post(reverse('password_reset'), {'email': 'testuser@gmail.com'})
        self.assertEqual(response.status_code, 302)
        # check email response
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password reset on testserver')

        # get the token and userid from the response
        token = response.context[0]['token']
        uid = response.context[0]['uid']

        # Now we can use the token to get the password change form
        response = self.client.get(reverse('password_reset_confirm', kwargs={'token': token, 'uidb64': uid}))
        self.assertRedirects(response, reverse('password_reset_confirm', kwargs={'token': 'set-password', 'uidb64': uid}),
                             status_code=302, target_status_code=200, fetch_redirect_response=True)
