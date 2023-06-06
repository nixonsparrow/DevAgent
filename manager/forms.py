from django import forms
from django.forms import DateTimeInput

from manager.models import Offer, RecruitmentStep


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = "__all__"
        exclude = ["status", "developer", "application_sent_on"]


class RecruitmentStepForm(forms.ModelForm):
    class Meta:
        model = RecruitmentStep
        fields = "__all__"
        exclude = ["offer", "status"]
        widgets = {
            "scheduled_on": DateTimeInput(attrs={"type": "datetime-local"}),
        }
