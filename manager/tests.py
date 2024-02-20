from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from .models import Offer, RecruitmentStep
from .views import RecruitmentStepCreateView

User = get_user_model()


class HomePageTestCase(TestCase):
    def setUp(self) -> None:
        self.response = self.client.get(reverse_lazy("homepage"))

    def test_template_used(self):
        self.assertTemplateUsed(self.response, "manager/homepage.html")

    def test_base_template_used(self):
        self.assertTemplateUsed(self.response, "main/base.html")

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)


class AboutPageTestCase(TestCase):
    def setUp(self) -> None:
        self.response = self.client.get(reverse_lazy("about-page"))

    def test_template_used(self):
        self.assertTemplateUsed(self.response, "manager/about_page.html")

    def test_base_template_used(self):
        self.assertTemplateUsed(self.response, "main/base.html")

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)


class RecruitmentStepCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.password = "VeryLongAndS3CUREPa$$word!23"
        self.user = User.objects.create_user(username="test_user", email="test@dev.dev", password=self.password)
        self.offer = Offer.objects.create(title="Test Offer", developer=self.user)

        self.password2 = "OtherLongAndS3CUREPa$$word!@"
        self.other_user = User.objects.create_user(username="user2", email="t35t@dev.dev", password=self.password2)

    def log_user(self, email=None, password=None):
        user_is_logged = self.client.login(
            username=email or self.user.email,
            password=password or self.password,
        )
        self.assertTrue(user_is_logged)

    def test_create_view_with_authenticated_user_and_owner_of_offer(self):
        self.log_user()
        response = self.client.get(reverse("step-create", kwargs={"offer_id": self.offer.id}))
        self.assertEqual(response.status_code, 200)

    def test_create_view_with_authenticated_user_and_not_owner_of_offer(self):
        self.log_user(email=self.other_user.email, password=self.password2)
        response = self.client.get(reverse("step-create", kwargs={"offer_id": self.offer.id}))
        self.assertEqual(response.status_code, 403)

    def test_form_valid(self):
        self.log_user()
        response = self.client.post(
            reverse("step-create", kwargs={"offer_id": self.offer.id}),
            {"title": "Test Step"},
        )
        self.assertEqual(response.status_code, 302)
        step = RecruitmentStep.objects.latest("id")
        self.assertEqual(step.title, "Test Step")

    def test_get_success_url(self):
        view = RecruitmentStepCreateView()
        view.object = RecruitmentStep.objects.create(offer=self.offer)
        self.assertEqual(
            view.get_success_url(),
            reverse("step-update", kwargs={"pk": view.object.id}),
        )
