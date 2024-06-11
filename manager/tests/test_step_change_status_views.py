from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from manager.models import RecruitmentStep
from manager.tests import TestingBase


class RecruitmentStepChangeStatusViewsTestCase(TestingBase, TestCase):
    def set_planned(self):
        self.step.status = self.step.Statuses.PLANNED
        self.step.save()

    def test_signal_setting_status_to_planned_after_creating(self):
        new_step = RecruitmentStep.objects.create(
            offer=self.offer, scheduled_on=timezone.now() + timezone.timedelta(days=1)
        )
        self.assertEqual(new_step.status, RecruitmentStep.Statuses.PLANNED)

    def test_signal_changing_status_to_planned_after_scheduling(self):
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.CREATED)
        self.step.scheduled_on = timezone.now() + timezone.timedelta(days=1)
        self.step.save()
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.PLANNED)

    def test_change_status_unauthorised_user(self):
        self.set_planned()
        self.client.get(reverse("step-finish", kwargs={"pk": self.step.id}))
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.PLANNED)

    def test_change_status_user_that_is_not_offer_developer(self):
        self.set_planned()
        self.log_user(email=self.other_user.email, password=self.password2)
        self.client.get(reverse("step-finish", kwargs={"pk": self.step.id}))
        self.step.refresh_from_db()
        self.assertNotEqual(self.step.status, RecruitmentStep.Statuses.FINISHED)

    def test_change_status_finish_step(self):
        self.set_planned()
        self.log_user()
        self.client.get(reverse("step-finish", kwargs={"pk": self.step.id}))
        self.step.refresh_from_db()
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.FINISHED)

    def test_change_status_accept_step(self):
        self.set_planned()
        self.log_user()
        self.client.get(reverse("step-accept", kwargs={"pk": self.step.id}))
        self.step.refresh_from_db()
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.SUCCESS)

    def test_change_status_reject_step(self):
        self.set_planned()
        self.log_user()
        self.client.get(reverse("step-reject", kwargs={"pk": self.step.id}))
        self.step.refresh_from_db()
        self.assertEqual(self.step.status, RecruitmentStep.Statuses.NEGATIVE)
