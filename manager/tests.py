from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .models import Company, Offer, RecruitmentStep, StepType
from .views import OfferCreateView, RecruitmentStepCreateView, RecruitmentStepUpdateView

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


class TestingBase:
    def setUp(self):
        self.client = Client()

        self.password = "VeryLongAndS3CUREPa$$word!23"
        self.user = User.objects.create_user(username="test_user", email="test@dev.dev", password=self.password)
        self.offer = Offer.objects.create(title="Test Offer", developer=self.user)
        self.company = Company.objects.create(name="Test company", added_by=self.user)
        self.step = RecruitmentStep.objects.create(offer=self.offer)

        self.password2 = "OtherLongAndS3CUREPa$$word!@"
        self.other_user = User.objects.create_user(username="user2", email="t35t@dev.dev", password=self.password2)

        self.step_type = StepType.objects.create(name="Test type", added_by=self.user)

    def log_user(self, email=None, password=None):
        user_is_logged = self.client.login(
            username=email or self.user.email,
            password=password or self.password,
        )
        self.assertTrue(user_is_logged)


class OfferCreateViewTestCase(TestingBase, TestCase):
    def test_create_view_with_not_authenticated_user(self):
        response = self.client.get(reverse("offer-create"))
        self.assertEqual(response.status_code, 302)

    def test_create_view_with_authenticated_user_and_owner_of_offer(self):
        self.log_user()
        response = self.client.get(reverse("offer-create"))
        self.assertEqual(response.status_code, 200)

    def test_form_valid(self):
        self.log_user()
        response = self.client.post(
            reverse("offer-create"),
            data={"title": "New test offer", "company": self.company.id},
        )
        self.assertEqual(response.status_code, 302)
        offer = Offer.objects.latest("id")
        self.assertEqual(offer.title, "New test offer")

    def test_get_success_url(self):
        view = OfferCreateView()
        view.object = Offer.objects.create(title="New test offer", company=self.company, developer=self.user)
        self.assertEqual(view.get_success_url(), reverse("offer-list"))


class RecruitmentStepCreateViewTestCase(TestingBase, TestCase):
    def test_create_view_with_not_authenticated_user(self):
        response = self.client.get(reverse("step-create", kwargs={"offer_id": self.offer.id}))
        self.assertEqual(response.status_code, 302)

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
            data={"type": self.step_type.id, "offer_id": self.offer.id},
        )
        self.assertEqual(response.status_code, 302)
        step = RecruitmentStep.objects.latest("id")
        self.assertEqual(step.type, self.step_type)

    def test_get_success_url(self):
        view = RecruitmentStepCreateView()
        view.object = RecruitmentStep.objects.create(offer=self.offer)
        self.assertEqual(view.get_success_url(), reverse("offer-list"))


class RecruitmentStepUpdateViewTestCase(TestingBase, TestCase):
    def test_update_view_with_not_authenticated_user(self):
        response = self.client.get(reverse("step-update", kwargs={"pk": self.step.id}))
        self.assertEqual(response.status_code, 302)

    def test_update_view_with_authenticated_user_and_owner_of_offer(self):
        self.log_user()
        response = self.client.get(reverse("step-update", kwargs={"pk": self.step.id}))
        self.assertEqual(response.status_code, 200)

    def test_create_view_with_authenticated_user_and_not_owner_of_offer(self):
        self.log_user(email=self.other_user.email, password=self.password2)
        response = self.client.get(reverse("step-update", kwargs={"pk": self.step.id}))
        self.assertEqual(response.status_code, 403)

    def test_form_valid(self):
        self.log_user()
        response = self.client.post(
            reverse("step-update", kwargs={"pk": self.step.id}),
            data={"type": self.step_type.id},
        )
        self.assertEqual(response.status_code, 302)
        step = RecruitmentStep.objects.latest("id")
        self.assertEqual(step.type, self.step_type)

    def test_get_success_url(self):
        view = RecruitmentStepUpdateView()
        view.object = self.step
        self.assertEqual(view.get_success_url(), reverse("offer-list"))


class RecruitmentStepChangeStatusViewsTestCase(TestingBase, TestCase):
    def set_planned(self):
        self.step.status = self.step.Statuses.PLANNED
        self.step.save()

    def test_signal_setting_status_to_planned_after_creating(self):
        new_step = RecruitmentStep.objects.create(offer=self.offer, scheduled_on=timezone.now() + timezone.timedelta(days=1))
        self.assertEqual(new_step.status, RecruitmentStep.Statuses.PLANNED)

    def test_signal_changing_status_to_planned_after_scheduling(self):
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.CREATED)
        self.step.scheduled_on = timezone.now() + timezone.timedelta(days=1)
        self.step.save()
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.PLANNED)

    def test_change_status_unauthorised_user(self):
        self.set_planned()
        self.client.get(
            reverse("step-finish", kwargs={"pk": self.step.id})
        )
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.PLANNED)

    def test_change_status_user_that_is_not_offer_developer(self):
        self.set_planned()
        self.log_user()
        self.client.get(
            reverse("step-finish", kwargs={"pk": self.step.id})
        )
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.PLANNED)

    def test_change_status_finish_step(self):
        self.set_planned()
        self.log_user(email=self.other_user.email, password=self.password2)
        self.client.get(
            reverse("step-finish", kwargs={"pk": self.step.id})
        )
        self.step.refresh_from_db()
        self.assertNotEqual(self.step.status, RecruitmentStep.Statuses.FINISHED)

    def test_change_status_accept_step(self):
        self.set_planned()
        self.log_user()
        self.client.get(
            reverse("step-accept", kwargs={"pk": self.step.id})
        )
        self.step.refresh_from_db()
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.SUCCESS)

    def test_change_status_reject_step(self):
        self.set_planned()
        self.log_user()
        self.client.get(
            reverse("step-reject", kwargs={"pk": self.step.id})
        )
        self.step.refresh_from_db()
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.NEGATIVE)

    def test_change_status_resign_step(self):
        self.set_planned()
        self.log_user()
        self.client.get(
            reverse("step-resign", kwargs={"pk": self.step.id})
        )
        self.step.refresh_from_db()
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.RESIGNED)
