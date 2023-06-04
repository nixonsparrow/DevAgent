from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseManagerModel(models.Model):
    class Meta:
        abstract = True

    title = models.CharField(_("title"), max_length=64, null=False, blank=False)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Offer(BaseManagerModel):
    class Meta:
        verbose_name = _("offer")
        verbose_name_plural = _("offers")
        ordering = ["-updated_on", "-created_on"]

    class Statuses(models.IntegerChoices):
        CREATED = 0, _("Created")
        APPLICATION_SENT = 1, _("Application sent")
        ACTIVE = 2, _("Active")
        SUCCESS = 3, _("Positive response")
        CONTRACT_SIGNED = 4, _("Contract signed")
        NEGATIVE = -1, _("Negative response")
        RESIGNED = -2, _("Resigned")

    class EmploymentTypes(models.TextChoices):
        NONE = None, _("None")
        B2B = "B2B", _("Business to business")
        PERMANENT = "PERMANENT", _("Permanent")
        CONTRACT = "CONTRACT", _("Contract")

    class ExperienceLevels(models.IntegerChoices):
        NONE = 0, _("Not provided")
        JUNIOR = 1, _("Junior")
        REGULAR = 2, _("Regular")
        SENIOR = 3, _("Senior")

    status = models.SmallIntegerField(_("status"), choices=Statuses.choices, default=Statuses.CREATED)
    employment_type = models.CharField(
        _("employment type"),
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
    developer = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False, blank=False)
    company = models.ForeignKey("manager.Company", on_delete=models.SET_NULL, null=True, blank=False)
    skills_required = models.JSONField(_("skills required"), default=dict, null=False, blank=True)
    skills_optional = models.JSONField(_("skills optional"), default=dict, null=False, blank=True)
    earnings_max = models.PositiveSmallIntegerField(_("earnings max"), default=None, null=True, blank=True)
    earnings_min = models.PositiveSmallIntegerField(_("earnings min"), default=None, null=True, blank=True)
    application_sent_on = models.DateTimeField(_("application sent date and time"), default=None, null=True, blank=True)
    remote = models.BooleanField(_("remote"), default=True)
    location = models.CharField(_("location"), max_length=32, null=True, blank=True)
    description = models.TextField(_("description"), max_length=2048, null=True, blank=True)
    comments = models.TextField(_("comments"), max_length=512, null=True, blank=True)


class RecruitmentStep(BaseManagerModel):
    class Statuses(models.IntegerChoices):
        CREATED = 0, _("Created")
        PLANNED = 1, _("Planned")
        FINISHED = 2, _("Waiting for response")
        SUCCESS = 3, _("Positive response")
        NEGATIVE = -1, _("Negative response")
        RESIGNED = -2, _("Resigned")

    offer = models.ForeignKey(
        "manager.Offer",
        on_delete=models.CASCADE,
        related_name="steps",
        null=False,
        blank=False,
    )
    description = models.TextField(_("description"), max_length=2048, null=True, blank=True)
    status = models.SmallIntegerField(_("status"), choices=Statuses.choices, default=Statuses.CREATED)
    scheduled_on = models.DateTimeField(_("scheduled on"), null=True, blank=True)

    class Meta:
        verbose_name = _("recruitment step")
        verbose_name_plural = _("recruitment steps")
        ordering = ["-updated_on", "-created_on"]


class Company(BaseManagerModel):
    location = models.CharField(_("location"), max_length=32, null=True, blank=True)
    website = models.CharField(_("website"), max_length=64, null=True, blank=True)

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        ordering = ["title"]
