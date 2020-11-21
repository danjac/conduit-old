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
