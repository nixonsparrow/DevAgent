from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _


class BaseManagerModel(models.Model):
    """Abstract model with most common attributes and functions"""

    class Meta:
        abstract = True

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if hasattr(self, "name"):
            return self.name
        elif hasattr(self, "title"):
            return self.title
        return super().__str__()

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.__str__()}')"


class Offer(BaseManagerModel):
    """Main model of an offer that developer found and added to DB"""

    class Meta:
        verbose_name = _("offer")
        verbose_name_plural = _("offers")

    class Statuses(models.IntegerChoices):
        CREATED = 0, _("Created")
        APPLICATION_SENT = 1, _("Application sent")
        ACTIVE = 2, _("Active")
        SUCCESS = 3, _("Positive response")
        CONTRACT_SIGNED = 4, _("Contract signed")
        NEGATIVE = -1, _("Negative response")
        RESIGNED = -2, _("Resigned")

    @classmethod
    def statuses_active(cls):
        return [cls.Statuses.CREATED, cls.Statuses.APPLICATION_SENT, cls.Statuses.ACTIVE]

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

    title = models.CharField(_("title"), max_length=64, null=False, blank=False)
    status = models.SmallIntegerField(_("status"), choices=Statuses.choices, default=Statuses.CREATED)
    employment_type = models.CharField(
        _("employment type"),
        default=EmploymentTypes.NONE,
        choices=EmploymentTypes.choices,
        max_length=16,
        null=True,
        blank=True,
    )
    level = models.PositiveSmallIntegerField(
        _("experience level"),
        default=ExperienceLevels.NONE,
        choices=ExperienceLevels.choices,
        null=False,
        blank=True,
    )
    developer = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False, blank=False)
    company = models.ForeignKey("manager.Company", on_delete=models.SET_NULL, null=True, blank=False)
    skills_required = models.ManyToManyField(
        "manager.Skill",
        verbose_name=_("skills required"),
        blank=True,
        related_name="offers_required_in",
    )
    skills_optional = models.ManyToManyField(
        "manager.Skill",
        verbose_name=_("skills optional"),
        blank=True,
        related_name="offers_optional_in",
    )
    earnings_min = models.PositiveSmallIntegerField(_("earnings min"), default=None, null=True, blank=True)
    earnings_max = models.PositiveSmallIntegerField(_("earnings max"), default=None, null=True, blank=True)
    currency = models.CharField(_("currency"), max_length=8, default="PLN", blank=True, null=True)
    application_sent_on = models.DateTimeField(
        _("application sent date and time"),
        default=None,
        null=True,
        blank=True,
    )
    remote = models.BooleanField(_("remote"), default=True)
    location = models.CharField(_("location"), max_length=32, null=True, blank=True)
    description = models.TextField(_("description"), max_length=2048, null=True, blank=True)
    comments = models.TextField(_("comments"), max_length=512, null=True, blank=True)

    @property
    def status_display(self):
        """Finds and returns string value of status set"""
        return [status for status in self.Statuses.choices if self.status == status[0]][0][1]

    @property
    def latest_step(self):
        """Returns latest related RecruitmentStep"""
        return self.steps.order_by("id").last()

    @property
    def earnings_range(self):
        """Returns string range in proper format"""
        earnings = ""
        if self.earnings_min and self.earnings_max:
            earnings = f"{self.earnings_min} - {self.earnings_max}"
        elif self.earnings_min:
            earnings = f"> {self.earnings_min}"
        elif self.earnings_max:
            earnings = f"< {self.earnings_max}"

        if earnings and self.currency:
            earnings += f" {self.currency}"

        return earnings or "-"

    @property
    def is_finished(self):
        """Returns True if status is final"""
        if self.status < self.Statuses.CREATED or self.status >= self.Statuses.CONTRACT_SIGNED:
            return True
        return False


class StepType(BaseManagerModel):
    """Model for creation of individual step types for each User"""

    name = models.CharField(_("name"), max_length=32, null=False, blank=False)
    added_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=False, blank=False, related_name="step_types_added"
    )


class RecruitmentStep(BaseManagerModel):
    """Step Many-to-One model related to Offer"""

    class Statuses(models.IntegerChoices):
        CREATED = 0, _("Created")
        PLANNED = 1, _("Planned")
        FINISHED = 2, _("Waiting for response")
        SUCCESS = 3, _("Positive response")
        NEGATIVE = -1, _("Negative response")
        RESIGNED = -2, _("Resigned")

    type = models.ForeignKey("manager.StepType", on_delete=models.SET_NULL, null=True, blank=False)
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

    @property
    def status_display(self):
        """Finds and returns string value of status set"""
        return [status for status in self.Statuses.choices if self.status == status[0]][0][1]

    @property
    def has_result(self):
        """Returns True if current status is considered final result"""
        if self.status in [self.Statuses.CREATED, self.Statuses.PLANNED, self.Statuses.FINISHED]:
            return False
        return True


class Company(BaseManagerModel):
    """Company model that is the company offering the Job"""

    name = models.CharField(_("name"), max_length=64, null=False, blank=False, unique=True)
    location = models.CharField(_("location"), max_length=32, null=True, blank=True)
    website = models.CharField(_("website"), max_length=64, null=True, blank=True)
    added_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=False, blank=False, related_name="companies_added"
    )

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("companies")
        ordering = ["name"]
        constraints = [
            UniqueConstraint(
                fields=["name", "added_by"],
                name="company per user unique",
            ),
        ]


class Skill(BaseManagerModel):
    """Developer's skill"""

    name = models.CharField(_("name"), max_length=64, null=False, blank=False, unique=True)

    # TODO should we add rating here?

    class Meta:
        verbose_name = _("skill")
        verbose_name_plural = _("skills")
        ordering = ["name"]
