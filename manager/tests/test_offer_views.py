from django.test import TestCase
from django.urls import reverse_lazy

from manager.models import Offer
from manager.tests import TestingBase
from manager.views import OfferCreateView, OfferUpdateView


class OfferDetailViewTestCase(TestingBase, TestCase):
    def test_detail_view_with_not_authenticated_user(self):
        response = self.client.get(reverse_lazy("offer-detail", kwargs={"pk": self.offer.id}))
        self.assertEqual(response.status_code, 302)

    def test_detail_view_with_authenticated_user_and_not_owner_of_offer(self):
        self.log_user(email=self.other_user.email, password=self.password2)
        response = self.client.get(reverse_lazy("offer-detail", kwargs={"pk": self.offer.id}))
        self.assertEqual(response.status_code, 403)

    def test_detail_view_with_authenticated_user_and_owner_of_offer(self):
        self.log_user()
        response = self.client.get(reverse_lazy("offer-detail", kwargs={"pk": self.offer.id}))
        self.assertEqual(response.status_code, 200)


class OfferListViewTestCase(TestingBase, TestCase):
    def test_list_view_with_not_authenticated_user(self):
        response = self.client.get(reverse_lazy("offer-list"))
        self.assertEqual(response.status_code, 302)

    def test_list_view_with_authenticated_user(self):
        self.log_user()
        response = self.client.get(reverse_lazy("offer-list"))
        self.assertEqual(response.status_code, 200)

    def test_list_view_includes_user_offer(self):
        self.log_user()
        response = self.client.get(reverse_lazy("offer-list"))
        self.assertIn(self.offer, response.context_data["object_list"])

    def test_list_view_does_not_include_other_user_offer(self):
        self.log_user(email=self.other_user.email, password=self.password2)
        response = self.client.get(reverse_lazy("offer-list"))
        self.assertNotIn(self.offer, response.context_data["object_list"])


class OfferCreateViewTestCase(TestingBase, TestCase):
    def test_create_view_with_not_authenticated_user(self):
        response = self.client.get(reverse_lazy("offer-create"))
        self.assertEqual(response.status_code, 302)

    def test_create_view_with_authenticated_user(self):
        self.log_user()
        response = self.client.get(reverse_lazy("offer-create"))
        self.assertEqual(response.status_code, 200)

    def test_form_valid(self):
        self.log_user()
        response = self.client.post(
            reverse_lazy("offer-create"),
            data={"title": "New test offer", "company": self.company.id},
        )
        self.assertEqual(response.status_code, 302)
        offer = Offer.objects.latest("id")
        self.assertEqual(offer.title, "New test offer")

    def test_get_success_url(self):
        view = OfferCreateView()
        view.object = Offer.objects.create(title="New test offer", company=self.company, developer=self.user)
        self.assertEqual(view.get_success_url(), reverse_lazy("offer-list"))


class OfferUpdateViewTestCase(TestingBase, TestCase):
    def test_update_view_with_not_authenticated_user(self):
        response = self.client.get(reverse_lazy("offer-update", kwargs={"pk": self.offer.id}))
        self.assertEqual(response.status_code, 302)

    def test_update_view_with_authenticated_user_and_owner_of_offer(self):
        self.log_user()
        response = self.client.get(reverse_lazy("offer-update", kwargs={"pk": self.offer.id}))
        self.assertEqual(response.status_code, 200)

    def test_update_view_with_authenticated_user_and_not_owner_of_offer(self):
        self.log_user(email=self.other_user.email, password=self.password2)
        response = self.client.get(reverse_lazy("offer-update", kwargs={"pk": self.offer.id}))
        self.assertEqual(response.status_code, 403)

    def test_form_valid(self):
        self.log_user()
        response = self.client.post(
            reverse_lazy("offer-update", kwargs={"pk": self.offer.id}),
            {
                "title": (new_title := "Test update offer"),
                "company": self.offer.company.id,
                "status": self.offer.status,
            },
        )
        self.assertEqual(response.status_code, 302)
        offer = Offer.objects.latest("id")
        self.assertEqual(offer.title, new_title)

    def test_get_success_url(self):
        view = OfferUpdateView()
        view.object = self.offer
        self.assertEqual(view.get_success_url(), reverse_lazy("offer-list"))


class OfferSendViewTestCase(TestingBase, TestCase):
    def test_send_view_with_not_authenticated_user(self):
        response = self.client.get(reverse_lazy("offer-send", kwargs={"pk": self.offer.id}))
        self.assertEqual(response.status_code, 302)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, Offer.Statuses.CREATED)

    def test_send_view_with_authenticated_user_and_owner_of_offer(self):
        self.log_user()
        response = self.client.get(reverse_lazy("offer-send", kwargs={"pk": self.offer.id}))
        self.assertEqual(response.status_code, 302)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, Offer.Statuses.APPLICATION_SENT)

    def test_send_view_with_authenticated_user_and_not_owner_of_offer(self):
        self.log_user(email=self.other_user.email, password=self.password2)
        response = self.client.get(reverse_lazy("offer-send", kwargs={"pk": self.offer.id}))
        self.assertEqual(response.status_code, 403)

    def test_offer_status_change_to_sent(self):
        self.log_user()
        self.assertEqual(self.offer.status, Offer.Statuses.CREATED)
        self.client.get(
            reverse_lazy("offer-send", kwargs={"pk": self.offer.id}),
        )
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, Offer.Statuses.APPLICATION_SENT)

    def test_offer_status_not_change_to_sent_from_any_other_status(self):
        self.log_user()
        for status, _ in Offer.Statuses.choices:
            if status == Offer.Statuses.CREATED:
                continue

            self.offer.status = status
            self.offer.save()
            self.assertEqual(self.offer.status, status)
            response = self.client.get(
                reverse_lazy("offer-send", kwargs={"pk": self.offer.id}),
            )
            self.assertEqual(response.status_code, 403)
            self.offer.refresh_from_db()
            self.assertEqual(self.offer.status, status)
