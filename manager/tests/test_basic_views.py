from django.test import TestCase
from django.urls import reverse_lazy


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
