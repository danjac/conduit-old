# Django
from django.urls import path

# Local
from . import views

app_name = "users"

urlpatterns = [
    path("<int:user_id>/~follow/", views.follow, name="follow"),
    path("<int:user_id>/~unfollow/", views.unfollow, name="unfollow"),
    path("settings/", views.user_settings, name="settings"),
    path("<slug:username>/", views.user_detail, name="detail"),
]
