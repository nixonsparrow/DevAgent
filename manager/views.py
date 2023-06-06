from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from manager.forms import OfferForm, RecruitmentStepForm
from manager.models import Offer, RecruitmentStep


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


class OfferDetailView(LoginRequiredMixin, DetailView):
    model = Offer
    context_object_name = "offer"
    extra_context = {"title": _("Offer details")}


class OfferListView(ListView):
    model = Offer
    context_object_name = "offers"
    ordering = ["-updated_on", "-created_on"]
    extra_context = {"title": _("Offers list")}


class OfferCreateView(LoginRequiredMixin, CreateView):
    model = Offer
    form_class = OfferForm
    extra_context = {"title": _("Add new offer")}

    def form_valid(self, form):
        form.instance.developer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("offer-update", kwargs={"pk": self.object.id})


class OfferUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Offer
    form_class = OfferForm
    extra_context = {"title": _("Update Offer")}

    def test_func(self):
        offer = self.get_object()
        if self.request.user == offer.developer:
            return True
        return False

    def get_success_url(self):
        return reverse_lazy("offer-update", kwargs={"pk": self.object.id})


class RecruitmentStepDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = RecruitmentStep
    context_object_name = "step"
    template_name = "manager/step_detail.html"
    extra_context = {"title": _("Recruitment Step details")}

    def test_func(self):
        step = self.get_object()
        if self.request.user == step.offer.developer:
            return True
        return False


class RecruitmentStepCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = RecruitmentStep
    form_class = RecruitmentStepForm
    template_name = "manager/step_form.html"
    context_object_name = "step"
    extra_context = {"title": _("Add new Recruitment Step")}

    def test_func(self):
        offer = get_object_or_404(Offer, id=self.kwargs.get("offer_id"))
        if self.request.user == offer.developer:
            return True
        return False

    def form_valid(self, form):
        form.instance.offer = get_object_or_404(Offer, id=self.kwargs.get("offer_id"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("step-update", kwargs={"pk": self.object.id})


class RecruitmentStepUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = RecruitmentStep
    form_class = RecruitmentStepForm
    template_name = "manager/step_form.html"
    extra_context = {"title": _("Recruitment Step update")}

    def test_func(self):
        step = self.get_object()
        if self.request.user == step.offer.developer:
            return True
        return False

    def get_success_url(self):
        return reverse_lazy("step-update", kwargs={"pk": self.object.id})
