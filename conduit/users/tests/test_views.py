# Django
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
        assert len(response.context["articles"].object_list) == 6


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
