from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import RecruitmentStep


@receiver(pre_save, sender=RecruitmentStep)
def change_status_to_planned_if_scheduled(sender, instance, **kwargs):
    if instance.status == RecruitmentStep.Statuses.CREATED and instance.scheduled_on:
        instance.status = RecruitmentStep.Statuses.PLANNED
