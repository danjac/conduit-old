# Django
from django.conf import settings
from django.urls import reverse

# Third Party Libraries
import pytest

# Local
from ..factories import ArticleFactory, CommentFactory
from ..models import Article, Comment

pytestmark = pytest.mark.django_db


@pytest.fixture
def article_post_data():
    return {
        "slug": "first-post",
        "title": "first post",
        "body": " first",
        "description": "first",
        "tags": "test",
    }


class TestArticleIndex:
    def test_get(self, client):
        ArticleFactory.create_batch(6)
        response = client.get(reverse("articles:index"))
        assert response.status_code == 200
        assert len(response.context["articles"].object_list) == 6

    def test_get_with_selected_tag(self, client):
        article = ArticleFactory()
        article.tags.add("red", "green", "blue")
        ArticleFactory.create_batch(5)
        response = client.get(reverse("articles:index"), {"tag": "green"})
        assert response.status_code == 200
        assert len(response.context["articles"].object_list) == 1
        assert response.context["articles"].object_list[0] == article


class TestCreateArticle:
    def test_post(self, client, login_user, article_post_data):
        response = client.post(reverse("articles:create"), article_post_data)
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


class TestLikeArticle:
    def test_like_article(self, client, article, login_user):
        response = client.post(reverse("articles:like", args=[article.id]))
        assert response.url == article.get_absolute_url()
        assert article in login_user.likes.all()

    def test_unlike_article(self, client, article, login_user):
        login_user.likes.add(article)
        response = client.post(reverse("articles:like", args=[article.id]))
        assert response.url == article.get_absolute_url()
        assert article not in login_user.likes.all()

    def test_like_own_article(self, client, login_user):
        article = ArticleFactory(author=login_user)
        response = client.post(reverse("articles:like", args=[article.id]))
        assert response.status_code == 404
        assert article not in login_user.likes.all()

    def test_return_html_fragment(self, client, article, login_user):
        response = client.post(
            reverse("articles:like", args=[article.id]), HTTP_X_REQUEST_FRAGMENT=True
        )
        assert response.status_code == 200
        assert article in login_user.likes.all()


class TestEditArticle:
    def test_post(self, client, login_user, article_post_data):
        article = ArticleFactory(author=login_user)
        response = client.post(
            reverse("articles:edit", args=[article.id]), article_post_data
        )
        article.refresh_from_db()

        assert response.url == article.get_absolute_url()
        assert article.title == "first post"

    def test_post_not_author(self, client, article, login_user, article_post_data):
        response = client.post(
            reverse("articles:edit", args=[article.id]), article_post_data
        )
        assert response.status_code == 404


class TestDeleteArticle:
    def test_post(self, client, login_user):
        article = ArticleFactory(author=login_user)
        response = client.post(reverse("articles:delete", args=[article.id]),)

        assert response.url == settings.HOME_URL
        assert Article.objects.count() == 0

    def test_post_not_author(self, client, article, login_user):
        response = client.post(reverse("articles:delete", args=[article.id]),)
        assert response.status_code == 404


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
