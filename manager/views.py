from django.shortcuts import render
from django.views.generic import TemplateView


class HomePage(TemplateView):
    template_name = "manager/homepage.html"


class AboutPage(TemplateView):
    template_name = "manager/about_page.html"


def error_403(request, exception):
    return render(request, "main/error_403.html", status=403, context={"exception": exception})


def error_404(request, exception):
    return render(request, "main/error_404.html", status=404, context={"exception": exception})


def error_500(request):
    return render(request, "main/error_500.html", status=500)
