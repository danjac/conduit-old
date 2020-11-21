from django.urls import path

from . import views

app_name = "articles"

urlpatterns = [
    path("", views.article_index, name="index"),
    path("author/<str:username>/", views.article_author_index, name="author"),
    path("~submit/", views.create_article, name="create"),
    path("<slug:slug>/", views.article_detail, name="detail"),
]
