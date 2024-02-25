from django.contrib import admin

from .models import Company, Offer, RecruitmentStep, Skill


class CompanyAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "location", "website"]


class OfferAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "developer",
        "title",
        "status",
        "earnings_range",
        "location",
        "company",
        "remote",
        "latest_step",
    ]


class RecruitmentStepAdmin(admin.ModelAdmin):
    list_display = ["id", "offer", "status", "scheduled_on"]


class SkillAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


admin.site.register(Company, CompanyAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(RecruitmentStep, RecruitmentStepAdmin)
admin.site.register(Skill, SkillAdmin)
