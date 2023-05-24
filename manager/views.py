from django.shortcuts import render
from django.views.generic import TemplateView


class HomePage(TemplateView):
    template_name = "manager/homepage.html"


class AboutPage(TemplateView):
    template_name = "manager/about_page.html"
