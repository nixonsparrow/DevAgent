from django import forms
from django.forms import DateTimeInput

from manager.models import Company, Offer, RecruitmentStep


class OfferCreateForm(forms.ModelForm):
    new_company = forms.CharField(max_length=64, strip=True, empty_value="")

    def __init__(self, *args, **kwargs):
        if "request_user" in kwargs:
            self.request_user = kwargs.pop("request_user")
        super().__init__(*args, **kwargs)

    class Meta:
        model = Offer
        fields = "__all__"
        exclude = ["status", "developer", "application_sent_on"]

    field_order = ["company", "new_company", "title"]

    def clean(self):
        cleaned_data = super().clean()
        if "new_company" in cleaned_data.keys():
            cleaned_data.update(
                {"company": Company.objects.create(name=cleaned_data.get("new_company"), added_by=self.request_user)}
            )
            self.errors.pop("company", None)
        elif "company" in cleaned_data.keys():
            self.errors.pop("new_company", None)
        return cleaned_data


class OfferUpdateForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = "__all__"
        exclude = ["developer", "application_sent_on"]

    field_order = ["company", "title"]


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = "__all__"
        exclude = ["added_by"]


class RecruitmentStepForm(forms.ModelForm):
    class Meta:
        model = RecruitmentStep
        fields = "__all__"
        exclude = ["offer", "status"]
        widgets = {
            "scheduled_on": DateTimeInput(attrs={"type": "datetime-local", "interval": 15}),
        }
