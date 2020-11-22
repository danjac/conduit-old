# Django
from django.urls import path

# Local
from . import views

app_name = "articles"

urlpatterns = [
    path("", views.article_index, name="index"),
    path(
        "comments/<int:comment_id>/~delete", views.delete_comment, name="delete_comment"
    ),
    path("~submit/", views.create_article, name="create"),
    path("<int:article_id>/~edit/", views.edit_article, name="edit"),
    path("<int:article_id>/~delete/", views.delete_article, name="delete"),
    path("<int:article_id>/~like/", views.like_article, name="like"),
    path("<slug:slug>/", views.article_detail, name="detail"),
]
