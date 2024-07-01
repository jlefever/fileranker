from django.urls import path

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sequences/<name>/", views.sequence, name="sequence"),
    path("answer/", views.answer, name="answer"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout")
]
