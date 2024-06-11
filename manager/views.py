from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from manager.forms import (
    CompanyForm,
    OfferCreateForm,
    OfferUpdateForm,
    RecruitmentStepForm,
)
from manager.models import Company, Offer, RecruitmentStep


class HomePage(TemplateView):
    template_name = "manager/homepage.html"


class AboutPage(TemplateView):
    template_name = "manager/about_page.html"


def error_403(request, exception):
    return render(
        request,
        "main/error_403.html",
        status=403,
        context={"exception": exception},
    )


def error_404(request, exception):
    return render(
        request,
        "main/error_404.html",
        status=404,
        context={"exception": exception},
    )


def error_500(request):
    return render(request, "main/error_500.html", status=500)


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    context_object_name = "companies"
    ordering = ["-updated_on", "-created_on"]
    extra_context = {"title": _("Company list")}

    def get_queryset(self):
        return self.model.objects.filter(added_by=self.request.user)


class CompanyCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    extra_context = {"title": _("Add new company"), "action": "create"}

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("company-list")

    def get_success_message(self, cleaned_data):
        return f"Company {self.object.name} has been created successfully."


class CompanyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    extra_context = {"title": _("Update Company"), "action": "update"}

    def test_func(self):
        company = self.get_object()
        if company.added_by == self.request.user:
            return True
        return False

    def get_success_url(self):
        return reverse_lazy("company-list")

    def get_success_message(self, cleaned_data):
        return f"Company {self.object.name} has been updated successfully."


class OfferDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Offer
    context_object_name = "offer"
    extra_context = {"title": _("Offer details")}

    def test_func(self):
        offer = self.get_object()
        if self.request.user == offer.developer:
            return True
        return False


class OfferListView(LoginRequiredMixin, ListView):
    model = Offer
    context_object_name = "offers"
    ordering = ["-updated_on", "-created_on"]
    extra_context = {"title": _("Offers list")}

    def get_queryset(self):
        return self.model.objects.filter(developer=self.request.user, status__in=self.model.statuses_active())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "archived": self.model.objects.filter(developer=self.request.user).exclude(
                    status__in=self.model.statuses_active()
                )
            }
        )
        return context


class OfferCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Offer
    form_class = OfferCreateForm
    extra_context = {"title": _("Add new offer"), "action": "create"}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"request_user": self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.developer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("offer-list")

    def get_success_message(self, cleaned_data):
        return f"Offer for {self.object.title} ({self.object.company}) has been created successfully."


class OfferUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Offer
    form_class = OfferUpdateForm
    extra_context = {"title": _("Update Offer"), "action": "update"}

    def test_func(self):
        offer = self.get_object()
        if self.request.user == offer.developer:
            return True
        return False

    def get_success_url(self):
        return reverse_lazy("offer-list")

    def get_success_message(self, cleaned_data):
        return f"Offer for {self.object.title} ({self.object.company}) has been updated successfully."


class OfferSendView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Offer
    fields = ["status"]

    def test_func(self):
        offer = self.get_object()
        if self.request.user == offer.developer and offer.status == Offer.Statuses.CREATED:
            return True
        return False

    def get(self, request, *args, **kwargs):
        offer = self.get_object()
        offer.status = Offer.Statuses.APPLICATION_SENT
        offer.application_sent_on = timezone.now()
        offer.save(update_fields=["status", "updated_on", "application_sent_on"])
        return redirect("offer-list")


class OfferSignContractView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Offer
    fields = ["status"]

    def test_func(self):
        offer = self.get_object()
        if (
            self.request.user == offer.developer
            and offer.status == Offer.Statuses.ACTIVE
            and offer.latest_step.status == RecruitmentStep.Statuses.SUCCESS
        ):
            return True
        return False

    def get(self, request, *args, **kwargs):
        offer = self.get_object()
        offer.status = Offer.Statuses.CONTRACT_SIGNED
        offer.application_sent_on = timezone.now()
        offer.save(update_fields=["status", "updated_on", "application_sent_on"])
        return redirect("offer-list")


class OfferResignView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Offer
    fields = ["status"]

    def test_func(self):
        offer = self.get_object()
        if self.request.user == offer.developer:
            return True
        return False

    def get(self, request, *args, **kwargs):
        offer = self.get_object()
        offer.status = Offer.Statuses.RESIGNED
        offer.application_sent_on = timezone.now()
        offer.save(update_fields=["status", "updated_on", "application_sent_on"])
        return redirect("offer-list")


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


class RecruitmentStepFormViewBase(LoginRequiredMixin, UserPassesTestMixin):
    model = RecruitmentStep
    form_class = RecruitmentStepForm
    template_name = "manager/step_form.html"
    context_object_name = "step"

    def get_success_url(self):
        return reverse_lazy("offer-list")


class RecruitmentStepCreateView(RecruitmentStepFormViewBase, CreateView):
    extra_context = {"title": _("Add new Recruitment Step")}

    def test_func(self):
        offer = get_object_or_404(Offer, id=self.kwargs.get("offer_id"))
        if self.request.user == offer.developer:
            return True
        return False

    def form_valid(self, form):
        form.instance.offer = get_object_or_404(Offer, id=self.kwargs.get("offer_id"))
        return super().form_valid(form)


class RecruitmentStepUpdateView(RecruitmentStepFormViewBase, UpdateView):
    extra_context = {"title": _("Recruitment Step update")}

    def test_func(self):
        step = get_object_or_404(RecruitmentStep, id=self.kwargs.get("pk"))
        if self.request.user == step.offer.developer:
            return True
        return False


class RecruitmentStepChangeStatusBaseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Base View for all RecruitmentStep status change Views. Inheriting View must have its own attributes:
    statuses_from (tuple of RecruitmentStep.Status statuses)
    and status_to (single object RecruitmentStep.Status status)"""

    model = RecruitmentStep
    fields = ["status"]

    # Mandatory attributes in a child view
    statuses_from = None
    status_to = None

    def test_func(self):
        step = self.get_object()
        if self.request.user == step.offer.developer:
            return True
        return False

    def get(self, request, *args, **kwargs):
        if not self.status_to or not self.statuses_from:
            raise NotImplementedError(f"{self} needs to have both status_to and statuses_from set.")

        if (step := self.get_object()).status in self.statuses_from:
            step.status = self.status_to
            step.save(update_fields=["status", "updated_on"])
        return redirect("offer-list")

    def is_step_valid(self):
        step = self.get_object()
        if step.status in self.statuses_from:
            return step


class RecruitmentStepFinishView(RecruitmentStepChangeStatusBaseView):
    statuses_from = (RecruitmentStep.Statuses.PLANNED,)
    status_to = RecruitmentStep.Statuses.FINISHED


class RecruitmentStepAcceptView(RecruitmentStepChangeStatusBaseView):
    statuses_from = (
        RecruitmentStep.Statuses.CREATED,
        RecruitmentStep.Statuses.PLANNED,
        RecruitmentStep.Statuses.FINISHED,
    )
    status_to = RecruitmentStep.Statuses.SUCCESS


class RecruitmentStepRejectView(RecruitmentStepChangeStatusBaseView):
    statuses_from = (
        RecruitmentStep.Statuses.CREATED,
        RecruitmentStep.Statuses.PLANNED,
        RecruitmentStep.Statuses.FINISHED,
    )
    status_to = RecruitmentStep.Statuses.NEGATIVE


class RecruitmentStepResignView(RecruitmentStepChangeStatusBaseView):
    statuses_from = (
        RecruitmentStep.Statuses.CREATED,
        RecruitmentStep.Statuses.PLANNED,
        RecruitmentStep.Statuses.FINISHED,
    )
    status_to = RecruitmentStep.Statuses.RESIGNED
