from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomePage.as_view(), name="homepage"),
    path("about/", views.AboutPage.as_view(), name="about-page"),
    path("offers", views.OfferListView.as_view(), name="offer-list"),
    path("offers/new", views.OfferCreateView.as_view(), name="offer-create"),
    path("offers/<int:pk>", views.OfferDetailView.as_view(), name="offer-detail"),
    path("offers/<int:pk>/update", views.OfferUpdateView.as_view(), name="offer-update"),
    path("offers/<int:offer_id>/new-step", views.RecruitmentStepCreateView.as_view(), name="step-create"),
    path("offers/steps/<int:pk>", views.RecruitmentStepDetailView.as_view(), name="step-detail"),
    path("offers/steps/<int:pk>/update", views.RecruitmentStepUpdateView.as_view(), name="step-update"),
]
