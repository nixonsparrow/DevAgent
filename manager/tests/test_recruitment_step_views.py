from django.test import TestCase
from django.urls import reverse

from manager.models import RecruitmentStep
from manager.tests import TestingBase
from manager.views import RecruitmentStepCreateView, RecruitmentStepUpdateView


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
        self.assertNotEqual(step.id, self.step.id)

    def test_get_success_url(self):
        view = RecruitmentStepUpdateView()
        view.object = self.step
        self.assertEqual(view.get_success_url(), reverse("offer-list"))
