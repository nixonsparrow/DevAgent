from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomePage.as_view(), name="homepage"),
    path("about/", views.AboutPage.as_view(), name="about-page"),
    path("companies", views.CompanyListView.as_view(), name="company-list"),
    path("companies/new", views.CompanyCreateView.as_view(), name="company-create"),
    path(
        "companies/<int:pk>/update",
        views.CompanyUpdateView.as_view(),
        name="company-update",
    ),
    path("offers", views.OfferListView.as_view(), name="offer-list"),
    path("offers/new", views.OfferCreateView.as_view(), name="offer-create"),
    path("offers/<int:pk>", views.OfferDetailView.as_view(), name="offer-detail"),
    path(
        "offers/<int:pk>/update",
        views.OfferUpdateView.as_view(),
        name="offer-update",
    ),
    path(
        "offers/<int:pk>/send",
        views.OfferSendView.as_view(),
        name="offer-send",
    ),
    path(
        "offers/<int:pk>/sign-contract",
        views.OfferSignContractView.as_view(),
        name="offer-sign-contract",
    ),
    path(
        "offers/<int:pk>/resign",
        views.OfferResignView.as_view(),
        name="offer-resign",
    ),
    path(
        "offers/<int:offer_id>/new-step",
        views.RecruitmentStepCreateView.as_view(),
        name="step-create",
    ),
    path(
        "offers/steps/<int:pk>",
        views.RecruitmentStepDetailView.as_view(),
        name="step-detail",
    ),
    path(
        "offers/steps/<int:pk>/update",
        views.RecruitmentStepUpdateView.as_view(),
        name="step-update",
    ),
    path(
        "offers/steps/<int:pk>/finish",
        views.RecruitmentStepFinishView.as_view(),
        name="step-finish",
    ),
    path(
        "offers/steps/<int:pk>/accept",
        views.RecruitmentStepAcceptView.as_view(),
        name="step-accept",
    ),
    path(
        "offers/steps/<int:pk>/reject",
        views.RecruitmentStepRejectView.as_view(),
        name="step-reject",
    ),
]
