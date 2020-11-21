# Django
from django.urls import path

# Local
from . import views

app_name = "users"

urlpatterns = [
    path("<int:pk>/~follow/", views.follow, name="follow"),
    path("<int:pk>/~unfollow/", views.unfollow, name="unfollow"),
    path("<slug:username>/", views.user_detail, name="detail"),
]
