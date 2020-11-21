# Django
from django.urls import reverse

# Third Party Libraries
import pytest

# Local
from ..factories import ArticleFactory

pytestmark = pytest.mark.django_db


class TestArticleIndex:
    def test_get(self, client):
        ArticleFactory.create_batch(6)
        response = client.get(reverse("articles:index"))
        assert response.status_code == 200
        assert len(response.context["page_obj"].object_list) == 6
