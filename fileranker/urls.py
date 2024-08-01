from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sequences/<name>/", views.sequence, name="sequence"),
    path("answer/", views.answer, name="answer"),
    path("responses.csv", views.download_responses_csv, name="download_responses_csv"),
    path("sequences.csv", views.download_sequences_csv, name="download_sequences_csv"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
