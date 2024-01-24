from django.urls import path

from setup import views

urlpatterns = [
    path("", views.SetupPageView.as_view(), name="setup-page"),
    path("mailings/", views.SetupMailingView.as_view(), name="setup-mailings"),
    path("complete/", views.SetupCompleteView.as_view(), name="setup-complete"),
]
