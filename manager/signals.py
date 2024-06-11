from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Offer, RecruitmentStep


@receiver(pre_save, sender=RecruitmentStep)
def change_status_to_planned_if_scheduled(sender, instance, **kwargs):
    if instance.status == RecruitmentStep.Statuses.CREATED and instance.scheduled_on:
        instance.status = RecruitmentStep.Statuses.PLANNED


@receiver(post_save, sender=RecruitmentStep)
def change_offer_status(sender, instance, **kwargs):
    if instance.status in [RecruitmentStep.Statuses.CREATED, RecruitmentStep.Statuses.PLANNED] and instance.offer.status in [
        Offer.Statuses.CREATED,
        Offer.Statuses.APPLICATION_SENT,
    ]:
        instance.offer.status = Offer.Statuses.ACTIVE
        instance.offer.save()

    if instance.status == RecruitmentStep.Statuses.NEGATIVE and instance.offer.status != Offer.Statuses.NEGATIVE:
        instance.offer.status = Offer.Statuses.NEGATIVE
        instance.offer.save()

    if instance.status == RecruitmentStep.Statuses.RESIGNED and instance.offer.status != Offer.Statuses.RESIGNED:
        instance.offer.status = Offer.Statuses.RESIGNED
        instance.offer.save()


@receiver(post_save, sender=Offer)
def offer_resign_update_last_step_status(sender, instance, **kwargs):
    if instance.status == Offer.Statuses.RESIGNED and instance.latest_step and instance.latest_step.status in (RecruitmentStep.Statuses.CREATED, RecruitmentStep.Statuses.PLANNED, RecruitmentStep.Statuses.FINISHED):
        latest_step = instance.latest_step
        latest_step.status = RecruitmentStep.Statuses.RESIGNED
        latest_step.save(update_fields=["status", "updated_on"])
