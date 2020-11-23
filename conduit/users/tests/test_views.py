# Django
from django.conf import settings
from django.urls import reverse

# Third Party Libraries
import pytest

# Conduit
from conduit.articles.factories import ArticleFactory

pytestmark = pytest.mark.django_db


class TestUserDetailIndex:
    def test_get(self, client, user):
        ArticleFactory.create_batch(6, author=user)
        response = client.get(reverse("users:detail", args=[user.username]))
        assert response.status_code == 200
        assert len(response.context["articles"]) == 6


class TestUserFavorites:
    def test_get(self, client, user, login_user):
        article = ArticleFactory(author=user)
        login_user.likes.add(article)
        ArticleFactory.create_batch(6, author=user)
        response = client.get(reverse("users:favorites", args=[user.username]))
        assert response.status_code == 200
        assert len(response.context["articles"]) == 1
        assert response.context["articles"][0] == article


class TestUserSettings:
    def test_post(self, client, login_user):
        response = client.post(
            reverse("users:settings"),
            {
                "name": "Test user",
                "bio": "test",
                "avatar": "",
                "email": "tester@gmail.com",
                "password1": "",
                "password2": "",
            },
        )
        assert response.url == settings.HOME_URL
        login_user.refresh_from_db()
        assert login_user.name == "Test user"
        # check password unchanged
        assert login_user.check_password("testpass1")

    def test_post_change_password(self, client, login_user):
        response = client.post(
            reverse("users:settings"),
            {
                "name": "Test user",
                "bio": "test",
                "avatar": "",
                "email": "tester@gmail.com",
                "password1": "testpass2",
                "password2": "testpass2",
            },
        )
        assert response.url == settings.HOME_URL
        login_user.refresh_from_db()
        assert login_user.name == "Test user"
        assert login_user.check_password("testpass2")


class TestUserFollow:
    def test_post(self, client, login_user, user):
        response = client.post(reverse("users:follow", args=[user.id]))
        assert response.url == user.get_absolute_url()
        assert user in login_user.follows.all()

    def test_post_follow_self(self, client, login_user):
        response = client.post(reverse("users:follow", args=[login_user.id]))
        assert response.status_code == 404


class TestUserUnfollow:
    def test_post(self, client, login_user, user):
        login_user.follows.add(user)
        response = client.post(reverse("users:unfollow", args=[user.id]))
        assert response.url == user.get_absolute_url()
        assert user not in login_user.follows.all()

    def test_post_not_following(self, client, login_user, user):
        response = client.post(reverse("users:unfollow", args=[user.id]))
        assert response.status_code == 404
