from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseManagerModel(models.Model):
    class Meta:
        abstract = True

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Offer(BaseManagerModel):
    class Meta:
        verbose_name = _("offer")
        verbose_name_plural = _("offers")
        ordering = ["-updated_on", "-created_on"]

    class EmploymentTypes(models.TextChoices):
        NONE = None, _("None")
        B2B = "B2B", _("Business to business")
        PERMANENT = "PERMANENT", _("Permanent")
        CONTRACT = "CONTRACT", _("Contract")

    class Status(models.IntegerChoices):
        CREATED = 0, _("Created")
        APPLICATION_SENT = 1, _("Application sent")
        ACTIVE = 2, _("Active")
        SUCCESS = 3, _("Positive response")
        CONTRACT_SIGNED = 4, _("Contract signed")
        NEGATIVE = -1, _("Negative response")
        DECLINED = -2, _("Declined")

    class ExperienceLevels(models.IntegerChoices):
        NONE = 0, _("Not provided")
        JUNIOR = 1, _("Junior")
        REGULAR = 2, _("Regular")
        SENIOR = 3, _("Senior")

    title = models.CharField(_("title"), max_length=64, null=False, blank=False)
    skills_required = models.JSONField(_("skills required"), default=dict, null=False, blank=True)
    skills_optional = models.JSONField(_("skills optional"), default=dict, null=False, blank=True)
    earnings_max = models.PositiveSmallIntegerField(_("earnings max"), default=None, null=True, blank=True)
    earnings_min = models.PositiveSmallIntegerField(_("earnings min"), default=None, null=True, blank=True)
    preferred_employment_mode = models.CharField(
        _("preferred employment type"),
        default=EmploymentTypes.NONE,
        choices=EmploymentTypes.choices,
        max_length=16,
        null=True,
    )
    level = models.PositiveSmallIntegerField(
        _("experience level"),
        default=ExperienceLevels.NONE,
        choices=ExperienceLevels.choices,
        null=False,
        blank=False,
    )
    application_sent = models.DateTimeField(_("application sent date and time"), default=None, null=True, blank=True)
    remote = models.BooleanField(_("remote"), default=True)
    location = models.CharField(_("location"), max_length=32, null=True, blank=True)
    description = models.TextField(_("description"), max_length=2048, null=True, blank=True)


class RecruitmentStep(BaseManagerModel):
    offer = models.ForeignKey(
        "manager.Offer",
        on_delete=models.CASCADE,
        related_name="steps",
        null=False,
        blank=False,
    )
    name = models.CharField(_("step name"), max_length=32, null=False, blank=False)

    class Meta:
        verbose_name = _("recruitment step")
        verbose_name_plural = _("recruitment steps")
        ordering = ["-updated_on", "-created_on"]
