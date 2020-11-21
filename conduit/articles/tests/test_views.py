# Django
from django.urls import reverse

# Third Party Libraries
import pytest

# Local
from ..factories import ArticleFactory, CommentFactory
from ..models import Article, Comment

pytestmark = pytest.mark.django_db


class TestArticleIndex:
    def test_get(self, client):
        ArticleFactory.create_batch(6)
        response = client.get(reverse("articles:index"))
        assert response.status_code == 200
        assert len(response.context["articles"].object_list) == 6


class TestArticleAuthorIndex:
    def test_get(self, client, user):
        ArticleFactory.create_batch(6, author=user)
        response = client.get(reverse("articles:author", args=[user.username]))
        assert response.status_code == 200
        assert len(response.context["articles"].object_list) == 6


class TestCreateArticle:
    def test_post(self, client, login_user):
        response = client.post(
            reverse("articles:create"),
            {
                "slug": "first-post",
                "title": "first post",
                "body": " first",
                "description": "first",
                "tags": "test",
            },
        )
        assert response.url == reverse("articles:index")
        article = Article.objects.first()
        assert article.author == login_user
        assert list(article.tags.names()) == ["test"]


class TestDeleteComment:
    def test_post_author(self, client, login_user):
        comment = CommentFactory(author=login_user)
        response = client.post(reverse("articles:delete_comment", args=[comment.id]))
        assert response.url == comment.article.get_absolute_url()
        assert not Comment.objects.filter(pk=comment.id).exists()

    def test_post_not_author(self, client, comment, login_user):
        response = client.post(reverse("articles:delete_comment", args=[comment.id]))
        assert response.status_code == 404
        assert Comment.objects.filter(pk=comment.id).exists()


class TestArticleDetail:
    def test_not_found(self, client):
        response = client.get(reverse("articles:detail", args=["test"]))
        assert response.status_code == 404

    def test_with_comments(self, client, article):
        CommentFactory.create_batch(6, article=article)
        response = client.get(reverse("articles:detail", args=[article.slug]))
        assert response.status_code == 200
        assert response.context["article"] == article
        assert len(response.context["comments"].object_list) == 6

    def test_not_authenticated(self, client, article):
        response = client.get(reverse("articles:detail", args=[article.slug]))
        assert response.status_code == 200
        assert response.context["article"] == article
        assert response.context["comment_form"] is None

    def test_authenticated(self, client, article, login_user):
        response = client.get(reverse("articles:detail", args=[article.slug]))
        assert response.status_code == 200
        assert response.context["article"] == article
        assert response.context["comment_form"] is not None

    def test_post_comment(self, client, article, login_user):
        article_url = reverse("articles:detail", args=[article.slug])
        response = client.post(article_url, {"body": "test comment"})
        assert response.url == article_url
        comment = article.comment_set.get()
        assert comment.author == login_user

    def test_post_comment_not_authenticated(self, client, article):
        article_url = reverse("articles:detail", args=[article.slug])
        response = client.post(article_url, {"body": "test comment"})
        assert response.status_code == 200
        assert article.comment_set.count() == 0
